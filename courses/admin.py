# core/admin.py – Django 5.2.4 + Unfold
from __future__ import annotations

from datetime import date as _dt_date, datetime as _dt_dt, time as _dt_time, timezone as _dt_tz

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from unfold.decorators import display

from pages.templatetags.custom_translation_tags import translate_number
from pages.templatetags.persian_calendar_convertor import (
    convert_to_persian_calendar,
    format_persian_datetime,
)

from . import models as m

# ════════════════════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════════════════════
def jalali_display(attr: str = "created_at", *, label: str | None = None):
    label = label or attr.replace("_", " ").title()

    @display(description=label)
    def _func(self, obj):
        value = getattr(obj, attr)
        if not value:
            return "-"
        if isinstance(value, _dt_date) and not isinstance(value, _dt_dt):
            value = _dt_dt.combine(value, _dt_time.min, tzinfo=_dt_tz.utc)
        pers = format_persian_datetime(convert_to_persian_calendar(value))
        return format_html("<b dir='rtl'>{}</b>", translate_number(pers))

    _func.__name__ = f"{attr}_jalali"
    return _func


def bool_badge(
    attr: str,
    *,
    description: str = "Status",
    true_text: str = "Active",
    false_text: str = "Inactive",
    true_color: str = "success",
    false_color: str = "danger",
):
    """Badge generator for Boolean fields."""
    @display(description=description, label={True: true_color, False: false_color})
    def _func(self, obj):
        val = getattr(obj, attr)
        return val, true_text if val else false_text

    _func.__name__ = f"{attr}_badge"
    return _func


def choice_badge(
    attr: str,
    *,
    mapping: dict[str, tuple[str, str]],  # value -> (text, color)
    description: str = "Status",
):
    """
    Badge generator for CharFields.
    mapping={"active": ("Active", "success"), "inactive": ("Inactive", "danger")}
    """
    label_map = {k: v[1] for k, v in mapping.items()}

    @display(description=description, label=label_map)
    def _func(self, obj):
        val = getattr(obj, attr)
        text, _color = mapping.get(val, (val, "info"))
        return val, text

    _func.__name__ = f"{attr}_badge"
    return _func


# ════════════════════════════════════════════════════════════════════════════
#  Global widgets
# ════════════════════════════════════════════════════════════════════════════
RICH_TEXT = {models.TextField: {"widget": WysiwygWidget}}
FORM_OVERRIDES = {
    **RICH_TEXT,
    models.JSONField: {"widget": ArrayWidget},
}

# ════════════════════════════════════════════════════════════════════════════
#  Inlines (unchanged content)
# ════════════════════════════════════════════════════════════════════════════
class TimeStampedInline(TabularInline):
    extra = 0
    readonly_fields = ("created_at",)


class TaskInline(TabularInline):
    model = m.Task
    extra = 0
    fields = ("title", "order_in_step", "is_required")
    formfield_overrides = RICH_TEXT


class ResourceInline(TimeStampedInline):
    model = m.Resource
    fields = ("title", "type", "url_or_location", "description")
    formfield_overrides = RICH_TEXT


# ════════════════════════════════════════════════════════════════════════════
#  Curriculum
# ════════════════════════════════════════════════════════════════════════════
class EducationalStepInline(StackedInline):
    model = m.EducationalStep
    extra = 0
    show_change_link = True
    formfield_overrides = RICH_TEXT
    fields = ("sequence_no", "title", "description", ("expected_duration_days", "is_mandatory"))


@admin.register(m.LearningPath)
class LearningPathAdmin(ModelAdmin):
    is_active_badge = bool_badge("is_active")
    created_j = jalali_display()
    list_display = ("name", "is_active_badge", "created_j")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    inlines = (EducationalStepInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.EducationalStep)
class EducationalStepAdmin(ModelAdmin):
    search_fields = "title", "description"
    created_j = jalali_display()
    is_mandatory_badge = bool_badge(
        "is_mandatory",
        true_text="Mandatory",
        false_text="Optional",
        true_color="danger",
        false_color="info",
        description="Status",
    )
    list_display = (
        "__str__",
        "expected_duration_days",
        "is_mandatory_badge",
        "created_j",
    )
    list_filter = ("learning_path", "is_mandatory")
    autocomplete_fields = ("learning_path",)
    inlines = (TaskInline, ResourceInline)
    ordering = ("learning_path", "sequence_no")
    formfield_overrides = RICH_TEXT


