# courses/admin.py  – Django 5.2 • Unfold • import-export
from __future__ import annotations

from datetime import date as _d, datetime as _dt, time as _t, timezone as _tz
from decimal import Decimal
from typing import List, Type

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db import models
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncDate, TruncDay
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, path
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect

from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.formats.base_formats import CSV, JSON, XLSX, Format

from unfold.enums import ActionVariant
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget, ArrayWidget
from unfold.contrib.import_export.forms import ImportForm, ExportForm
from unfold.decorators import display, action

from pages.templatetags.custom_translation_tags import translate_number
from pages.templatetags.persian_calendar_convertor import (
    convert_to_persian_calendar,
    format_persian_datetime,
)

from . import models as m
from core.notify import send_subscription_expired_sms


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def _jalali(val):
    if isinstance(val, _d) and not isinstance(val, _dt):
        val = _dt.combine(val, _t.min, tzinfo=_tz.utc)
    return format_persian_datetime(convert_to_persian_calendar(val))


def jalali_display(attr="created_at", *, label=None):
    label = label or attr.replace("_", " ").title()

    @display(description=label)
    def _fn(self, obj):
        v = getattr(obj, attr, None)
        return "-" if not v else format_html("<b dir='rtl'>{}</b>", translate_number(_jalali(v)))
    _fn.__name__ = f"{attr}_jalali"
    return _fn


def bool_badge(attr, *, true="Yes", false="No", t_color="success", f_color="danger", desc="Status"):
    @display(description=desc, label={True: t_color, False: f_color})
    def _fn(self, obj):
        val = getattr(obj, attr)
        return val, true if val else false
    _fn.__name__ = f"{attr}_badge"
    return _fn


def choice_badge(attr, *, mapping: dict[str, tuple[str, str]], desc="Status"):
    label_map = {k: c for k, (_, c) in mapping.items()}

    @display(description=desc, label=label_map)
    def _fn(self, obj):
        raw = getattr(obj, attr)
        text, _ = mapping.get(raw, (raw, "info"))
        return raw, text
    _fn.__name__ = f"{attr}_badge"
    return _fn


def badge(text: str, variant: str) -> str:
    # Unfold badge variants: primary, success, info, warning, danger, default
    return f'<span class="badge badge--{variant}">{text}</span>'


def _format_shamsi(dt) -> str:
    if hasattr(dt, "strftime"):
        return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M")
    return "—"


# ──────────────────────────────────────────────────────────────
# Import/Export resources (Subscriptions)
# ──────────────────────────────────────────────────────────────
class LearnerSubscribePlanResource(resources.ModelResource):
    learner = fields.Field(column_name="learner_full_name")
    plan = fields.Field(column_name="plan_name")
    start = fields.Field(attribute="start_datetime", column_name="start_datetime")
    end = fields.Field(attribute="end_datetime", column_name="end_datetime")
    discount = fields.Field(attribute="discount", column_name="discount_percent")
    final_cost = fields.Field(attribute="final_cost", column_name="final_cost_toman")
    status = fields.Field(attribute="status", column_name="status")

    class Meta:
        model = m.LearnerSubscribePlan
        fields = ("learner", "plan", "start", "end", "discount", "final_cost", "status")
        export_order = ("learner", "plan", "start", "end", "discount", "final_cost", "status")

    def dehydrate_learner(self, obj: m.LearnerSubscribePlan) -> str:
        try:
            u = obj.learner_enrollment.learner.user
            return f"{u.first_name} {u.last_name}".strip() or u.email
        except Exception:
            return str(obj.learner_enrollment_id)

    def dehydrate_plan(self, obj: m.LearnerSubscribePlan) -> str:
        return getattr(obj.subscription_plan, "name", str(obj.subscription_plan_id))


class PDF(Format):
    def get_title(self): return "pdf"
    def get_extension(self): return "pdf"
    def get_content_type(self): return "application/pdf"
    def export_data(self, dataset, **kwargs):
        html = render_to_string(
            "admin/courses/learner_subscribe_plan/export_pdf.html",
            {"dataset": dataset, "generated_at": timezone.now()},
        )
        try:
            if getattr(settings, "USE_WEASYPRINT", False):
                from weasyprint import HTML
                return HTML(string=html).write_pdf()
        except Exception:
            pass
        return html.encode("utf-8")


# ──────────────────────────────────────────────────────────────
# Base Admin
# ──────────────────────────────────────────────────────────────
FORM_OVERRIDES = {
    models.TextField: {"widget": WysiwygWidget},
    models.JSONField: {"widget": ArrayWidget},
    ArrayField: {"widget": ArrayWidget},
}


