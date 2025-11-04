from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Learner, Learner
from core.models import CustomUser
from django.db.models import Max, Count, Q
from django.urls import reverse_lazy
from .forms import ProfileForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# Learner side Views
class LearnerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/learner_dash.html')
    
class StepListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/step_list.html')
    
class TaskListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/task_list.html')
    
class TaskSubmissionView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/task_submission.html')
    
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
    
class LearningPathView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/learning_path.html')
    
class SubscriptionPlansView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/subscription/plans.html')

class StepPromiseView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/step_promise.html')
    
class TaskFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/task_feedback.html')
    
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