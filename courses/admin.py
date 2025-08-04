# courses/admin.py  – Django 5.2 • Unfold 0.24 • import‑export 4.x
from __future__ import annotations

from datetime import date as _d, datetime as _dt, time as _t, timezone as _tz

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField 

from import_export.admin import ImportExportModelAdmin

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget, ArrayWidget
from unfold.contrib.import_export.forms import ImportForm, ExportForm
from unfold.decorators import display

from pages.templatetags.custom_translation_tags import translate_number
from pages.templatetags.persian_calendar_convertor import (
    convert_to_persian_calendar,
    format_persian_datetime,
)

from . import models as m

# ════════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════════
def _jalali(val):
    if isinstance(val, _d) and not isinstance(val, _dt):
        val = _dt.combine(val, _t.min, tzinfo=_tz.utc)
    return format_persian_datetime(convert_to_persian_calendar(val))


def jalali_display(attr="created_at", *, label=None):
    label = label or attr.replace("_", " ").title()

    @display(description=label)
    def _fn(self, obj):
        v = getattr(obj, attr)
        return "-" if not v else format_html("<b dir='rtl'>{}</b>", translate_number(_jalali(v)))

    _fn.__name__ = f"{attr}_jalali"
    return _fn


def bool_badge(attr, *, true="Yes", false="No",
               t_color="success", f_color="danger", desc="Status"):
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


# ════════════════════════════════════════════════════════════════
#  Base mix‑in
# ════════════════════════════════════════════════════════════════
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


# ════════════════════════════════════════════════════════════════
#  CURRICULUM
# ════════════════════════════════════════════════════════════════
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
    # inlines = (EducationalStepInline,)


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


# ════════════════════════════════════════════════════════════════
#  PEOPLE
# ════════════════════════════════════════════════════════════════
@admin.register(m.Specialty)
class SpecialtyAdmin(BaseAdmin):
    active_badge = bool_badge("is_active")
    list_display = ("name", "code", "active_badge")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(m.Mentor)
class MentorAdmin(BaseAdmin):
    hire_j = jalali_display("hire_date", label="Hire date")
    status_badge = bool_badge("status", true="Active", false="Inactive")

    @display(header=True, description=_("Mentor"))
    def heading(self, obj):
        initials = "".join([obj.user.first_name[:1], obj.user.last_name[:1]])
        return [obj.user.get_full_name(), obj.user.email, initials]

    list_display = ("heading", "hire_j", "status_badge")
    list_filter = ("status", "specialties")
    autocomplete_fields = ("user", "specialties",)
    search_fields = ("user__first_name", "user__last_name", "user__email")


@admin.register(m.Learner)
class LearnerAdmin(BaseAdmin):
    status_badge = bool_badge("status", true="Active", false="Inactive")
    list_display = ("user", "status_badge")
    search_fields = ("user__first_name", "user__last_name", "user__email")
    autocomplete_fields = ("user",)


# ════════════════════════════════════════════════════════════════
#  ENROLMENT & MENTORING
# ════════════════════════════════════════════════════════════════
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


@admin.register(m.LearnerEnrolment)
class LearnerEnrolmentAdmin(BaseAdmin):
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
    # inlines = (MentorAssignmentInline,)


@admin.register(m.MentorAssignment)
class MentorAssignmentAdmin(BaseAdmin):
    list_display = ("enrolment", "mentor", "start_date", "end_date")
    autocomplete_fields = ("enrolment", "mentor")
    list_filter = ("mentor",)
    search_fields = (
        "mentor__user__first_name",
        "mentor__user__last_name",
        "mentor__user__email",
        "enrolment__learner__user__email",
    )

# ════════════════════════════════════════════════════════════════
#  PROGRESS & TASKS
# ════════════════════════════════════════════════════════════════
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
    autocomplete_fields = ("step_progress", "session_type",)
    # list_select_related = ("step_progress", "session_type",)
    search_fields = (
        "step_progress",
        "session_type",
    )

#inline -> StepProgress
# class StepProgressSessionInline(TabularInline):
    # ...


@admin.register(m.StepProgress)
class StepProgressAdmin(BaseAdmin):
    skipped_badge = bool_badge("skipped", true="Skipped", false="On track")
    list_display = ("mentor_assignment", "educational_step", "skipped_badge")
    autocomplete_fields = ("mentor_assignment", "educational_step")
    list_filter = ("skipped", "educational_step__learning_path")
    inlines = (StepExtensionInline, )
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
    search_fields = (
        "task__title",
        "step_progress__educational_step__title",
    )


