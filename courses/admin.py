# admin.py
from django.contrib import admin
from django.db import models

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from . import models as m


# ---------- Mixins / Base ----------

class TextWysiwygMixin:
    """Force WysiwygWidget on all TextFields."""
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class TimeStampedReadOnlyMixin:
    """Make created_at / updated_at read-only if present."""
    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        fields = {f.name for f in self.model._meta.get_fields() if hasattr(f, "attname")}
        for f in ("created_at", "updated_at"):
            if f in fields and f not in ro:
                ro.append(f)
        return ro


class BaseAdmin(TimeStampedReadOnlyMixin, TextWysiwygMixin, ModelAdmin):
    pass


# ---------- Inlines ----------

class MentorSpecialtyInline(TabularInline):
    model = m.MentorSpecialty
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class ResourceInline(TabularInline):
    model = m.Resource
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class TaskInline(TabularInline):
    model = m.Task
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class MentorGroupRoleInline(TabularInline):
    model = m.MentorPathGroupRole
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class MentorGroupLearnerInline(TabularInline):
    model = m.MentorGroupLearner
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class AttendanceInline(TabularInline):
    model = m.Attendance
    extra = 1
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class TaskEvaluationInline(StackedInline):
    model = m.TaskEvaluation
    extra = 0
    can_delete = False
    formfield_overrides = TextWysiwygMixin.formfield_overrides


class StepExtensionInline(TabularInline):
    """Extensions shown on a StepProgress page."""
    model = m.StepExtension
    extra = 0
    formfield_overrides = TextWysiwygMixin.formfield_overrides


# ---------- Admin Registrations ----------

