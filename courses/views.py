from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (Learner, LearnerEnrollment, MentorAssignment, LearnerSubscribePlan, MentorGroupSessionOccurrence, 
                    StepProgress, EducationalStep, Task, TaskEvaluation, TaskSubmission, SocialPost, SocialMedia)
from core.models import CustomUser
from django.db.models import Max, Count, Q, Prefetch, Sum, Exists, OuterRef
from django.urls import reverse_lazy
from .forms import ProfileForm
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

# Learner side Views
class LearnerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/learner_dash.html')
    

class StepListView(LoginRequiredMixin, ListView):
    template_name = "courses/step_list.html"
    context_object_name = "steps"

    def get_queryset(self):
        self.enrollment = get_object_or_404(
            LearnerEnrollment.objects.select_related("learner", "learning_path"),
            id=self.kwargs["pk"],
            learner__user=self.request.user,
        )
        qs = EducationalStep.objects.with_progress(self.enrollment).ordered()

        for s in qs:
            s.percentile = s.get_percentile()
            s.can_start = s.can_start(self.enrollment)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["enrollment"] = self.enrollment
        return ctx
    

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "courses/task_list.html"

    def get_step_progress(self, step_id, learner):
        return (
            StepProgress.objects.filter(
                educational_step_id=step_id,
                mentor_assignment__enrollment__learner=learner,
            )
            .annotate(
                total_extension_days=Sum(
                    "extensions__extended_by_days",
                    filter=Q(extensions__approved_by_mentor=True),
                    default=0,
                )
            )
            .select_related("educational_step")
            .first()
        )

    def get_base_queryset(self, step_id, step_progress):
        tasks = Task.objects.filter(step_id=step_id).select_related("step").order_by("order_in_step")
        if not step_progress:
            return tasks

        submissions_qs = (
            TaskSubmission.objects.filter(step_progress=step_progress)
            .prefetch_related(Prefetch("evaluations", queryset=TaskEvaluation.objects.select_related("mentor")))
        )
        evaluated_subq = TaskEvaluation.objects.filter(
            submission__task=OuterRef("pk"),
            submission__step_progress=step_progress,
            evaluated_at__isnull=False,
        )

        return tasks.prefetch_related(Prefetch("submissions", queryset=submissions_qs)).annotate(
            latest_submission=Max(
                "submissions__submitted_at", filter=Q(submissions__step_progress=step_progress)
            ),
            is_completed=Count(
                "submissions__evaluations",
                filter=Q(
                    submissions__step_progress=step_progress,
                    submissions__evaluations__evaluated_at__isnull=False,
                ),
                distinct=True,
            ),
            is_evaluated=Exists(evaluated_subq),
        )

    def get_queryset(self):
        step_id = self.kwargs["step_id"]
        learner = getattr(self.request.user, "learner_profile", None)
        if not learner:
            return Task.objects.none()

        self.step_progress = self.get_step_progress(step_id, learner)
        tasks = self.get_base_queryset(step_id, self.step_progress)

        # Filters
        search, status = self.request.GET.get("search", ""), self.request.GET.get("status", "all")
        if search:
            tasks = tasks.filter(title__icontains=search)
        if status == "evaluated":
            tasks = tasks.filter(is_completed=True)
        elif status == "todo":
            tasks = tasks.filter(Q(is_completed=False) | Q(is_completed__isnull=True))

        return tasks

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        step = get_object_or_404(
            EducationalStep.objects.select_related("learning_path").prefetch_related("resources"),
            pk=self.kwargs["step_id"],
        )
        tasks = ctx["tasks"]
        total = len(tasks)
        completed = sum(1 for t in tasks if getattr(t, "is_completed", 0))

        due_date = None
        step_progress_id = None
        if getattr(self, "step_progress", None):
            sp = self.step_progress
            step_progress_id = sp.id
            due_date = sp.initial_promise_date + timedelta(
                days=sp.initial_promise_days + (sp.total_extension_days or 0)
            )

        ctx.update({
            "step": step,
            "learning_path": step.learning_path,
            "resources": step.resources.all(),
            "due_date": due_date,
            "progress_percent": round((completed / total) * 100) if total else 0,
            "completed_count": completed,
            "remaining_count": total - completed,
            "total": total,
            "step_progress_id": step_progress_id,
        })
        return ctx

    def get_template_names(self):
        return ["courses/partials/task_list_partial.html"] if self.request.headers.get("HX-Request") \
               else ["courses/task_list.html"]
    

