# core/admin.py  – Django 5.2.4 + django‑unfold
from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from . import models as m

# --------------------------------------------------------------------------- #
#  Shared helpers
# --------------------------------------------------------------------------- #
RICH_TEXT = {models.TextField: {"widget": WysiwygWidget}}


class TimeStampedInline(TabularInline):
    extra = 0
    readonly_fields = ("created_at",)


# --------------------------------------------------------------------------- #
#  Inlines that must exist *before* parent admins reference them
# --------------------------------------------------------------------------- #
class TaskInline(TabularInline):
    """Tasks belong to an EducationalStep (FK: step)."""
    model = m.Task
    extra = 0
    fields = ("title", "order_in_step", "is_required")
    formfield_overrides = RICH_TEXT


class ResourceInline(TimeStampedInline):
    model = m.Resource
    fields = ("title", "type", "url_or_location", "description")
    formfield_overrides = RICH_TEXT


# --------------------------------------------------------------------------- #
#  Curriculum & resources
# --------------------------------------------------------------------------- #
class EducationalStepInline(StackedInline):
    model = m.EducationalStep
    show_change_link = True
    extra = 0
    formfield_overrides = RICH_TEXT
    fields = (
        "sequence_no",
        "title",
        "description",
        ("expected_duration_days", "is_mandatory"),
    )