@admin.register(m.Learner)
class LearnerAdmin(BaseAdmin):
    list_display = ("first_name", "last_name", "email", "status", "signup_date", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("status", "gender", "signup_date")


@admin.register(m.Mentor)
class MentorAdmin(BaseAdmin):
    list_display = ("first_name", "last_name", "email", "status", "hire_date")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("status",)
    inlines = [MentorSpecialtyInline]


@admin.register(m.Specialty)
class SpecialtyAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(m.MentorSpecialty)
class MentorSpecialtyAdmin(BaseAdmin):
    list_display = ("mentor", "specialty")
    search_fields = ("mentor__first_name", "mentor__last_name", "specialty__name")


@admin.register(m.Staff)
class StaffAdmin(BaseAdmin):
    list_display = ("email", "role_code", "status")
    search_fields = ("email", "role_code")
    list_filter = ("status",)


@admin.register(m.LearningPath)
class LearningPathAdmin(BaseAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(m.EducationalStep)
class EducationalStepAdmin(BaseAdmin):
    list_display = ("path", "sequence_no", "title", "is_mandatory")
    list_filter = ("path", "is_mandatory")
    search_fields = ("title", "path__name")
    inlines = [ResourceInline, TaskInline]


@admin.register(m.Resource)
class ResourceAdmin(BaseAdmin):
    list_display = ("title", "step", "resource_type", "created_at")
    list_filter = ("resource_type", "step__path")
    search_fields = ("title", "description")


@admin.register(m.Task)
class TaskAdmin(BaseAdmin):
    list_display = ("title", "step", "order_in_step", "is_required")
    list_filter = ("is_required", "step__path")
    search_fields = ("title", "description")


@admin.register(m.PathEnrollment)
class PathEnrollmentAdmin(BaseAdmin):
    list_display = ("learner", "path", "status", "start_date", "end_date")
    list_filter = ("status", "path")
    search_fields = ("learner__first_name", "learner__last_name", "path__name")


@admin.register(m.MentorPathGroup)
class MentorPathGroupAdmin(BaseAdmin):
    list_display = ("group_name", "path", "start_date", "end_date")
    list_filter = ("path",)
    search_fields = ("group_name", "path__name")
    inlines = [MentorGroupRoleInline, MentorGroupLearnerInline]


@admin.register(m.MentorPathGroupRole)
class MentorPathGroupRoleAdmin(BaseAdmin):
    list_display = ("mentor_path_group", "mentor", "role")
    list_filter = ("role", "mentor_path_group__path")
    search_fields = ("mentor__first_name", "mentor__last_name", "mentor_path_group__group_name")


@admin.register(m.MentorGroupLearner)
class MentorGroupLearnerAdmin(BaseAdmin):
    list_display = ("mentor_path_group", "path_enrollment", "start_date", "end_date")
    search_fields = ("mentor_path_group__group_name",
                     "path_enrollment__learner__first_name",
                     "path_enrollment__learner__last_name")


@admin.register(m.StepProgress)
class StepProgressAdmin(BaseAdmin):
    list_display = ("learner", "step", "status", "started_at", "completed_at", "created_at")
    list_filter = ("status", "step__path")
    search_fields = ("learner__first_name", "learner__last_name", "step__title")
    inlines = [StepExtensionInline]


@admin.register(m.StepExtension)
class StepExtensionAdmin(BaseAdmin):
    # Show learner/step via callables since model stores only progress FK
    def learner(self, obj):
        return obj.progress.learner
    learner.admin_order_field = "progress__learner__first_name"

    def step(self, obj):
        return obj.progress.step
    step.admin_order_field = "progress__step__title"

    list_display = ("progress", "learner", "step", "extended_by_days",
                    "approved_by_mentor", "requested_at")
    list_filter = ("approved_by_mentor", "progress__step__path")
    search_fields = ("progress__learner__first_name",
                     "progress__learner__last_name",
                     "progress__step__title",
                     "reason")


@admin.register(m.TaskSubmission)
class TaskSubmissionAdmin(BaseAdmin):
    list_display = ("task", "learner", "submitted_at")
    search_fields = ("task__title", "learner__first_name", "learner__last_name", "comment")
    inlines = [TaskEvaluationInline]


@admin.register(m.TaskEvaluation)
class TaskEvaluationAdmin(BaseAdmin):
    list_display = ("task_submission", "mentor", "score", "evaluated_at")
    list_filter = ("score",)
    search_fields = ("mentor__first_name", "mentor__last_name",
                     "task_submission__task__title", "feedback")


@admin.register(m.VideoSubmission)
class VideoSubmissionAdmin(BaseAdmin):
    list_display = ("learner", "step", "submitted_at", "duration_seconds")
    list_filter = ("step__path",)
    search_fields = ("learner__first_name", "learner__last_name", "step__title", "notes")


@admin.register(m.SocialPost)
class SocialPostAdmin(BaseAdmin):
    list_display = ("learner", "platform", "url", "posted_at", "step")
    list_filter = ("platform", "step__path")
    search_fields = ("url", "learner__first_name", "learner__last_name")


@admin.register(m.MeetingType)
class MeetingTypeAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(m.Session)
class SessionAdmin(BaseAdmin):
    list_display = ("meeting_type", "starts_at", "ends_at", "mentor", "mentor_path_group")
    list_filter = ("meeting_type", "mentor_path_group__path", "mentor")
    search_fields = ("notes", "link")
    inlines = [AttendanceInline]


@admin.register(m.Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ("session", "learner", "status", "recorded_at")
    list_filter = ("status", "session__meeting_type")
    search_fields = ("learner__first_name", "learner__last_name", "session__meeting_type__name")


@admin.register(m.SubscriptionPlan)
class SubscriptionPlanAdmin(BaseAdmin):
    list_display = ("name", "price_amount", "currency_code", "duration_months", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(m.LearnerSubscription)
class LearnerSubscriptionAdmin(BaseAdmin):
    list_display = ("learner", "subscription_plan", "status", "start_date", "end_date",
                    "price_paid", "currency_code")
    list_filter = ("status", "subscription_plan")
    search_fields = ("learner__first_name", "learner__last_name", "subscription_plan__name")