class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    show_full_result_count = False
    formfield_overrides = FORM_OVERRIDES


class HistoryBaseAdmin(SimpleHistoryAdmin, BaseAdmin):
    pass


# ──────────────────────────────────────────────────────────────
# CURRICULUM
# ──────────────────────────────────────────────────────────────
class ResourceInline(TabularInline):
    model = m.Resources
    extra = 0
    fields = ("title", "type", "address")
    formfield_overrides = FORM_OVERRIDES


class TaskInline(TabularInline):
    model = m.Task
    extra = 0
    fields = ("title", "order_in_step", "is_required")
    formfield_overrides = FORM_OVERRIDES


class EducationalStepInline(TabularInline):
    model = m.EducationalStep
    extra = 0
    show_change_link = True
    ordering = ("sequence_no",)
    fields = ("sequence_no", "title", "expected_duration_days", "is_mandatory")


@admin.register(m.LearningPath)
class LearningPathAdmin(BaseAdmin):
    created_j = jalali_display()
    active_badge = bool_badge("is_active", true="Active", false="Inactive")

    list_display = ("name", "active_badge", "created_j")
    list_filter = ("is_active",)
    search_fields = ("name",)

    # Open the progress analytics dashboard (separate from financial analytics)
    actions_list = ["go_progress_analytics"]

    @action(description=_("Progress Analytics"), icon="timeline", variant=ActionVariant.PRIMARY)
    def go_progress_analytics(self, request: HttpRequest, queryset=None):
        return redirect(reverse("admin:courses_learningpath_progress_analytics"))

    # ---- URLs for the progress analytics
    def get_urls(self):
        return [
            path(
                "progress-analytics/",
                self.admin_site.admin_view(self.progress_analytics_view),
                name="courses_learningpath_progress_analytics",
            ),
            path(
                "progress-analytics/data/",
                self.admin_site.admin_view(self.progress_analytics_data),
                name="courses_learningpath_progress_analytics_data",
            ),
            path(
                "progress-analytics/choices/",
                self.admin_site.admin_view(self.progress_analytics_choices),
                name="courses_learningpath_progress_analytics_choices",
            ),
            path(
                "progress-analytics/search/mentors/",
                self.admin_site.admin_view(self.progress_analytics_search_mentors),
                name="courses_learningpath_progress_analytics_search_mentors",
            ),
            path(
                "progress-analytics/search/learners/",
                self.admin_site.admin_view(self.progress_analytics_search_learners),
                name="courses_learningpath_progress_analytics_search_learners",
            ),
        ] + super().get_urls()

    def progress_analytics_view(self, request):
        ctx = dict(self.admin_site.each_context(request), title=_("Progress Analytics"))
        return TemplateResponse(
            request,
            "admin/courses/learningpath/progress_analytics.html",
            ctx,
        )

    # --- initial choices for dropdowns (used once on page load)
    def progress_analytics_choices(self, request: HttpRequest):
        """
        Initial lists and re-population for LP, mentors, learners.
        Accepts optional: lp, mentor, learner
        """
        lp_id = request.GET.get("lp")
        mentor_id = request.GET.get("mentor")
        learner_id = request.GET.get("learner")

        # Learning Paths
        lps = list(m.LearningPath.objects.order_by("name").values("id", "name"))

        # Mentors (reverse name is Mentor.assignments)
        mentors_qs = m.Mentor.objects.select_related("user")
        if lp_id:
            mentors_qs = mentors_qs.filter(assignments__enrollment__learning_path_id=lp_id)
        if learner_id:
            mentors_qs = mentors_qs.filter(assignments__enrollment__learner_id=learner_id)
        mentors_qs = mentors_qs.order_by("user__first_name", "user__last_name").distinct()[:50]
        mentors = [
            {"id": i.id, "name": (f"{i.user.first_name} {i.user.last_name}".strip() or i.user.email)}
            for i in mentors_qs
        ]

        # Learners (reverse name is Learner.enrollments)
        learners_qs = m.Learner.objects.select_related("user")
        if lp_id:
            learners_qs = learners_qs.filter(enrollments__learning_path_id=lp_id)
        if mentor_id:
            learners_qs = learners_qs.filter(enrollments__mentor_assignments__mentor_id=mentor_id)
        learners_qs = learners_qs.order_by("user__first_name", "user__last_name").distinct()[:50]
        learners = [
            {"id": i.id, "name": (f"{i.user.first_name} {i.user.last_name}".strip() or i.user.email)}
            for i in learners_qs
        ]

        return JsonResponse({"learning_paths": lps, "mentors": mentors, "learners": learners})

    # --- instant-search: mentors
    def progress_analytics_search_mentors(self, request: HttpRequest):
        """Search mentors, filtered by lp and (optionally) learner."""
        q = (request.GET.get("q") or "").strip()
        lp_id = request.GET.get("lp")
        learner_id = request.GET.get("learner")

        qs = m.Mentor.objects.select_related("user")
        if lp_id:
            qs = qs.filter(assignments__enrollment__learning_path_id=lp_id)
        if learner_id:
            qs = qs.filter(assignments__enrollment__learner_id=learner_id)
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__email__icontains=q)
            )

        qs = qs.order_by("user__first_name", "user__last_name").distinct()[:20]
        data = [{"id": o.id, "name": (f"{o.user.first_name} {o.user.last_name}".strip() or o.user.email)} for o in qs]
        return JsonResponse({"results": data})

    # --- instant-search: learners
    def progress_analytics_search_learners(self, request: HttpRequest):
        """Search learners, filtered by lp and (optionally) mentor."""
        q = (request.GET.get("q") or "").strip()
        lp_id = request.GET.get("lp")
        mentor_id = request.GET.get("mentor")

        qs = m.Learner.objects.select_related("user")
        if lp_id:
            qs = qs.filter(enrollments__learning_path_id=lp_id)
        if mentor_id:
            qs = qs.filter(enrollments__mentor_assignments__mentor_id=mentor_id)
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__email__icontains=q)
            )

        qs = qs.order_by("user__first_name", "user__last_name").distinct()[:20]
        data = [{"id": o.id, "name": (f"{o.user.first_name} {o.user.last_name}".strip() or o.user.email)} for o in qs]
        return JsonResponse({"results": data})

    # --- Data endpoint for charts
    def progress_analytics_data(self, request: HttpRequest):
        """
        JSON API for progress analytics.
        chart: step_funnel | avg_score | completions_over_time | learner_progress
        filters: lp (required), mentor, learner, year, month
        """
        chart = (request.GET.get("chart") or "step_funnel").strip()
        lp_id = request.GET.get("lp")
        mentor_id = request.GET.get("mentor")
        learner_id = request.GET.get("learner")
        year = request.GET.get("year")
        month = request.GET.get("month")

        if not lp_id:
            return JsonResponse({"error": "lp required"}, status=400)

        # base StepProgress filter (ensure we never defer fields we traverse)
        sp_base = m.StepProgress.objects.select_related(
            "educational_step",
            "mentor_assignment",
            "mentor_assignment__enrollment",
            "mentor_assignment__enrollment__learner",
            "mentor_assignment__enrollment__learning_path",
        ).filter(
            educational_step__learning_path_id=lp_id
        )
        if mentor_id:
            sp_base = sp_base.filter(mentor_assignment__mentor_id=mentor_id)
        if learner_id:
            sp_base = sp_base.filter(mentor_assignment__enrollment__learner_id=learner_id)

        # STEP FUNNEL: per step => completed vs total
        if chart == "step_funnel":
            steps = list(
                m.EducationalStep.objects.filter(learning_path_id=lp_id)
                .order_by("sequence_no")
                .values("id", "title")
            )
            step_ids = [s["id"] for s in steps]
            total_by_step = dict(
                sp_base.values("educational_step_id").annotate(c=Count("id")).values_list("educational_step_id", "c")
            )
            completed_by_step = dict(
                sp_base.filter(task_completion_date__isnull=False)
                      .values("educational_step_id")
                      .annotate(c=Count("id"))
                      .values_list("educational_step_id", "c")
            )
            labels = [s["title"] for s in steps]
            total = [int(total_by_step.get(sid, 0)) for sid in step_ids]
            completed = [int(completed_by_step.get(sid, 0)) for sid in step_ids]
            return JsonResponse({"chart": chart, "labels": labels, "total": total, "completed": completed})

        # AVG SCORE: average TaskEvaluation.score per step
        if chart == "avg_score":
            evals = m.TaskEvaluation.objects.select_related(
                "submission",
                "submission__step_progress",
                "submission__step_progress__educational_step",
                "submission__step_progress__mentor_assignment__enrollment__learner",
                "submission__step_progress__mentor_assignment__enrollment__learning_path",
            ).filter(
                submission__step_progress__educational_step__learning_path_id=lp_id
            )
            if mentor_id:
                evals = evals.filter(submission__step_progress__mentor_assignment__mentor_id=mentor_id)
            if learner_id:
                evals = evals.filter(submission__step_progress__mentor_assignment__enrollment__learner_id=learner_id)

            rows = (
                evals.values("submission__step_progress__educational_step__title",
                             "submission__step_progress__educational_step__sequence_no")
                     .annotate(score=Avg("score"))
                     .order_by("submission__step_progress__educational_step__sequence_no")
            )
            labels = [r["submission__step_progress__educational_step__title"] for r in rows]
            scores = [round(r["score"] or 0, 2) for r in rows]
            return JsonResponse({"chart": chart, "labels": labels, "scores": scores})

        # COMPLETIONS OVER TIME: use StepProgress.task_completion_date
        if chart == "completions_over_time":
            sps = sp_base.filter(task_completion_date__isnull=False)
            if year:
                sps = sps.filter(task_completion_date__year=int(year))
            if month:
                sps = sps.filter(task_completion_date__month=int(month))

            rows = (
                sps.annotate(d=TruncDay("task_completion_date"))
                   .values("d")
                   .order_by("d")
                   .annotate(c=Count("id"))
            )
            labels = [r["d"].date().isoformat() for r in rows]
            daily = [int(r["c"] or 0) for r in rows]
            cum = []
            t = 0
            for v in daily:
                t += v
                cum.append(t)
            return JsonResponse({"chart": chart, "labels": labels, "daily": daily, "cumulative": cum})

        # LEARNER PROGRESS (requires learner)
        if chart == "learner_progress":
            if not learner_id:
                return JsonResponse({"chart": chart, "labels": [], "promised_days": [], "actual_days": []})
            sps = sp_base.filter(mentor_assignment__enrollment__learner_id=learner_id) \
                         .order_by("educational_step__sequence_no")
            labels, promised, actual = [], [], []
            for sp in sps:
                labels.append(sp.educational_step.title)
                # promised days: prefer explicit value; otherwise fall back to step.expected_duration_days
                p_days = int(getattr(sp, "initial_promise_days", 0) or 0)
                if p_days <= 0:
                    p_days = int(getattr(sp.educational_step, "expected_duration_days", 0) or 0)
                promised.append(max(p_days, 0))

                # actual days: completion_date - initial_promise_date (both datetimes)
                a_days = 0
                if sp.task_completion_date:
                    try:
                        a_days = (sp.task_completion_date.date() - sp.initial_promise_date.date()).days
                        a_days = max(a_days, 0)
                    except Exception:
                        a_days = 0
                actual.append(a_days)
            return JsonResponse({"chart": chart, "labels": labels, "promised_days": promised, "actual_days": actual})

        return JsonResponse({"chart": chart, "labels": [], "data": []})


