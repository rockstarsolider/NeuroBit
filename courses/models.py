# courses/models.py ― Django 5.2.x
#

# ➋  Enumerations                         │  keep logic tidy
# ➌  Core actors  (Learner, Mentor, …)    │
# ➍  Curriculum   (LearningPath, Step …)  │
# ➎  Enrolment / Mentoring                │
# ➏  Sessions & attendance                │
# ➐  Progress & task workflow             │
# ➑  Subscription plans                   │
# ➒  Mentor‑group sessions  ← new block   │  **added to match ERD**

from datetime import timedelta

from django.core.validators import (
    RegexValidator, MinValueValidator, MaxValueValidator
)
from django.db import models, transaction
from django.db.models import Q, CheckConstraint
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField

from core.utility import phone_re
from pages.templatetags.custom_translation_tags import translate_number
from pages.templatetags.persian_calendar_convertor import convert_to_persian_calendar, format_persian_datetime


# ────────────────────────────────────────────────────────────────
# ➋  ENUMS
# ────────────────────────────────────────────────────────────────
class SubscriptionDurations(models.IntegerChoices):
    ONE_MONTHS = 30, "30 days"
    THREE_MONTHS = 90, "90 days"
    SIX_MONTHS = 180, "180 days"
    NINE_MONTHS = 270, "270 days"
    TWELVE_MONTHS = 360, "360 days"

class ActiveStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class LearnerEnrolmentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    GRADUATED = "graduated", "Graduated"
    DROPPED = "dropped", "Dropped"
    RESERVED = "reserved", "Reserved"


class ResourceType(models.TextChoices):
    VIDEO = "video", "Video"
    DOC = "doc", "Document"
    BOOK = "book", "Book"
    COURSE = "course", "Course"
    PLAYLIST = "playlist", "Playlist"
    ARTICLE = "article", "Article"
    GITHUB_REPOSITORY = "repository", "Repository"
    OTHER = "other", "Other"


class SessionCode(models.TextChoices):
    PRIVATE = "private", "Private"
    PUBLIC = "public", "Public"
    META_PUBLIC = "meta_public", "Meta‑Public"
    META_PRIVATE = "meta_private", "Meta‑Private"


class SessionTemplateStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"


class SessionOccurrenceStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    CANCELED = "canceled", "Canceled"
    HELD = "held", "Held"


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"


class Weekday(models.IntegerChoices):
    MON = 1, "Monday"
    TUE = 2, "Tuesday"
    WED = 3, "Wednesday"
    THU = 4, "Thursday"
    FRI = 5, "Friday"
    SAT = 6, "Saturday"
    SUN = 7, "Sunday"


class SubscribePlanStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    CANCELED = "canceled", "Canceled"
    RESERVED = "reserved", "Reserved"
    FROZEN = "freeze", "Frozen"


# ────────────────────────────────────────────────────────────────
# ➌  CORE ACTORS
# ────────────────────────────────────────────────────────────────
class Specialty(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Mentor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentor_profile")
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    specialties = models.ManyToManyField(Specialty, blank=True, related_name="mentors")
    hire_date = models.DateField(null=True, blank=True, default=timezone.now)
    status = models.CharField(max_length=8, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        ordering = ("user__last_name", "user__first_name")

    def __str__(self):
        return self.user.get_full_name()


class Learner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learner_profile")
    mother_phone = models.CharField(max_length=15, validators=[phone_re], blank=True)
    father_phone = models.CharField(max_length=15, validators=[phone_re], blank=True)
    status = models.CharField(max_length=8, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)
    notes = models.TextField(blank=True, help_text="Any data about the learner.")
    signup_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-signup_date",)

    def __str__(self):
        return self.user.get_full_name()


# ────────────────────────────────────────────────────────────────
# ➍  CURRICULUM
# ────────────────────────────────────────────────────────────────
class LearningPath(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(max_length=7000, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class EducationalStep(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="steps")
    sequence_no = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=7000, blank=True)
    expected_duration_days = models.PositiveSmallIntegerField()
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("learning_path", "sequence_no")
        unique_together = ("learning_path", "sequence_no")

    def __str__(self):
        return f"{self.learning_path} | {self.sequence_no}. {self.title}"


class Resources(models.Model):
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=120)
    type = models.CharField(max_length=12, choices=ResourceType.choices)
    address = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


# ────────────────────────────────────────────────────────────────
# ➎  ENROLMENT & MENTORING
# ────────────────────────────────────────────────────────────────
class LearnerEnrolment(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="enrolments")
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE,related_name="enrolments")
    enroll_date = models.DateTimeField(auto_now_add=True)
    unenroll_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField( 
        max_length=9,
        choices=LearnerEnrolmentStatus.choices,
        default=LearnerEnrolmentStatus.ACTIVE
        )

    class Meta:
        unique_together = ("learner", "learning_path")
        indexes = [models.Index(fields=("learning_path", "enroll_date"))]

    def __str__(self):
        return f"{self.learner} → {self.learning_path}"


class MentorAssignment(models.Model):
    enrolment = models.ForeignKey(LearnerEnrolment, on_delete=models.CASCADE, related_name="mentor_assignments")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="assignments")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    reason_for_change = models.TextField(blank=True)
    # if the learner was pro
    code_review_pro_session_datetime = models.DateTimeField(blank=True, null=True)
    code_review_session_day = models.PositiveSmallIntegerField(choices=Weekday, default=Weekday.SAT)
    code_review_session_time = models.TimeField(default=timezone.now)

    class Meta:
        ordering = ("-start_date",)
        unique_together = ("enrolment", "mentor", "start_date")

    def __str__(self):
        return f"{self.enrolment} ↔ {self.mentor}"


