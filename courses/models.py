# core/models.py  – Django 5.2.4
#
# A faithful, uncluttered implementation of the data‑model you described.
# • No external packages required.
# • Uses Django’s TextChoices / IntegerChoices for all enums.
# • Adds the minimum sensible constraints (unique_together, check, indexes).
# • Every FK has an explicit `related_name` for clear, self‑documenting queries.
# • Field names are snake_case and line‑wrapped ≤ 88 cols (PEP 8).

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


# --------------------------------------------------------------------------- #
#  Enumerations
# --------------------------------------------------------------------------- #
class ActiveStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    UNDISCLOSED = "na", "Prefer not to say"


class ResourceType(models.TextChoices):
    VIDEO = "video", "Video"
    ARTICLE = "article", "Article"
    REPO = "repo", "Repository"
    OTHER = "other", "Other"


class SessionCode(models.TextChoices):
    PRIVATE = "private", "Private"
    PUBLIC = "public", "Public"
    META_PUBLIC = "meta_public", "Meta Public"
    META_PRIVATE = "meta_private", "Meta Private"


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


# --------------------------------------------------------------------------- #
#  Core actors
# --------------------------------------------------------------------------- #
class Learner(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=12, choices=Gender.choices, default=Gender.UNDISCLOSED
    )
    country = models.CharField(max_length=2, help_text="ISO‑3166‑1 alpha‑2 code")
    signup_date = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.CharField(
        max_length=8, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-signup_date",)
        verbose_name_plural = "Learners"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Mentor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    specialties = models.JSONField(default=list, blank=True)
    hire_date = models.DateField()
    status = models.CharField(
        max_length=8, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE
    )

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


# --------------------------------------------------------------------------- #
#  Curriculum & resources
# --------------------------------------------------------------------------- #
class LearningPath(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class EducationalStep(models.Model):
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="steps"
    )
    sequence_no = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    expected_duration_days = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ("learning_path", "sequence_no")
        unique_together = ("learning_path", "sequence_no")

    def __str__(self) -> str:
        return f"{self.learning_path.name} | {self.sequence_no}. {self.title}"


class Resource(models.Model):
    step = models.ForeignKey(
        EducationalStep, on_delete=models.CASCADE, related_name="resources"
    )
    title = models.CharField(max_length=120)
    type = models.CharField(max_length=12, choices=ResourceType.choices)
    url_or_location = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.get_type_display()})"


# --------------------------------------------------------------------------- #
#  Enrolment & mentoring
# --------------------------------------------------------------------------- #
class LearnerEnrolment(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="enrolments"
    )
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="enrolments"
    )
    enroll_date = models.DateField(default=timezone.now)
    unenroll_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("learner", "learning_path")
        indexes = [
            models.Index(fields=("learning_path", "enroll_date")),
        ]

    def __str__(self) -> str:
        return f"{self.learner} → {self.learning_path}"


class MentorAssignment(models.Model):
    enrolment = models.ForeignKey(
        LearnerEnrolment, on_delete=models.CASCADE, related_name="mentor_assignments"
    )
    mentor = models.ForeignKey(
        Mentor, on_delete=models.CASCADE, related_name="assignments"
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    reason_for_change = models.TextField(blank=True)

    class Meta:
        ordering = ("-start_date",)
        unique_together = ("enrolment", "mentor", "start_date")

    def __str__(self) -> str:
        return f"{self.enrolment} ↔ {self.mentor}"


# --------------------------------------------------------------------------- #
#  Session scheduling
# --------------------------------------------------------------------------- #
class SessionType(models.Model):
    code = models.CharField(max_length=12, choices=SessionCode.choices, unique=True)
    name_fa = models.CharField(max_length=32)
    duration_minutes = models.PositiveSmallIntegerField()
    max_participants = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return self.get_code_display()


class SessionTemplate(models.Model):
    mentor_assignment = models.ForeignKey(
        MentorAssignment, on_delete=models.CASCADE, related_name="session_templates"
    )
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="session_templates"
    )
    session_type = models.ForeignKey(
        SessionType, on_delete=models.CASCADE, related_name="templates"
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    active_from = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=8,
        choices=SessionTemplateStatus.choices,
        default=SessionTemplateStatus.ACTIVE,
    )
    google_meet_link = models.URLField(max_length=500)

    class Meta:
        ordering = ("weekday", "active_from")

    def __str__(self) -> str:
        return (
            f"{self.learning_path} – {self.get_weekday_display()} – "
            f"{self.session_type.get_code_display()}"
        )


class SessionOccurrence(models.Model):
    template = models.ForeignKey(
        SessionTemplate, on_delete=models.CASCADE, related_name="occurrences"
    )
    planned_date = models.DateField()
    planned_start_time = models.TimeField()
    planned_end_time = models.TimeField()
    actual_start_time = models.TimeField(null=True, blank=True)
    actual_end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=SessionOccurrenceStatus.choices,
        default=SessionOccurrenceStatus.SCHEDULED,
    )
    recorded_meet_link = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-planned_date", "planned_start_time")
        unique_together = ("template", "planned_date", "planned_start_time")

    def __str__(self) -> str:
        return f"{self.template} – {self.planned_date}"