@admin.register(m.EducationalStep)
class EducationalStepAdmin(BaseAdmin):
    created_j = jalali_display()
    mandatory_badge = bool_badge(
        "is_mandatory", true="Mandatory", false="Optional", t_color="danger", f_color="info"
    )
    list_display = ("__str__", "expected_duration_days", "mandatory_badge", "created_j")
    list_filter = ("learning_path", "is_mandatory")
    autocomplete_fields = ("learning_path",)
    inlines = (TaskInline, ResourceInline)
    search_fields = ("title", "description")


@admin.register(m.Resources)
class ResourceAdmin(BaseAdmin):
    created_j = jalali_display()
    list_display = ("title", "type", "step", "created_j")
    list_filter = ("type", "step__learning_path")
    autocomplete_fields = ("step",)
    search_fields = ("title", "address")


# ──────────────────────────────────────────────────────────────
# PEOPLE
# ──────────────────────────────────────────────────────────────
@admin.register(m.Specialty)
class SpecialtyAdmin(BaseAdmin):
    active_badge = bool_badge("is_active")
    list_display = ("name", "code", "active_badge")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(m.Mentor)
class MentorAdmin(BaseAdmin):
    hire_j = jalali_display("hire_date", label="Hire date")
    status_badge = bool_badge("status", true="Active", false="Inactive")

    @display(header=True, description=_("Mentor"))
    def heading(self, obj):
        initials = "".join([obj.user.first_name[:1], obj.user.last_name[:1]])
        return [obj.user.get_full_name(), obj.user.email, initials]

    list_display = ("heading", "hire_j", "status_badge")
    list_filter = ("status", "specialties")
    autocomplete_fields = ("user", "specialties")
    search_fields = ("user__first_name", "user__last_name", "user__email")