# ────────────────────────────────────────────────────────────────
# ➏  SESSION SCHEDULING
# ────────────────────────────────────────────────────────────────
class SessionType(models.Model):
    code = models.CharField(max_length=12,
                            choices=SessionCode.choices,
                            unique=True)
    name_fa = models.CharField(max_length=32)
    duration_minutes = models.PositiveSmallIntegerField()
    max_participants = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return self.get_code_display()


# ────────────────────────────────────────────────────────────────
# ➐  PROGRESS & TASKS
# ────────────────────────────────────────────────────────────────
class StepProgress(models.Model):
    mentor_assignment = models.ForeignKey(MentorAssignment, on_delete=models.CASCADE, related_name="step_progresses")
    educational_step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="step_progresses")
    skipped = models.BooleanField(default=False, help_text="If True, promise_days must be 0")
    initial_promise_date = models.DateTimeField(auto_now_add=True)
    initial_promise_days = models.PositiveSmallIntegerField(default=1)
    repromise_count = models.PositiveSmallIntegerField(default=0)
    task_completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("mentor_assignment", "educational_step")
        ordering = ("initial_promise_date",)

    def __str__(self):
        return f"{self.mentor_assignment} | {self.educational_step}"


class StepProgressSession(models.Model):
    step_progress = models.ForeignKey(StepProgress, on_delete=models.CASCADE, related_name="step_progress_sessions")
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, related_name="step_progress_sessions")
    datetime = models.DateTimeField(auto_now=True)
    present = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    recorded_meet_link = models.URLField(blank=True, null=True)


