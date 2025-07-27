# courses/admin.py – Django 5.2 + Unfold 0.24 + django‑import‑export 4.x
from __future__ import annotations

from datetime import date as _dt_date, datetime as _dt_dt, time as _dt_time, timezone as _dt_tz

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.decorators import display

from pages.templatetags.custom_translation_tags import translate_number
from pages.templatetags.persian_calendar_convertor import (
    convert_to_persian_calendar,
    format_persian_datetime,
)

from . import models as m

# ────────────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────────────
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
    true_text: str = "Yes",
    false_text: str = "No",
    true_color: str = "success",
    false_color: str = "danger",
):
    @display(description=description, label={True: true_color, False: false_color})
    def _func(self, obj):
        val = getattr(obj, attr)
        return val, true_text if val else false_text

    _func.__name__ = f"{attr}_badge"
    return _func


def choice_badge(attr: str, *, mapping: dict[str, tuple[str, str]], description: str = "Status"):
    """
    mapping = {
        "raw_value": ("Display text", "unfold‑colour"),   # e.g. "success", "danger", "warning", "info", "secondary"
    }
    """
    label_map = {k: v[1] for k, v in mapping.items()}  # colour map

    @display(description=description, label=label_map)
    def _func(self, obj):
        raw = getattr(obj, attr)
        text, _ = mapping.get(raw, (raw, "info"))
        return raw, text  # (value, caption)

    _func.__name__ = f"{attr}_badge"
    return _func

# ────────────────────────────────────────────────────────────────
#  Global widgets & Import‑Export base
# ────────────────────────────────────────────────────────────────
RICH_TEXT = {models.TextField: {"widget": WysiwygWidget}}
FORM_OVERRIDES = {**RICH_TEXT, models.JSONField: {"widget": ArrayWidget}}


class BaseIEAdmin(ModelAdmin, ImportExportModelAdmin):
    """
    Every concrete admin below inherits from this mixin:
    * Unfold styling (ModelAdmin)
    * django‑import‑export bulk export/import
    """
    import_form_class = ImportForm
    export_form_class = ExportForm
    show_full_result_count = False  # speed up large changelists


# ────────────────────────────────────────────────────────────────
#  Inlines (unchanged)
# ────────────────────────────────────────────────────────────────
class TimeStampedInline(TabularInline):
    extra = 0
    readonly_fields = ("created_at",)


class TaskInline(TabularInline):
    model = m.Task
    extra = 0
    fields = ("title", "order_in_step", "is_required_badge")
    readonly_fields = ("is_required_badge",)
    formfield_overrides = RICH_TEXT

    is_required_badge = bool_badge(
        "is_required",
        true_text="Required",
        false_text="Optional",
        true_color="danger",
        false_color="info",
    )


class ResourceInline(TimeStampedInline):
    model = m.Resource
    fields = ("title", "type", "url_or_location", "description")
    formfield_overrides = RICH_TEXT


# ────────────────────────────────────────────────────────────────
#  Curriculum
# ────────────────────────────────────────────────────────────────
class EducationalStepInline(StackedInline):
    model = m.EducationalStep
    extra = 0
    show_change_link = True
    formfield_overrides = RICH_TEXT
    fields = ("sequence_no", "title", "description", ("expected_duration_days", "is_mandatory_badge"))
    readonly_fields = ("is_mandatory_badge",)

    is_mandatory_badge = bool_badge(
        "is_mandatory",
        true_text="Mandatory",
        false_text="Optional",
        true_color="danger",
        false_color="info",
    )


@admin.register(m.LearningPath)
class LearningPathAdmin(BaseIEAdmin):
    is_active_badge = bool_badge(
        "is_active",
        true_text="Active",
        false_text="Inactive",
        true_color="success",
        false_color="danger",
    )
    created_j = jalali_display()

    list_display = ("name", "is_active_badge", "created_j")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    inlines = (EducationalStepInline,)
    formfield_overrides = RICH_TEXT

    # bulk actions
    @admin.action(description="Mark selected paths as active")
    def make_active(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description="Mark selected paths as inactive")
    def make_inactive(self, request, qs):
        qs.update(is_active=False)

    actions = ("make_active", "make_inactive")