@admin.register(m.Learner)
class LearnerAdmin(BaseAdmin):
    list_select_related = ['user']
    status_badge = bool_badge("status", true="Active", false="Inactive")
    list_display = ("heading", "status_badge")
    search_fields = ("user__first_name", "user__last_name", "user__email")
    autocomplete_fields = ("user",)

    @display(header=True, description=_("Fullname"), image=True)
    def heading(self, obj):
        initials = "".join([obj.user.first_name[:1], obj.user.last_name[:1]])
        return [obj.user.get_full_name(), obj.user.phone_number, initials]

# ──────────────────────────────────────────────────────────────
# ENROLMENT & MENTORING
# ──────────────────────────────────────────────────────────────
class MentorAssignmentInline(TabularInline):
    model = m.MentorAssignment
    extra = 0
    autocomplete_fields = ("mentor",)
    fields = (
        "mentor",
        "start_date",
        "end_date",
        "reason_for_change",
        "code_review_session_day",
        "code_review_session_time",
    )
    conditional_fields = {"reason_for_change": "end_date != ''"}


@admin.register(m.LearnerEnrollment)
class LearnerEnrollmentAdmin(BaseAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "graduated": ("Graduated", "primary"),
            "dropped": ("Dropped", "danger"),
            "reserved": ("Reserved", "warning"),
        },
    )
    list_display = ("learner", "learning_path", "status_badge", "enroll_date", "unenroll_date")
    list_filter = ("status", "learning_path")
    autocomplete_fields = ("learner", "learning_path")
    search_fields = ("learner__user__email", "learning_path__name")