class SessionParticipant(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="session_participations"
    )
    occurrence = models.ForeignKey(
        SessionOccurrence, on_delete=models.CASCADE, related_name="participants"
    )
    guest_name = models.CharField(max_length=120, blank=True)
    attendance_status = models.CharField(
        max_length=8,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.ABSENT,
    )

    class Meta:
        unique_together = ("learner", "occurrence")

    def __str__(self) -> str:
        return f"{self.learner} @ {self.occurrence}"


# --------------------------------------------------------------------------- #
#  Progress & tasks
# --------------------------------------------------------------------------- #
class StepProgress(models.Model):
    enrolment = models.ForeignKey(
        LearnerEnrolment, on_delete=models.CASCADE, related_name="step_progresses"
    )
    step = models.ForeignKey(
        EducationalStep, on_delete=models.CASCADE, related_name="progresses"
    )
    initial_due_date = models.DateField()
    initial_promise_days = models.PositiveSmallIntegerField()
    skipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ("enrolment", "step")
        ordering = ("initial_due_date",)

    def __str__(self) -> str:
        return f"{self.enrolment} | {self.step}"


class StepExtension(models.Model):
    step_progress = models.ForeignKey(
        StepProgress, on_delete=models.CASCADE, related_name="extensions"
    )
    extended_by_days = models.PositiveSmallIntegerField()
    requested_at = models.DateTimeField(default=timezone.now)
    approved_by_mentor = models.BooleanField(default=False)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-requested_at",)

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return f"{self.step} – {self.title}"


def submissions_upload_to(instance, filename) -> str:  # noqa: D401
    """Upload path:  task_submissions/<step_progress_id>/<filename>"""
    return f"task_submissions/{instance.step_progress_id}/{filename}"


class TaskSubmission(models.Model):
    step_progress = models.ForeignKey(
        StepProgress, on_delete=models.CASCADE, related_name="submissions"
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    artifact_url = models.URLField(max_length=500, blank=True)
    file = models.FileField(upload_to=submissions_upload_to, blank=True)
    report_video_file = models.FileField(
        upload_to=submissions_upload_to, blank=True, help_text="Optional video"
    )
    report_video_link = models.URLField(max_length=500, blank=True)
    repository = models.URLField(max_length=500, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self) -> str:
        return f"Submission #{self.pk} – {self.step_progress}"


class TaskEvaluation(models.Model):
    submission = models.ForeignKey(
        TaskSubmission, on_delete=models.CASCADE, related_name="evaluations"
    )
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="evaluations")
    score_numeric = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback_text = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("submission", "mentor")
        ordering = ("-evaluated_at",)
        constraints = [
            models.CheckConstraint(
                check=models.Q(score_numeric__gte=1, score_numeric__lte=5),
                name="valid_score_range",
            )
        ]

    def __str__(self) -> str:
        return f"{self.score_numeric}/5 by {self.mentor}"


class SocialPost(models.Model):
    step_progress = models.ForeignKey(
        StepProgress, on_delete=models.CASCADE, related_name="social_posts"
    )
    platform = models.CharField(max_length=32)
    url = models.URLField(max_length=500)
    posted_at = models.DateTimeField()

    class Meta:
        ordering = ("-posted_at",)

    def __str__(self) -> str:
        return f"{self.platform} – {self.url}"


# --------------------------------------------------------------------------- #
#  Subscription plans
# --------------------------------------------------------------------------- #
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_days = models.PositiveSmallIntegerField(
        choices=((30, "30 days"), (90, "90 days"), (120, "120 days"))
    )
    is_active = models.BooleanField(default=True)

    features = models.ManyToManyField(
        "Feature", through="PlanFeature", related_name="plans"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class PlanFeature(models.Model):
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name="plan_features"
    )
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="feature_plans"
    )

    class Meta:
        unique_together = ("plan", "feature")

    def __str__(self) -> str:
        return f"{self.plan} ↔ {self.feature}"


class LearnerSubscribePlan(models.Model):
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name="learner_plans"
    )
    learner_enrolment = models.ForeignKey(
        LearnerEnrolment, on_delete=models.CASCADE, related_name="subscribe_plans"
    )
    start_date = models.DateField(default=timezone.now)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="% discount (e.g., 10.00 = 10%)",
        default=0,
    )
    duration_in_days = models.PositiveSmallIntegerField(
        choices=((30, "30 days"), (90, "90 days"), (120, "120 days"))
    )
    status = models.CharField(
        max_length=8,
        choices=SubscribePlanStatus.choices,
        default=SubscribePlanStatus.ACTIVE,
    )

    class Meta:
        ordering = ("-start_date",)
        unique_together = ("subscription_plan", "learner_enrolment", "start_date")

    def __str__(self) -> str:
        return f"{self.learner_enrolment} | {self.subscription_plan}"


class LearnerSubscribePlanFreeze(models.Model):
    subscribe_plan = models.ForeignKey(
        LearnerSubscribePlan, on_delete=models.CASCADE, related_name="freezes"
    )
    start_date = models.DateField()
    duration = models.PositiveSmallIntegerField(help_text="Freeze duration in days")

    class Meta:
        ordering = ("-start_date",)

    def __str__(self) -> str:
        return f"Freeze {self.duration} d from {self.start_date} on {self.subscribe_plan}"