class StepExtension(models.Model):
    step_progress = models.ForeignKey(StepProgress, on_delete=models.CASCADE, related_name="extensions")
    extended_by_days = models.PositiveSmallIntegerField(default=0)
    requested_at = models.DateTimeField(default=timezone.now)
    approved_by_mentor = models.BooleanField(default=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-requested_at",)

    def __str__(self):
        return f"{self.extended_by_days} days for {self.step_progress}"


class Task(models.Model):
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    order_in_step = models.PositiveSmallIntegerField()
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ("step", "order_in_step")
        ordering = ("step", "order_in_step")

    def __str__(self):
        return f"{self.step} – {self.title}"


def submissions_upload_to(instance, filename) -> str:  # noqa: D401
    return f"task_submissions/{instance.step_progress_id}/{filename}"


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    step_progress = models.ForeignKey(StepProgress, on_delete=models.CASCADE, related_name="submissions")
    submitted_at = models.DateTimeField(blank=True, null=True)
    artifact_url = models.URLField(max_length=500, blank=True)
    file = models.FileField(upload_to=submissions_upload_to, blank=True)
    report_video_file = models.FileField(upload_to=submissions_upload_to, blank=True)
    report_video_link = models.URLField(max_length=500, blank=True)
    repository = models.URLField(max_length=500, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"Submission #{self.pk} – {self.step_progress}"

class ScoreTaskEvaluation(models.IntegerChoices):
    ONE   =   1, "⭐"
    TWO   =   2, "⭐⭐"
    THREE =   3, "⭐⭐⭐"
    FOUR  =   4, "⭐⭐⭐⭐"
    FIVE  =   5, "⭐⭐⭐⭐⭐"


class TaskEvaluation(models.Model):
    submission = models.ForeignKey(TaskSubmission, on_delete=models.CASCADE, related_name="evaluations")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="evaluations")
    score = models.PositiveSmallIntegerField(
        choices=ScoreTaskEvaluation,
        default=ScoreTaskEvaluation.ONE,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="""
        <b>⚖️Stars will increase if:</b>
        <br>
        1- Completed the task.
        <br>
        2- Task has doc/readme file and is published on the github.
        <br>
        3- Deadline was honored.
        <br>
        4- Learner inform the mentro before he deadline.
        <br>
        5- There is creativity and perfection.
        """
    )
    feedback = models.TextField(max_length=10000, blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("submission", "mentor")
        ordering = ("-evaluated_at",)
        constraints = [
            models.CheckConstraint(
                check=models.Q(score__gte=1,
                               score__lte=5),
                name="valid_score_range",
            )
        ]

    def __str__(self):
        return f"{self.score}/5 by {self.mentor}"


class SocialMedia(models.Model):
    platform = models.CharField(
        max_length=32,
        unique=True,
        help_text="Social-media platform (e.g. Twitter, LinkedIn).",
    )


    class Meta:
        ordering = ("platform",)

    def __str__(self):
        return self.platform


class SocialPost(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="social_posts")
    step_progress = models.ForeignKey(StepProgress, on_delete=models.CASCADE, related_name="social_posts")
    platform = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, related_name="social_posts")
    url = models.URLField(max_length=500,  help_text="The address of the post.", null=True, blank=True)
    posted_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    description = models.TextField(max_length=10000, blank=True)

    datetime_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ("-posted_at",)

    def __str__(self):
        return f"{self.learner} posted on {self.platform} at {self.posted_at}"


# ────────────────────────────────────────────────────────────────
# ➑  SUBSCRIPTION PLANS
# ────────────────────────────────────────────────────────────────
class Feature(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=20, unique=True, help_text="(Basic/Plus/Pro)")
    description = models.TextField(blank=True)
    price_amount = models.PositiveIntegerField(default=0, help_text="Toman")
    duration_in_days = models.PositiveSmallIntegerField(choices=SubscriptionDurations, default=SubscriptionDurations.ONE_MONTHS)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class PlanFeature(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="plan_features")
    feature = models.ManyToManyField(Feature, related_name="feature_plans")

    def __str__(self):
        return f"{self.plan} ↔ {self.feature}"


class LearnerSubscribePlan(models.Model):
    learner_enrolment = models.ForeignKey(LearnerEnrolment, on_delete=models.CASCADE, related_name="learner_subscribe_plans")
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="learner_subscribe_plans")
    start_datetime = models.DateTimeField(blank=False, null=False, default=timezone.now)
    end_datetime = models.DateTimeField(blank=True, null=True)
    discount = models.PositiveSmallIntegerField(
        default=0, 
        validators=[MaxValueValidator(100, r"100 % discount is the maximum allowed value!")],
        help_text=r"% discount (e.g. 10 => 10%)"
        )
    status = models.CharField(max_length=8, choices=SubscribePlanStatus.choices, default=SubscribePlanStatus.ACTIVE)
    final_cost = models.PositiveBigIntegerField(default=0)

    def clean(self):
        if self.start_datetime is None:
            self.start_datetime = timezone.now()

        previous = (
            LearnerSubscribePlan.objects
            .filter(learner_enrolment=self.learner_enrolment)
            .exclude(pk=self.pk)                     # ignore self on update
            .order_by("-start_datetime")
            .first()
        )
        if previous and self.start_datetime <= previous.start_datetime:
            raise ValidationError({
                "start_datetime":
                    f"Start must be **after** "
                    f"{convert_to_persian_calendar(format_persian_datetime(translate_number(previous.start_datetime)))}.",
            })

    # ──────── PERSISTENCE HOOK ────────────────────────
    def save(self, *args, **kwargs):
        # run clean() every time save() is called programmatically
        self.full_clean()

        # ➊  end_datetime
        if self.subscription_plan and self.start_datetime:
            self.end_datetime = (
                self.start_datetime +
                timedelta(days=self.subscription_plan.duration_in_days)
            )

        # ➋  final_cost
        if self.subscription_plan:
            price = self.subscription_plan.price_amount
            self.final_cost = int(price * (100 - self.discount) / 100)

        # ➌  keep the whole thing atomic (especially important if you
        #     add signals that might query inside the same transaction)
        with transaction.atomic():
            super().save(*args, **kwargs)
    
    class Meta:
        ordering = ("-start_datetime",)
        # unique_together = ("subscription_plan", "learner_enrolment", "start_datetime")
        constraints = [
            models.UniqueConstraint(
                fields=("learner_enrolment", "start_datetime"),
                name="unique_start_per_enrolment",
            )
        ]

    def __str__(self):
        return f"{self.learner_enrolment} | {self.subscription_plan}"