@admin.register(m.MentorAssignment)
class MentorAssignmentAdmin(BaseAdmin):
    list_display = ("enrollment", "mentor", "start_date", "end_date")
    autocomplete_fields = ("enrollment", "mentor")
    list_filter = ("mentor",)
    search_fields = (
        "mentor__user__first_name",
        "mentor__user__last_name",
        "mentor__user__email",
        "enrollment__learner__user__email",
    )


# ──────────────────────────────────────────────────────────────
# PROGRESS & TASKS
# ──────────────────────────────────────────────────────────────
@admin.register(m.StepExtension)
class StepExtension(BaseAdmin):
    list_display = (
        "step_progress",
        "extended_by_days",
        "requested_at",
        "approved_by_mentor",
        "reason",
    )
    list_select_related = ("step_progress",)


class StepExtensionInline(TabularInline):
    model = m.StepExtension
    extra = 0
    fields = ("extended_by_days", "requested_at", "approved_by_mentor", "reason")


class TaskSubmissionInline(TabularInline):
    model = m.TaskSubmission
    extra = 0
    readonly_fields = ("submitted_at",)
    fields = ("task", "step_progress", "submitted_at")
    autocomplete_fields = ("task", "step_progress")


@admin.register(m.SessionType)
class SessionTypeAdmin(BaseAdmin):
    list_display = ("code", "name_fa", "duration_minutes", "max_participants")
    search_fields = ("code", "name_fa")


@admin.register(m.StepProgressSession)
class StepProgressSessionAdmin(BaseAdmin):
    list_display = (
        "step_progress",
        "session_type",
        "datetime",
        "present",
        "description",
        "recorded_meet_link",
    )
    autocomplete_fields = ("step_progress", "session_type")
    search_fields = ("step_progress", "session_type")


@admin.register(m.StepProgress)
class StepProgressAdmin(BaseAdmin):
    skipped_badge = bool_badge("skipped", true="Skipped", false="On track")
    list_display = ("mentor_assignment", "educational_step", "skipped_badge")
    autocomplete_fields = ("mentor_assignment", "educational_step")
    list_filter = ("skipped", "educational_step__learning_path")
    inlines = (StepExtensionInline,)
    conditional_fields = {"initial_promise_days": "skipped == false"}
    search_fields = (
        "mentor_assignment__mentor__user__first_name",
        "mentor_assignment__mentor__user__last_name",
        "educational_step__title",
    )


@admin.register(m.Task)
class TaskAdmin(BaseAdmin):
    req_badge = bool_badge(
        "is_required", true="Required", false="Optional", t_color="danger", f_color="info"
    )
    list_display = ("title", "step", "order_in_step", "req_badge")
    list_filter = ("is_required", "step__learning_path")
    autocomplete_fields = ("step",)
    search_fields = ("title", "step__title")


@admin.register(m.TaskSubmission)
class TaskSubmissionAdmin(BaseAdmin):
    submitted_j = jalali_display("submitted_at", label="Submitted")
    list_display = ("task", "step_progress", "submitted_j")
    autocomplete_fields = ("task", "step_progress")
    readonly_fields = ("submitted_at",)
    search_fields = ("task__title", "step_progress__educational_step__title")


@admin.register(m.TaskEvaluation)
class TaskEvaluationAdmin(BaseAdmin):
    submitted_j = jalali_display("evaluated_at", label="Evaluated")
    list_display = ("submission", "mentor", "score", "feedback")
    autocomplete_fields = ("mentor", "submission")
    search_fields = ("submission__task__title", "mentor__user")