@admin.register(m.LearningPath)
class LearningPathAdmin(ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    inlines = (EducationalStepInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.EducationalStep)
class EducationalStepAdmin(ModelAdmin):
    list_display = ("__str__", "expected_duration_days", "is_mandatory", "created_at")
    list_filter = ("learning_path", "is_mandatory")
    autocomplete_fields = ("learning_path",)
    search_fields = ("title", "description")
    inlines = (TaskInline, ResourceInline)
    formfield_overrides = RICH_TEXT
    ordering = ("learning_path", "sequence_no")


@admin.register(m.Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ("title", "type", "step", "created_at")
    list_filter = ("type", "step__learning_path")
    search_fields = ("title", "url_or_location", "description")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT


# --------------------------------------------------------------------------- #
#  People
# --------------------------------------------------------------------------- #
@admin.register(m.Learner)
class LearnerAdmin(ModelAdmin):
    list_display = ("first_name", "last_name", "email", "country", "status", "signup_date")
    list_filter = ("status", "country")
    search_fields = ("first_name", "last_name", "email", "phone")
    readonly_fields = ("signup_date",)
    formfield_overrides = RICH_TEXT


@admin.register(m.Mentor)
class MentorAdmin(ModelAdmin):
    list_display = ("first_name", "last_name", "email", "hire_date", "status")
    list_filter = ("status",)
    search_fields = ("first_name", "last_name", "email", "specialties")
    formfield_overrides = RICH_TEXT


# --------------------------------------------------------------------------- #
#  Enrolment & mentoring
# --------------------------------------------------------------------------- #
class MentorAssignmentInline(TabularInline):
    model = m.MentorAssignment
    extra = 0
    autocomplete_fields = ("mentor",)
    fields = ("mentor", "start_date", "end_date", "reason_for_change")


@admin.register(m.LearnerEnrolment)
class LearnerEnrolmentAdmin(ModelAdmin):
    list_display = ("learner", "learning_path", "enroll_date", "unenroll_date")
    list_filter = ("learning_path",)
    search_fields = (
        "learner__first_name",
        "learner__last_name",
        "learner__email",
        "learning_path__name",
    )
    autocomplete_fields = ("learner", "learning_path")
    inlines = (MentorAssignmentInline,)


@admin.register(m.MentorAssignment)
class MentorAssignmentAdmin(ModelAdmin):
    list_display = ("enrolment", "mentor", "start_date", "end_date")
    list_filter = ("mentor",)
    autocomplete_fields = ("enrolment", "mentor")
    search_fields = (
        "enrolment__learner__email",
        "mentor__email",
        "mentor__first_name",
        "mentor__last_name",
    )
    formfield_overrides = RICH_TEXT


# --------------------------------------------------------------------------- #
#  Sessions
# --------------------------------------------------------------------------- #
class SessionOccurrenceInline(TabularInline):
    model = m.SessionOccurrence
    extra = 0
    fields = (
        ("planned_date", "planned_start_time", "planned_end_time"),
        ("status", "recorded_meet_link"),
    )
    autocomplete_fields = ("template",)
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
    fields = (
        "session_type",
        "weekday",
        "active_from",
        "status",
        "google_meet_link",
    )


@admin.register(m.SessionTemplate)
class SessionTemplateAdmin(ModelAdmin):
    list_display = ("learning_path", "mentor_assignment", "session_type", "weekday", "status")
    list_filter = ("weekday", "status", "learning_path")
    autocomplete_fields = ("learning_path", "mentor_assignment", "session_type")
    search_fields = (
        "learning_path__name",
        "mentor_assignment__mentor__first_name",
        "mentor_assignment__mentor__last_name",
    )
    inlines = (SessionOccurrenceInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.SessionOccurrence)
class SessionOccurrenceAdmin(ModelAdmin):
    list_display = ("template", "planned_date", "planned_start_time", "status")
    list_filter = ("status", "template__learning_path")
    autocomplete_fields = ("template",)
    search_fields = ("template__learning_path__name",)
    inlines = (
        type(
            "ParticipantInline",
            (TabularInline,),
            {
                "model": m.SessionParticipant,
                "extra": 0,
                "autocomplete_fields": ("learner",),
                "fields": ("learner", "attendance_status", "guest_name"),
            },
        ),
    )
    formfield_overrides = RICH_TEXT


# --------------------------------------------------------------------------- #
#  Progress & tasks
# --------------------------------------------------------------------------- #
class StepExtensionInline(TabularInline):
    model = m.StepExtension
    extra = 0
    fields = ("extended_by_days", "requested_at", "approved_by_mentor", "reason")
    formfield_overrides = RICH_TEXT
    readonly_fields = ("requested_at",)


@admin.register(m.StepProgress)
class StepProgressAdmin(ModelAdmin):
    list_display = ("enrolment", "step", "initial_due_date", "skipped")
    list_filter = ("skipped", "step__learning_path")
    autocomplete_fields = ("enrolment", "step")
    search_fields = (
        "enrolment__learner__first_name",
        "enrolment__learner__last_name",
        "step__title",
        "step__learning_path__name",
    )
    inlines = (StepExtensionInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.Task)
class TaskAdmin(ModelAdmin):
    list_display = ("title", "step", "order_in_step", "is_required")
    list_filter = ("step__learning_path", "is_required")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT


class TaskEvaluationInline(TabularInline):
    model = m.TaskEvaluation
    extra = 0
    autocomplete_fields = ("mentor",)
    fields = ("mentor", "score_numeric", "feedback_text", "evaluated_at")
    readonly_fields = ("evaluated_at",)
    formfield_overrides = RICH_TEXT


@admin.register(m.TaskSubmission)
class TaskSubmissionAdmin(ModelAdmin):
    list_display = ("step_progress", "submitted_at")
    autocomplete_fields = ("step_progress",)
    inlines = (TaskEvaluationInline,)
    formfield_overrides = RICH_TEXT
    readonly_fields = ("submitted_at",)


@admin.register(m.SocialPost)
class SocialPostAdmin(ModelAdmin):
    list_display = ("platform", "url", "posted_at")
    list_filter = ("platform",)
    search_fields = ("url",)
    autocomplete_fields = ("step_progress",)
    readonly_fields = ("posted_at",)


# --------------------------------------------------------------------------- #
#  Subscription plans
# --------------------------------------------------------------------------- #
class PlanFeatureInline(TabularInline):
    model = m.PlanFeature
    extra = 0
    autocomplete_fields = ("feature",)
    formfield_overrides = RICH_TEXT


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ("name", "price_amount", "duration_in_days", "is_active")
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
    fields = ("start_date", "duration")


@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(ModelAdmin):
    list_display = (
        "learner_enrolment",
        "subscription_plan",
        "start_date",
        "duration_in_days",
        "status",
    )
    list_filter = ("status", "subscription_plan")
    autocomplete_fields = ("subscription_plan", "learner_enrolment")
    search_fields = (
        "learner_enrolment__learner__first_name",
        "learner_enrolment__learner__last_name",
        "subscription_plan__name",
    )
    inlines = (FreezeInline,)