class TaskSubmissionView(View):
    template_name = "courses/task_submission.html"

    def get(self, request, step_progress_id, task_id):
        step_progress = get_object_or_404(StepProgress, pk=step_progress_id)
        task = get_object_or_404(Task, pk=task_id, step=step_progress.educational_step)

        learner = getattr(request.user, "learner_profile", None)
        if not learner or step_progress.mentor_assignment.enrollment.learner != learner:
            messages.error(request, "You are not allowed to access this task.")
            return redirect("task_list")

        social_medias = SocialMedia.objects.all()
        social_posts = SocialPost.objects.filter(step_progress=step_progress)

        return render(request, self.template_name, {
            "step_progress": step_progress,
            "task": task,
            "social_medias": social_medias,
            "social_posts": social_posts,
        })

    def post(self, request, step_progress_id, task_id):
        step_progress = get_object_or_404(StepProgress, pk=step_progress_id)
        task = get_object_or_404(Task, pk=task_id, step=step_progress.educational_step)
        learner = getattr(request.user, "learner_profile", None)

        if not learner or step_progress.mentor_assignment.enrollment.learner != learner:
            messages.error(request, "Unauthorized submission attempt.")
            return redirect("task_list")

        errors = []

        # Handle TaskSubmission
        artifact_url = request.POST.get("link1", "").strip()
        report_video_link = request.POST.get("link2", "").strip()
        repository = request.POST.get("link3", "").strip()
        comment = request.POST.get("comments", "").strip()
        file = request.FILES.get("file-upload1")
        report_video_file = request.FILES.get("file-upload2")

        if not any([artifact_url, report_video_link, repository, file, report_video_file]):
            errors.append("Please provide at least one link or file for submission.")

        if not errors:
            TaskSubmission.objects.create(
                task=task,
                step_progress=step_progress,
                artifact_url=artifact_url,
                report_video_link=report_video_link,
                repository=repository,
                file=file,
                report_video_file=report_video_file,
                comment=comment
            )
            messages.success(request, "Task submitted successfully.")

        # Handle SocialPost
        platform_id = request.POST.get("platform1")
        post_link = request.POST.get("post_link1")
        description = request.POST.get("description1")
        post_date = request.POST.get("post_date1")

        if platform_id and post_link:
            platform = get_object_or_404(SocialMedia, pk=platform_id)
            existing_post = SocialPost.objects.filter(
                learner=learner, step_progress=step_progress, platform=platform
            ).first()
            if existing_post:
                errors.append(f"You already added a post for {platform}.")
            else:
                SocialPost.objects.create(
                    learner=learner,
                    step_progress=step_progress,
                    platform=platform,
                    url=post_link,
                    description=description,
                    posted_at=post_date or timezone.now()
                )
                messages.success(request, f"Social post for {platform} added.")

        if errors:
            for err in errors:
                messages.error(request, err)

        return redirect(request.path)
    