@admin.register(m.Resource)
class ResourceAdmin(ModelAdmin):
    created_j = jalali_display()
    list_display = ("title", "type", "step", "created_j")
    list_filter = ("type", "step__learning_path")
    search_fields = ("title", "url_or_location")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT


# ════════════════════════════════════════════════════════════════════════════
#  People
# ════════════════════════════════════════════════════════════════════════════
@admin.register(m.Learner)
class LearnerAdmin(ModelAdmin):
    signup_j = jalali_display("signup_date", label="Signup")
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "inactive": ("Inactive", "danger"),
        },
    )
    list_display = (
        "first_name",
        "last_name",
        "email",
        "country",
        "status_badge",
        "signup_j",
    )
    list_filter = ("status", "country")
    search_fields = ("first_name", "last_name", "email")
    readonly_fields = ("signup_date",)
    formfield_overrides = RICH_TEXT


@admin.register(m.Specialty)
class SpecialtyAdmin(ModelAdmin):
    is_active_badge = bool_badge("is_active")
    list_display = ("name", "code", "is_active_badge", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    list_editable = ("is_active",)
    formfield_overrides = RICH_TEXT


@admin.register(m.Mentor)
class MentorAdmin(ModelAdmin):
    hire_j = jalali_display("hire_date", label="Hire Date")
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "inactive": ("Inactive", "danger"),
        },
    )

    @display(header=True, description="Mentor")
    def heading(self, obj):
        initials = f"{obj.first_name[0]}{obj.last_name[0]}"
        return [f"{obj.first_name} {obj.last_name}", obj.email, initials]

    list_display = ("heading", "phone", "hire_j", "status_badge")
    list_filter = ("status", "specialties")
    autocomplete_fields = ("specialties",)
    search_fields = ("first_name", "last_name", "email")
    formfield_overrides = RICH_TEXT


# ════════════════════════════════════════════════════════════════════════════
#  Enrolment & mentoring (unchanged except formfield_overrides)
# ════════════════════════════════════════════════════════════════════════════
class MentorAssignmentInline(TabularInline):
    model = m.MentorAssignment
    extra = 0
    autocomplete_fields = ("mentor",)
    fields = ("mentor", "start_date", "end_date", "reason_for_change")


@admin.register(m.LearnerEnrolment)
class LearnerEnrolmentAdmin(ModelAdmin):
    list_display = ("learner", "learning_path", "enroll_date", "unenroll_date")
    autocomplete_fields = ("learner", "learning_path")
    list_filter = ("learning_path",)
    search_fields = ("learner__email", "learning_path__name")
    inlines = (MentorAssignmentInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.MentorAssignment)
class MentorAssignmentAdmin(ModelAdmin):
    list_display = ("enrolment", "mentor", "start_date", "end_date")
    autocomplete_fields = ("enrolment", "mentor")
    list_filter = ("mentor",)
    formfield_overrides = RICH_TEXT
    search_fields = (
       "mentor__first_name",
       "mentor__last_name",
       "mentor__email",
       "enrolment__learner__email",
   )


# ════════════════════════════════════════════════════════════════════════════
#  Sessions
# ════════════════════════════════════════════════════════════════════════════
class SessionOccurrenceInline(TabularInline):
    model = m.SessionOccurrence
    extra = 0
    autocomplete_fields = ("template",)
    fields = ("planned_date", "planned_start_time", "planned_end_time", "status")
    formfield_overrides = RICH_TEXT


@admin.register(m.SessionType)
class SessionTypeAdmin(ModelAdmin):
    list_display = ("code", "name_fa", "duration_minutes", "max_participants")
    search_fields = ("code", "name_fa")
    formfield_overrides = RICH_TEXT


class SessionTemplateInline(TabularInline):
    model = m.SessionTemplate
    extra = 0
    autocomplete_fields = ("session_type", "learning_path")
    fields = ("session_type", "weekday", "active_from", "status", "google_meet_link")


@admin.register(m.SessionTemplate)
class SessionTemplateAdmin(ModelAdmin):
    search_fields = (
       "learning_path__name",
       "mentor_assignment__mentor__first_name",
       "mentor_assignment__mentor__last_name",
       "mentor_assignment__mentor__email",
    )
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "expired": ("Expired", "danger"),
        },
    )
    list_display = (
        "learning_path",
        "mentor_assignment",
        "session_type",
        "weekday",
        "status_badge",
    )
    list_filter = ("weekday", "status", "learning_path")
    autocomplete_fields = ("learning_path", "mentor_assignment", "session_type")
    inlines = (SessionOccurrenceInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.SessionOccurrence)