@admin.register(m.EducationalStep)
class EducationalStepAdmin(BaseIEAdmin):
    created_j = jalali_display()
    is_mandatory_badge = bool_badge(
        "is_mandatory",
        true_text="Mandatory",
        false_text="Optional",
        true_color="danger",
        false_color="info",
    )

    list_display = ("__str__", "expected_duration_days", "is_mandatory_badge", "created_j")
    list_filter = ("learning_path", "is_mandatory")
    autocomplete_fields = ("learning_path",)
    inlines = (TaskInline, ResourceInline)
    ordering = ("learning_path", "sequence_no")
    formfield_overrides = RICH_TEXT
    search_fields = ("title", "description")


@admin.register(m.Resource)
class ResourceAdmin(BaseIEAdmin):
    created_j = jalali_display()
    list_display = ("title", "type", "step", "created_j")
    list_filter = ("type", "step__learning_path")
    search_fields = ("title", "url_or_location")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT


# ────────────────────────────────────────────────────────────────
#  People
# ────────────────────────────────────────────────────────────────
@admin.register(m.Learner)
class LearnerAdmin(BaseIEAdmin):
    signup_j = jalali_display("signup_date", label="Signup")
    status_badge = choice_badge(
        "status",
        mapping={"active": ("Active", "success"), "inactive": ("Inactive", "danger")},
    )

    # 1️⃣  city_column replaces raw "city"
    list_display = ("user_fullname", "email", "city_column", "status_badge", "signup_j")

    # 2️⃣  use related lookup for filtering
    list_filter = ("status", "user__city")

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone_number",
    )
    readonly_fields = ("signup_date",)
    formfield_overrides = RICH_TEXT
    autocomplete_fields = ("user",)

    @display(description=_("Name"), ordering="user__first_name")
    def user_fullname(self, obj):
        return obj.user.get_full_name()

    @display(description=_("Email"), ordering="user__email")
    def email(self, obj):
        return obj.user.email

    @display(description=_("City"), ordering="user__city")  # 1️⃣ new helper
    def city_column(self, obj):
        return obj.user.city


# ────────────────────────────────────────────────────────────────
#  Specialty
# ────────────────────────────────────────────────────────────────
@admin.register(m.Specialty)
class SpecialtyAdmin(BaseIEAdmin):
    is_active_badge = bool_badge(
        "is_active",
        true_text="Active",
        false_text="Inactive",
        true_color="success",
        false_color="danger",
    )

    # 3️⃣  include real field so list_editable works
    list_display = ("name", "code", "is_active", "is_active_badge")
    list_editable = ("is_active",)

    list_filter = ("is_active",)
    search_fields = ("name", "code")
    formfield_overrides = RICH_TEXT


@admin.register(m.Mentor)
class MentorAdmin(BaseIEAdmin):
    hire_j = jalali_display("hire_date", label="Hire Date")
    status_badge = choice_badge(
        "status",
        mapping={"active": ("Active", "success"), "inactive": ("Inactive", "danger")},
    )

    @display(header=True, description="Mentor")
    def heading(self, obj):
        initials = "".join(filter(None, (obj.user.first_name[:1], obj.user.last_name[:1])))
        return [obj.user.get_full_name(), obj.user.email, initials]

    list_display = ("heading", "phone", "hire_j", "status_badge")
    list_filter = ("status", "specialties")
    autocomplete_fields = ("specialties",)
    search_fields = ("user__first_name", "user__last_name", "user__email")
    formfield_overrides = RICH_TEXT

    # phone column
    @display(description=_("Phone"), ordering="user__phone_number")
    def phone(self, obj):
        return obj.user.phone_number


# ────────────────────────────────────────────────────────────────
#  Enrolment & mentoring
# ────────────────────────────────────────────────────────────────
class MentorAssignmentInline(TabularInline):
    model = m.MentorAssignment
    extra = 0
    autocomplete_fields = ("mentor",)
    fields = ("mentor", "start_date", "end_date", "reason_for_change")


@admin.register(m.LearnerEnrolment)
class LearnerEnrolmentAdmin(BaseIEAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "active":    ("Active",    "success"),
            "graduated": ("Graduated", "primary"),
            "dropped":   ("Dropped",   "danger"),
            "reserved":  ("Reserved",  "warning"),
        },
    )
    list_display  = ("learner", "learning_path", "enroll_date", "unenroll_date", "status_badge")
    list_filter   = ("status", "learning_path")
    autocomplete_fields = ("learner", "learning_path")
    search_fields = ("learner__user__email", "learning_path__name")
    inlines = (MentorAssignmentInline,)
    formfield_overrides = RICH_TEXT