class LearnerSubscribePlanFreeze(models.Model):
    subscribe_plan = models.ForeignKey(LearnerSubscribePlan, on_delete=models.CASCADE, related_name="freezes")
    duration = models.PositiveSmallIntegerField(help_text="Freeze duration in days")
    start_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return f"Freeze {self.duration} d from {self.start_date}"


# ────────────────────────────────────────────────────────────────
# ➒  MENTOR‑GROUP SESSIONS  ← **NEW (missing in old file)**
# ────────────────────────────────────────────────────────────────
class MentorGroupSession(models.Model):
    "نوع جلسه و جزئیات آن را مشخص می کند"
    """
    A themed group session that multiple learners can attend.
    One mentor leads each session.
    """
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="group_sessions")
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="group_sessions")
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, related_name="group_sessions")
    suppused_day = models.PositiveSmallIntegerField(choices=Weekday, default=Weekday.SAT)
    suppoused_time = models.TimeField(blank=True, null=True)
    google_meet_link = models.URLField(blank=True, help_text="The link for joining the meeting session.")

    class Meta:
        ordering = ("-suppused_day", "-suppoused_time")

    def __str__(self):
        return f"{self.mentor} - {self.suppused_day}"


class MentorGroupSessionOccurrence(models.Model):
    "جلسه ی برگزار شده با حضور منتور"
    mentor_group_session = models.ForeignKey(MentorGroupSession, on_delete=models.CASCADE, related_name="mentor_group_sessions")
    occurence_datetime = models.DateTimeField(blank=False)
    occurence_datetime_changed = models.BooleanField(default=False, help_text="⚠️If the inital DateTime has been changed then You must turn this on!")
    new_datetime = models.DateTimeField(blank=True, null=True)
    reason_for_change = models.TextField(max_length=10000, blank=True, null=True)
    session_video_record = models.URLField(blank=True, null=True, help_text="Link for downloading the session record.")

    class Meta:
        ordering = ("-occurence_datetime",)
        indexes = [models.Index(fields=("mentor_group_session", "occurence_datetime"))]
        constraints = [
            # data-level guarantee: if changed → new_datetime must be set
            CheckConstraint(
                check=(
                    Q(occurence_datetime_changed=True,  new_datetime__isnull=False) |
                    Q(occurence_datetime_changed=False, new_datetime__isnull=True)
                ),
                name="occurrence_requires_new_datetime_when_changed",
            )
        ]
    
    def __str__(self):
        return f"{self.mentor_group_session} @ {self.occurence_datetime:%Y-%m-%d %H:%M}"

class MentorGroupSessionParticipant(models.Model):
    "مشارکت فراگیران در جلسه گروهی"
    
    mentor_group_session_occurence = models.ForeignKey(MentorGroupSessionOccurrence,on_delete=models.CASCADE, related_name="participants")
    mentor_assignment = models.ForeignKey(MentorAssignment,on_delete=models.CASCADE, related_name="participants")
    learner_was_present = models.BooleanField(default=True, help_text="off -> absent, on -> present.")

    class Meta:
        unique_together = ("mentor_group_session_occurence", "mentor_assignment")

    def __str__(self):
        return f"{self.mentor_assignment} in {self.mentor_group_session_occurence}"