class ProfileOverviewView(LoginRequiredMixin, View):
    def get(self, request):
        learner = get_object_or_404(Learner, user=request.user)
        enrollments = (
            learner.enrollments
            .select_related("learning_path")
            .annotate(
                total=Count("learning_path__steps", distinct=True),
                done=Count(
                    "learning_path__steps__step_progresses",
                    filter=Q(learning_path__steps__step_progresses__task_completion_date__isnull=False),
                    distinct=True
                ),
                last_done=Max("learning_path__steps__step_progresses__task_completion_date")
            )
        )

        ongoing, completed = [], []
        for e in enrollments:
            print(e, e.done)
            p = round((e.done / e.total * 100), 1) if e.total else 0
            data = {"path": e.learning_path, "status": e.status, "progress": p, "completed_date": e.last_done or e.unenroll_date}
            (completed if e.status == "graduated" else ongoing).append(data)

        return render(request, "courses/profile_overview.html", {
            "learner": learner,
            "ongoing_paths": ongoing,
            "completed_paths": completed,
        })
    

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = "courses/edit_profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("learner-dashboard")

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _("Your profile has been updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("There was an error updating your profile. Please check the form."))
        return super().form_invalid(form)
    

class LearningPathView(LoginRequiredMixin, DetailView):
    model = LearnerEnrollment
    template_name = "courses/learning_path.html"
    context_object_name = "enrollment"

    def get_object(self, queryset=None):
        learner = get_object_or_404(Learner, user=self.request.user)
        return get_object_or_404(
            LearnerEnrollment.objects
            .select_related("learning_path")
            .prefetch_related(
                Prefetch("mentor_assignments",
                         queryset=MentorAssignment.objects.select_related("mentor__user")),
                Prefetch("subscriptions",
                         queryset=LearnerSubscribePlan.objects
                         .select_related("subscription_plan")
                         .order_by("-end_datetime"))
            ),
            pk=self.kwargs["pk"],
            learner=learner
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        e = ctx["enrollment"]
        now = timezone.now()

        ma = e.mentor_assignments.first()
        sub = e.subscriptions.first()
        

        ctx.update({
            "mentor": ma.mentor.user.get_full_name() if ma else "-",
            "mentor_assignment": ma,
            "plan": sub.subscription_plan.name if sub else "-",
            "plan_expires": sub.end_datetime if sub else None,
            "days_remaining": max((sub.end_datetime - now).days, 0) if sub else None,
            "upcoming_sessions": MentorGroupSessionOccurrence.objects.filter(
                mentor_group_session__mentor=ma.mentor if ma else None,
                occurence_datetime__gte=now,
                mentor_group_session__learning_path=e.learning_path
            )[:3],
            "past_sessions": MentorGroupSessionOccurrence.objects.filter(
                mentor_group_session__mentor=ma.mentor if ma else None,
                occurence_datetime__lt=now,
                mentor_group_session__learning_path=e.learning_path
            )[:3],
        })
        return ctx
    

class SubscriptionPlansView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/subscription/plans.html')


class StepPromiseView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/step_promise.html')
    

class TaskFeedbackView(LoginRequiredMixin, View):
    template_name = "courses/task_feedback.html"

    def get(self, request, step_progress_id, task_id):
        learner = getattr(request.user, "learner_profile", None)
        if not learner:
            messages.error(request, "You must be logged in as a learner.")
            return redirect("dashboard")

        step_progress = get_object_or_404(StepProgress, pk=step_progress_id)
        task = get_object_or_404(Task, pk=task_id, step=step_progress.educational_step)

        # ✅ Permission check
        if step_progress.mentor_assignment.enrollment.learner != learner:
            messages.error(request, "You are not allowed to view feedback for this task.")
            return redirect("task-list")

        # ✅ Get latest submission for this learner and task
        submission = (
            TaskSubmission.objects.filter(task=task, step_progress=step_progress)
            .order_by("-submitted_at")
            .first()
        )

        if not submission:
            messages.error(request, "You haven’t submitted this task yet.")
            return redirect("task-list", step_progress.educational_step.id)

        # ✅ Get evaluation if exists
        evaluation = (
            TaskEvaluation.objects
            .select_related("mentor")
            .filter(submission=submission)
            .order_by("-evaluated_at")
            .first()
        )

        if not evaluation:
            messages.error(request, "This task has not been evaluated yet.")
            return redirect("task-list", step_progress.educational_step.id)

        context = {
            "task": task,
            "step_progress": step_progress,
            "submission": submission,
            "evaluation": evaluation,
            "mentor": evaluation.mentor,
        }

        return render(request, self.template_name, context)
    

# Mentor side Views
class MnetorFeedbackListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/mentor_feedback_list.html')
    

class MnetorFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/mentor_feedback.html')
    

class AttendaceHubView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/attendance_hub.html')
    

class LearnersListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/learners_list.html')
    

class SessionListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/session_list.html')
    

class GroupSessionAttendanceView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/group_session_attendance.html')


class PrivateSessionAttendanceView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/private_session_attendance.html')


class PrivateSessionManageView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/private_session_manage.html')


class LearnerAttendanceHistoryView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/learner_attendance_history.html')
    

class GroupAttendanceHistoryView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/group_attend_history.html')