@admin.register(m.TaskEvaluation)
class TaskEvaluationAdmin(BaseAdmin):
    submitted_j = jalali_display("evaluated_at", label="evaluated_at")

    list_display = (
        "submission",
        "mentor",
        "score",
        "feedback",
    )
    autocomplete_fields = ("mentor", "submission")
    search_fields = (
        "submission__task__title"
        "mentor__user",
    )


@admin.register(m.SocialMedia)
class SocialMediaAdmin(BaseAdmin):
    list_display = ("platform",)
    search_fields = ("platform",)


@admin.register(m.SocialPost)
class SocialPostAdmin(BaseAdmin):
    posted_j = jalali_display("posted_at", label="Posted")
    
    @display(description="Platforms")
    def platforms_disp(self, obj):
        return ", ".join(obj.platform.values_list("platform", flat=True))
    
    list_display = ("platforms_disp", "learner", "step_progress", "posted_j")
    list_filter = ("platform",)
    autocomplete_fields = ("learner", "step_progress", "platform")
    search_fields = (
        "learner__user__email",
        "step_progress__educational_step__title",
        "urls",
    )


# ════════════════════════════════════════════════════════════════
#  SUBSCRIPTIONS
# ════════════════════════════════════════════════════════════════
class PlanFeatureInline(TabularInline):
    model = m.PlanFeature
    extra = 0
    autocomplete_fields = ("feature",)
    fields = ("feature",)


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(BaseAdmin):
    active_badge = bool_badge("is_active")
    price_disp = display(description=_("Price (T)"))(lambda _, o: intcomma(o.price_amount))
    dur_disp = display(description=_("Duration (d)"))(lambda _, o: o.duration_in_days)

    list_display = ("name", "price_disp", "dur_disp", "active_badge")
    list_filter = ("is_active", "duration_in_days")
    inlines = (PlanFeatureInline,)
    search_fields = ("name",)


@admin.register(m.Feature)
class FeatureAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class FreezeInline(TabularInline):
    model = m.LearnerSubscribePlanFreeze
    extra = 0
    fields = ("duration",)


@admin.register(m.LearnerSubscribePlan)
class LearnerSubscribePlanAdmin(BaseAdmin):
    status_badge = choice_badge(
        "status",
        mapping={
            "active": ("Active", "success"),
            "freeze": ("Frozen", "secondary"),
            "reserved": ("Reserved", "warning"),
            "expired": ("Expired", "danger"),
            "canceled": ("Canceled", "danger"),
        },
        desc="Status",
    )
    start_j = jalali_display("start_datetime", label="Start")
    end_j   = jalali_display("end_datetime",   label="End")

    # formatted money / percent columns
    @display(description=_("Disc. %"))
    def discount_disp(self, obj):
        return f"{obj.discount} %"

    @display(description=_("Final cost (T)"))
    def cost_disp(self, obj):
        return intcomma(obj.final_cost)

    list_display = (
        "learner_enrolment",
        "subscription_plan",
        "start_j",
        "end_j",
        "discount_disp",
        "cost_disp",
        "status_badge",
    )

    list_filter = ("status", "subscription_plan", "discount")
    search_fields = (
        "learner_enrolment__learner__user__email",
        "subscription_plan__name",
    )

    autocomplete_fields = ("subscription_plan", "learner_enrolment")
    inlines = (FreezeInline,)

    # Prevent manual tampering with system-calculated values
    readonly_fields = ("end_datetime", "final_cost")

    # Nice, compact field layout
    fieldsets = (
        (None, {
            "fields": (
                ("learner_enrolment", "subscription_plan"),
                ("start_datetime", "end_datetime"),
                ("discount", "final_cost"),
                "status",
            )
        }),
    )

# ════════════════════════════════════════════════════════════════
#  MENTOR GROUP SESSIONS
# ════════════════════════════════════════════════════════════════
@admin.register(m.MentorGroupSessionParticipant)
class MentorGroupSessionParticipantAdmin(BaseAdmin):
    list_display = (
        "mentor_group_session_occurence",
        "mentor_assignment",
        "learner_was_present",
    )
    list_filter = ("learner_was_present",)
    autocomplete_fields = ("mentor_group_session_occurence", "mentor_assignment",)
    search_fields = ("mentor_assignment",)
    list_select_related = ("mentor_group_session_occurence", "mentor_assignment" ,)


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
        "reason_for_change",
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
    list_select_related = ("mentor_group_session" ,)
    inlines = (MGSParticipantInline,)
    # 🔑  Unfold magic:
    conditional_fields = {
        # show only when the checkbox is ticked
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
    search_fields = ("mentor",)
    