class SessionOccurrenceAdmin(ModelAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "scheduled": ("Scheduled", "info"),
            "held": ("Held", "success"),
            "canceled": ("Canceled", "danger"),
        },
    )
    list_display = ("template", "planned_date", "planned_start_time", "status_badge")
    list_filter = ("status", "template__learning_path")
    autocomplete_fields = ("template",)
    formfield_overrides = RICH_TEXT


# ════════════════════════════════════════════════════════════════════════════
#  Progress & tasks  (unchanged list logic)
# ════════════════════════════════════════════════════════════════════════════
class StepExtensionInline(TabularInline):
    model = m.StepExtension
    extra = 0
    readonly_fields = ("requested_at",)
    formfield_overrides = RICH_TEXT
    fields = ("extended_by_days", "requested_at", "approved_by_mentor", "reason")


@admin.register(m.StepProgress)
class StepProgressAdmin(ModelAdmin):
    skipped_badge = bool_badge("skipped", true_text="Skipped", false_text="On Track")
    list_display = ("enrolment", "step", "initial_due_date", "skipped_badge")
    autocomplete_fields = ("enrolment", "step")
    list_filter = ("skipped", "step__learning_path")
    inlines = (StepExtensionInline,)
    formfield_overrides = RICH_TEXT
    search_fields = (
       "enrolment__learner__email",
       "step__title",
       "step__learning_path__name",
    )


@admin.register(m.Task)
class TaskAdmin(ModelAdmin):
    list_display = ("title", "step", "order_in_step", "is_required")
    list_filter = ("is_required", "step__learning_path")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT


class TaskEvaluationInline(TabularInline):
    model = m.TaskEvaluation
    extra = 0
    autocomplete_fields = ("mentor",)
    readonly_fields = ("evaluated_at",)
    formfield_overrides = RICH_TEXT
    fields = ("mentor", "score_numeric", "feedback_text", "evaluated_at")


@admin.register(m.TaskSubmission)
class TaskSubmissionAdmin(ModelAdmin):
    submitted_j = jalali_display("submitted_at", label="Submitted")
    list_display = ("step_progress", "submitted_j")
    autocomplete_fields = ("step_progress",)
    inlines = (TaskEvaluationInline,)
    readonly_fields = ("submitted_at",)
    formfield_overrides = RICH_TEXT


@admin.register(m.SocialPost)
class SocialPostAdmin(ModelAdmin):
    posted_j = jalali_display("posted_at", label="Posted")
    list_display = ("platform", "url", "posted_j")
    list_filter = ("platform",)
    search_fields = ("url",)
    autocomplete_fields = ("step_progress",)
    readonly_fields = ("posted_at",)
    formfield_overrides = RICH_TEXT


# ════════════════════════════════════════════════════════════════════════════
#  Subscription plans
# ════════════════════════════════════════════════════════════════════════════
class PlanFeatureInline(TabularInline):
    model = m.PlanFeature
    extra = 0
    autocomplete_fields = ("feature",)
    formfield_overrides = RICH_TEXT


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    is_active_badge = bool_badge("is_active")
    price_display = display(description="Price")(lambda _, o: intcomma(int(o.price_amount)))
    duration_display = display(description="Duration (d)")(lambda _, o: o.duration_in_days)

    list_display = ("name", "price_display", "duration_display", "is_active_badge")
    list_filter = ("is_active", "duration_in_days")
    search_fields = ("name", "description")
    inlines = (PlanFeatureInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.Feature)
class FeatureAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    formfield_overrides = RICH_TEXT


class FreezeInline(TabularInline):
    model = m.LearnerSubscribePlanFreeze
    extra = 0
    formfield_overrides = RICH_TEXT
    fields = ("start_date", "duration")


@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(ModelAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "expired": ("Expired", "danger"),
            "canceled": ("Canceled", "danger"),
            "reserved": ("Reserved", "info"),
            "freeze": ("Frozen", "info"),
        },
    )
    start_j = jalali_display("start_date", label="Start")

    list_display = (
        "learner_enrolment",
        "subscription_plan",
        "start_j",
        "status_badge",
    )
    list_filter = ("status", "subscription_plan")
    autocomplete_fields = ("subscription_plan", "learner_enrolment")
    inlines = (FreezeInline,)
    formfield_overrides = RICH_TEXT