# ──────────────────────────────────────────────────────────────
# SOCIAL / POSTS
# ──────────────────────────────────────────────────────────────
@admin.register(m.SocialMedia)
class SocialMediaAdmin(BaseAdmin):
    list_display = ("platform",)
    search_fields = ("platform",)


@admin.register(m.SocialPost)
class SocialPostAdmin(BaseAdmin):
    posted_j = jalali_display("posted_at", label="Posted")

    @display(description="Platform")
    def platforms_disp(self, obj):
        if obj.platform:
            return obj.platform.platform
        return "—" # Display a dash if no platform is set

    list_display = ("platforms_disp", "learner", "step_progress", "posted_j")
    list_filter = ("platform",)
    autocomplete_fields = ("learner", "step_progress", "platform")
    search_fields = ("learner__user__email", "step_progress__educational_step__title", "urls")


# ──────────────────────────────────────────────────────────────
# MENTOR GROUP SESSIONS  ✅ (present & registered)
# ──────────────────────────────────────────────────────────────
@admin.register(m.MentorGroupSessionParticipant)
class MentorGroupSessionParticipantAdmin(BaseAdmin):
    list_display = (
        "mentor_group_session_occurence",
        "mentor_assignment",
        "learner_was_present",
    )
    list_filter = ("learner_was_present",)
    autocomplete_fields = (
        "mentor_group_session_occurence",
        "mentor_assignment",
    )
    search_fields = ("mentor_assignment__mentor__user__email",)
    list_select_related = ("mentor_group_session_occurence", "mentor_assignment")


class MGSParticipantInline(TabularInline):
    model = m.MentorGroupSessionParticipant
    tab = True
    extra = 0
    autocomplete_fields = ("mentor_assignment",)
    fields = ("mentor_assignment", "learner_was_present")


@admin.register(m.MentorGroupSessionOccurrence)
class MentorGroupSessionOccurrenceAdmin(BaseAdmin):
    list_display = (
        "mentor_group_session",
        "occurence_datetime",
        "occurence_datetime_changed",
        "new_datetime",
        "session_video_record",
    )
    fields = (
        "mentor_group_session",
        "occurence_datetime",
        "occurence_datetime_changed",
        "new_datetime",
        "reason_for_change",
        "session_video_record",
    )
    autocomplete_fields = ("mentor_group_session",)
    search_fields = (
        "mentor_group_session__learning_path__name",
        "mentor_group_session__mentor__user__email",
    )
    list_select_related = ("mentor_group_session",)
    inlines = (MGSParticipantInline,)
    conditional_fields = {
        "new_datetime": "occurence_datetime_changed == true",
        "reason_for_change": "occurence_datetime_changed == true",
    }


class MGSOccurrenceInline(TabularInline):
    model = m.MentorGroupSessionOccurrence
    tab = True
    extra = 0
    fields = (
        "occurence_datetime",
        "occurence_datetime_changed",
        "new_datetime",
        "reason_for_change",
        "session_video_record",
    )
    conditional_fields = {
        "new_datetime": "occurence_datetime_changed == true",
        "reason_for_change": "occurence_datetime_changed == true",
    }


@admin.register(m.MentorGroupSession)
class MentorGroupSessionAdmin(BaseAdmin):
    list_display = (
        "mentor",
        "learning_path",
        "session_type",
        "suppused_day",
        "suppoused_time",
    )
    list_filter = ("mentor", "learning_path", "session_type", "suppused_day")
    autocomplete_fields = ("mentor", "learning_path", "session_type")
    inlines = (MGSOccurrenceInline,)
    search_fields = ("mentor__user__email", "learning_path__name")


# ──────────────────────────────────────────────────────────────
# SUBSCRIPTIONS (financial analytics stay separate)
# ──────────────────────────────────────────────────────────────
class SubscriptionTransactionResource(resources.ModelResource):
    class Meta:
        model = m.SubscriptionTransaction
        fields = (
            "id",
            "learner_enrollment__learner__user__username",
            "subscription_plan__name",
            "kind",
            "status",
            "amount",
            "paid_at",
            "gateway",
            "ref",
            "note",
        )
        export_order = fields


@admin.register(m.SubscriptionTransaction)
class SubscriptionTransactionAdmin(SimpleHistoryAdmin, ModelAdmin):
    resource_class = SubscriptionTransactionResource
    list_display = (
        "learner_enrollment",
        "subscription_plan",
        "kind",
        "status",
        "amount_disp",
        "paid_at",
    )
    list_filter = ("kind", "status", "subscription_plan", "gateway")
    search_fields = (
        "learner_enrollment__learner__user__username",
        "subscription_plan__name",
        "ref",
        "note",
    )
    date_hierarchy = "paid_at"
    autocomplete_fields = ("learner_enrollment", "subscription", "subscription_plan")

    @display(description=_("Amount (T)"))
    def amount_disp(self, obj):
        return intcomma(obj.amount)