@admin.register(m.MentorAssignment)
class MentorAssignmentAdmin(BaseIEAdmin):
    list_display = ("enrolment", "mentor", "start_date", "end_date")
    autocomplete_fields = ("enrolment", "mentor")
    list_filter = ("mentor",)
    formfield_overrides = RICH_TEXT
    search_fields = (
        "mentor__user__first_name",
        "mentor__user__last_name",
        "mentor__user__email",
        "enrolment__learner__user__email",
    )


# ────────────────────────────────────────────────────────────────
#  Sessions
# ────────────────────────────────────────────────────────────────
class SessionOccurrenceInline(TabularInline):
    model = m.SessionOccurrence
    extra = 0
    autocomplete_fields = ("template",)
    fields = ("planned_date", "planned_start_time", "planned_end_time", "status_badge")
    readonly_fields = ("status_badge",)
    formfield_overrides = RICH_TEXT

    status_badge = choice_badge(
        "status",
        mapping={
            "scheduled": ("Scheduled", "info"),
            "held": ("Held", "success"),
            "canceled": ("Canceled", "danger"),
        },
    )


@admin.register(m.SessionType)
class SessionTypeAdmin(BaseIEAdmin):
    list_display = ("code", "name_fa", "duration_minutes", "max_participants")
    search_fields = ("code", "name_fa")
    formfield_overrides = RICH_TEXT


@admin.register(m.SessionTemplate)
class SessionTemplateAdmin(BaseIEAdmin):
    status_badge = choice_badge(
        "status",
        mapping={"active": ("Active", "success"), "expired": ("Expired", "danger")},
    )
    list_display = ("learning_path", "mentor_assignment", "session_type", "weekday", "status_badge")
    list_filter = ("weekday", "status", "learning_path")
    autocomplete_fields = ("learning_path", "mentor_assignment", "session_type")
    inlines = (SessionOccurrenceInline,)
    formfield_overrides = RICH_TEXT
    search_fields = (
        "learning_path__name",
        "mentor_assignment__mentor__user__first_name",
        "mentor_assignment__mentor__user__last_name",
        "mentor_assignment__mentor__user__email",
    )


class SessionParticipantInline(TabularInline):
    model = m.SessionParticipant
    extra = 0
    autocomplete_fields = ("learner",)

    # badge callable attached **inside** the class ↓
    attendance_badge = choice_badge(
        "attendance_status",
        mapping={
            "present": ("Present", "success"),
            "absent":  ("Absent",  "danger"),
            "late":    ("Late",    "warning"),
        },
    )

    readonly_fields = ("attendance_badge",)
    fields = ("learner", "guest_name", "attendance_badge")



@admin.register(m.SessionOccurrence)
class SessionOccurrenceAdmin(BaseIEAdmin):
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
    inlines = (SessionParticipantInline,)
    formfield_overrides = RICH_TEXT


# ────────────────────────────────────────────────────────────────
#  Progress & tasks
# ────────────────────────────────────────────────────────────────
class StepExtensionInline(TabularInline):
    model = m.StepExtension
    extra = 0
    autocomplete_fields = ()
    formfield_overrides = RICH_TEXT

    # badge callable attached **inside** the class ↓
    approved_badge = bool_badge(
        "approved_by_mentor",
        true_text="Approved",
        false_text="Pending",
        true_color="success",
        false_color="warning",
    )

    readonly_fields = ("requested_at", "approved_badge")
    fields = ("extended_by_days", "requested_at", "approved_badge", "reason")


@admin.register(m.StepProgress)
class StepProgressAdmin(BaseIEAdmin):
    skipped_badge = bool_badge("skipped", true_text="Skipped", false_text="On Track")
    list_display = ("enrolment", "step", "initial_due_date", "skipped_badge")
    autocomplete_fields = ("enrolment", "step")
    list_filter = ("skipped", "step__learning_path")
    inlines = (StepExtensionInline,)
    formfield_overrides = RICH_TEXT
    search_fields = (
        "enrolment__learner__user__email",
        "step__title",
        "step__learning_path__name",
    )


@admin.register(m.Task)
class TaskAdmin(BaseIEAdmin):
    is_required_badge = bool_badge(
        "is_required",
        true_text="Required",
        false_text="Optional",
        true_color="danger",
        false_color="info",
    )
    list_display = ("title", "step", "order_in_step", "is_required_badge")
    list_filter = ("is_required", "step__learning_path")
    autocomplete_fields = ("step",)
    formfield_overrides = RICH_TEXT
    search_fields = ("title", "step__title", "step__learning_path__name")


class TaskEvaluationInline(TabularInline):
    model = m.TaskEvaluation
    extra = 0
    autocomplete_fields = ("mentor",)
    readonly_fields = ("evaluated_at",)
    formfield_overrides = RICH_TEXT
    fields = ("mentor", "score_numeric", "feedback_text", "evaluated_at")