@admin.register(m.Feature)
class FeatureAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(BaseAdmin):
    active_badge = bool_badge("is_active")
    price_disp = display(description=_("Price (T)"))(lambda _, o: intcomma(o.price_amount))
    dur_disp = display(description=_("Duration (d)"))(lambda _, o: o.duration_in_days)

    list_display = ("name", "price_disp", "dur_disp", "active_badge")
    list_filter = ("is_active", "duration_in_days")
    search_fields = ("name",)
    filter_horizontal = ("features",)


class FreezeInline(TabularInline):
    model = m.LearnerSubscribePlanFreeze
    extra = 0
    fields = ("duration",)


class TransactionInline(admin.TabularInline):
    model = m.SubscriptionTransaction
    extra = 0
    fields = ("paid_at", "kind", "status", "amount", "gateway", "ref", "note")
    readonly_fields = ("paid_at", "kind", "status", "amount", "gateway", "ref")


@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(ModelAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm
    resource_classes = [LearnerSubscribePlanResource]
    inlines = (TransactionInline,)
    autocomplete_fields = ['learner_enrollment', "subscription_plan"]
    show_full_result_count = False
    list_select_related = (
        "learner_enrollment__learner__user",
        "learner_enrollment__learning_path",
        "subscription_plan",
    )
    list_display = (
        "learner_full_name",
        "plan_name",
        "start_shamsi",
        "end_shamsi",
        "discount_percent",
        "final_cost_h",
        "status_badge",
    )
    list_filter = ("status", "subscription_plan")
    search_fields = (
        "learner_enrollment__learner__user__first_name",
        "learner_enrollment__learner__user__last_name",
        "subscription_plan__name",
    )
    ordering = ("-start_datetime", "-id")
    list_per_page = 50
    readonly_fields = ("end_datetime", "expired_at")
    actions_list = ["go_analytics_dropdown"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "learner_enrollment__learner__user",
            "learner_enrollment__learning_path",
            "subscription_plan",
        )

    @action(description=_("Analytics & Export"), icon="query_stats", variant=ActionVariant.PRIMARY)
    def go_analytics_dropdown(self, request: HttpRequest, queryset=None):
        return redirect(reverse("admin:courses_learnersubscribeplan_analytics"))

    def learner_full_name(self, obj: m.LearnerSubscribePlan) -> str:
        u = obj.learner_enrollment.learner.user
        return f"{u.first_name} {u.last_name}".strip() or u.email

    def plan_name(self, obj: m.LearnerSubscribePlan) -> str:
        return obj.subscription_plan.name

    def start_shamsi(self, obj: m.LearnerSubscribePlan) -> str:
        return _format_shamsi(obj.start_datetime)

    def end_shamsi(self, obj: m.LearnerSubscribePlan) -> str:
        return _format_shamsi(obj.end_datetime)

    def discount_percent(self, obj: m.LearnerSubscribePlan) -> str:
        try:
            return f"{int(Decimal(obj.discount))}%"
        except Exception:
            return f"{obj.discount}%"

    def final_cost_h(self, obj: m.LearnerSubscribePlan) -> str:
        return f"{intcomma(obj.final_cost)}"

    def status_badge(self, obj: m.LearnerSubscribePlan) -> str:
        if obj.status == m.LearnerSubscribePlan.STATUS_ACTIVE:
            return format_html(badge(_("Active"), "success"))
        elif obj.status == m.LearnerSubscribePlan.STATUS_EXPIRED:
            return format_html(badge(_("Expired"), "danger"))
        return format_html(badge(str(obj.status), "default"))

    status_badge.short_description = _("Status")
    learner_full_name.short_description = _("Learner")
    plan_name.short_description = _("Plan")
    start_shamsi.short_description = _("Start (Shamsi)")
    end_shamsi.short_description = _("End (Shamsi)")
    discount_percent.short_description = _("Disc")
    final_cost_h.short_description = _("Final Cost")

    def get_export_formats(self) -> List[Type[Format]]:
        fmts: List[Type[Format]] = [CSV, JSON, XLSX]
        if getattr(settings, "USE_WEASYPRINT", False):
            fmts.append(PDF)
        return fmts

    def get_urls(self):
        return [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="courses_learnersubscribeplan_analytics",
            ),
            path(
                "analytics/data/",
                self.admin_site.admin_view(self.analytics_data),
                name="courses_learnersubscribeplan_analytics_data",
            ),
        ] + super().get_urls()

    def analytics_view(self, request: HttpRequest):
        ctx = dict(self.admin_site.each_context(request), title=_("Subscriptions Analytics"))
        return TemplateResponse(
            request,
            "admin/courses/learner_subscribe_plan/analytics.html",
            ctx,
        )

    def analytics_data(self, request: HttpRequest):
        chart = (request.GET.get("chart") or "monthly_revenue").strip()
        year = int(request.GET.get("year") or timezone.now().year)
        month_str = (request.GET.get("month") or "").strip()
        month = int(month_str) if month_str.isdigit() else None
        scope = (request.GET.get("scope") or "all").lower()

        qs = m.LearnerSubscribePlan.objects.select_related(
            "subscription_plan",
            "learner_enrollment__learner__user",
            "learner_enrollment__learning_path",
        )
        if scope == "active":
            qs = qs.filter(status=m.LearnerSubscribePlan.STATUS_ACTIVE)

        if chart == "monthly_revenue":
            if month:
                rows = (
                    qs.filter(start_datetime__year=year, start_datetime__month=month)
                    .annotate(d=TruncDate("start_datetime"))
                    .values("d")
                    .order_by("d")
                    .annotate(revenue=Sum("final_cost"), count=Count("id"))
                )
                labels, revenues, counts = [], [], []
                for r in rows:
                    dval = r["d"]
                    labels.append(dval.strftime("%Y-%m-%d"))
                    revenues.append(int(r["revenue"] or 0))
                    counts.append(int(r["count"] or 0))
                return JsonResponse(
                    {
                        "chart": chart,
                        "year": year,
                        "month": month,
                        "labels": labels,
                        "revenues": revenues,
                        "counts": counts,
                        "total_revenue": sum(revenues),
                        "total_count": sum(counts),
                    }
                )
            else:
                rows = (
                    qs.filter(start_datetime__year=year)
                    .annotate(m=TruncMonth("start_datetime"))
                    .values("m")
                    .order_by("m")
                    .annotate(revenue=Sum("final_cost"), count=Count("id"))
                )
                labels, revenues, counts = [], [], []
                for r in rows:
                    mval = r["m"]
                    labels.append(mval.strftime("%Y-%m"))
                    revenues.append(int(r["revenue"] or 0))
                    counts.append(int(r["count"] or 0))
                return JsonResponse(
                    {
                        "chart": chart,
                        "year": year,
                        "labels": labels,
                        "revenues": revenues,
                        "counts": counts,
                        "total_revenue": sum(revenues),
                        "total_count": sum(counts),
                    }
                )

        if chart == "plan_counts":
            base = qs.filter(start_datetime__year=year)
            if month:
                base = base.filter(start_datetime__month=month)
            rows = base.values("subscription_plan__name").annotate(c=Count("id")).order_by("-c")
            labels = [r["subscription_plan__name"] or "—" for r in rows]
            counts = [int(r["c"] or 0) for r in rows]
            return JsonResponse(
                {"chart": chart, "year": year, "month": month, "labels": labels, "counts": counts, "total": sum(counts)}
            )

        if chart == "paths_pie":
            base = qs.filter(start_datetime__year=year)
            if month:
                base = base.filter(start_datetime__month=month)
            rows = (
                base.values("learner_enrollment__learning_path__name")
                .annotate(c=Count("id"))
                .order_by("-c")
            )
            labels = [r["learner_enrollment__learning_path__name"] or "—" for r in rows]
            values = [int(r["c"] or 0) for r in rows]
            return JsonResponse({"chart": chart, "labels": labels, "values": values})

        if chart == "age_scatter":
            base = qs.filter(start_datetime__year=year)
            if month:
                base = base.filter(start_datetime__month=month)
            rev = base.values("learner_enrollment__learner_id").annotate(total=Sum("final_cost"))
            rev_map = {
                r["learner_enrollment__learner_id"]: int(r["total"] or 0)
                for r in rev if r["learner_enrollment__learner_id"]
            }
            learner_ids = list(rev_map.keys())
            ages, totals = [], []
            if learner_ids:
                learners = m.Learner.objects.filter(id__in=learner_ids).select_related("user")
                today = timezone.now().date()
                for lr in learners:
                    dob = getattr(lr.user, "birthdate", None)
                    if dob:
                        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                        if 5 <= age <= 100:
                            ages.append(int(age))
                            totals.append(rev_map.get(lr.id, 0))
            return JsonResponse({"chart": chart, "x": ages, "y": totals, "x_title": "Age", "y_title": "Revenue (T)"})

        return JsonResponse({"chart": chart, "labels": [], "revenues": [], "counts": []})