@admin.register(m.TaskSubmission)
class TaskSubmissionAdmin(BaseIEAdmin):
    submitted_j = jalali_display("submitted_at", label="Submitted")
    list_display = ("step_progress", "submitted_j")
    autocomplete_fields = ("step_progress",)
    inlines = (TaskEvaluationInline,)
    readonly_fields = ("submitted_at",)
    formfield_overrides = RICH_TEXT
    search_fields = ("step_progress__step__title",)


@admin.register(m.SocialPost)
class SocialPostAdmin(BaseIEAdmin):
    posted_j = jalali_display("posted_at", label="Posted")
    list_display = ("platform", "url", "posted_j")
    list_filter = ("platform",)
    search_fields = ("url",)
    autocomplete_fields = ("step_progress",)
    readonly_fields = ("posted_at",)
    formfield_overrides = RICH_TEXT


# ────────────────────────────────────────────────────────────────
#  Subscription plans
# ────────────────────────────────────────────────────────────────
class PlanFeatureInline(TabularInline):
    model = m.PlanFeature
    extra = 0
    autocomplete_fields = ("feature",)
    formfield_overrides = RICH_TEXT


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(BaseIEAdmin):
    is_active_badge = bool_badge(
        "is_active",
        true_text="Active",
        false_text="Inactive",
        true_color="success",
        false_color="danger",
    )
    price_display = display(description="Price")(lambda _, o: intcomma(int(o.price_amount)))
    duration_display = display(description="Duration (d)")(lambda _, o: o.duration_in_days)

    list_display = ("name", "price_display", "duration_display", "is_active_badge")
    list_filter = ("is_active", "duration_in_days")
    search_fields = ("name", "description")
    inlines = (PlanFeatureInline,)
    formfield_overrides = RICH_TEXT

    actions = ("make_active", "make_inactive")

    @admin.action(description="Activate selected plans")
    def make_active(self, _, qs):
        qs.update(is_active=True)

    @admin.action(description="Deactivate selected plans")
    def make_inactive(self, _, qs):
        qs.update(is_active=False)


@admin.register(m.Feature)
class FeatureAdmin(BaseIEAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    formfield_overrides = RICH_TEXT


class FreezeInline(TabularInline):
    model = m.LearnerSubscribePlanFreeze
    extra = 0
    formfield_overrides = RICH_TEXT
    fields = ("start_date", "duration")


@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(BaseIEAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "active":   ("Active",   "success"),   # green
            "freeze":   ("Frozen",   "secondary"), # grey
            "reserved": ("Reserved", "warning"),   # orange
            "expired":  ("Expired",  "danger"),    # red
            "canceled": ("Canceled", "danger"),    # red
        },
    )
    start_j = jalali_display("start_date", label="Start")
    list_display = ("learner_enrolment", "subscription_plan", "start_j", "status_badge")
    list_filter  = ("status", "subscription_plan")
    autocomplete_fields = ("subscription_plan", "learner_enrolment")
    inlines = (FreezeInline,)
    formfield_overrides = RICH_TEXT


# ────────────────────────────────────────────────────────────────
#  Mentor‑group sessions  (NEW block)
# ────────────────────────────────────────────────────────────────
class MentorGroupSessionParticipantInline(TabularInline):
    model = m.MentorGroupSessionParticipant
    extra = 0
    autocomplete_fields = ("learner",)
    readonly_fields = ("joined_at",)
    fields = ("learner", "joined_at")


@admin.register(m.MentorGroupSession)
class MentorGroupSessionAdmin(BaseIEAdmin):
    is_active_badge = bool_badge(
        "is_active",
        true_text="Active",
        false_text="Inactive",
        true_color="success",
        false_color="danger",
    )
    list_display = ("title", "mentor", "start_datetime", "end_datetime", "is_active_badge")
    list_filter = ("is_active", "mentor")
    search_fields = ("title", "mentor__user__first_name", "mentor__user__last_name", "mentor__user__email")
    autocomplete_fields = ("mentor",)
    inlines = (MentorGroupSessionParticipantInline,)
    formfield_overrides = RICH_TEXT

    actions = ("make_active", "make_inactive")

    @admin.action(description="Activate selected sessions")
    def make_active(self, _, qs):
        qs.update(is_active=True)

    @admin.action(description="Deactivate selected sessions")
    def make_inactive(self, _, qs):
        qs.update(is_active=False)
