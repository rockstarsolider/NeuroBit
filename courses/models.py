# models.py
from django.db import models
from django.utils import timezone


# ---------- Utility / Base ----------

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------- Choice Enums (replace with real tables if needed) ----------

class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"
    NA = "N", "Prefer not to say"


class StatusCommon(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    BLOCKED = "blocked", "Blocked"


class EnrollmentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    DROPPED = "dropped", "Dropped"
    PAUSED = "paused", "Paused"


class ResourceType(models.TextChoices):
    VIDEO = "video", "Video"
    ARTICLE = "article", "Article"
    REPO = "repo", "Repository"
    FILE = "file", "File"
    OTHER = "other", "Other"


class Score(models.TextChoices):
    POOR = "poor", "Poor"
    OK = "ok", "OK"
    GOOD = "good", "Good"
    HIGH = "high", "High"


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"


class MentorGroupRole(models.TextChoices):
    PRIMARY = "primary", "Primary"
    ASSISTANT = "assistant", "Assistant"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class StepProgressStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    DONE = "done", "Done"


class SocialPlatform(models.TextChoices):
    ROCKET_CHAT = "rocket_chat", "Rocket.Chat"
    LINKEDIN = "linkedin", "LinkedIn"
    OTHER = "other", "Other"


# ---------- People ----------

class Learner(TimeStampedModel):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.NA)
    country_code = models.CharField(max_length=2, blank=True)  # link to ISO table if needed
    signup_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=StatusCommon.choices, default=StatusCommon.ACTIVE)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Mentor(TimeStampedModel):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    hire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusCommon.choices, default=StatusCommon.ACTIVE)

    specialties = models.ManyToManyField(
        "Specialty",
        through="MentorSpecialty",
        related_name="mentors",
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Specialty(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class MentorSpecialty(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("mentor", "specialty")


class Staff(TimeStampedModel):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    role_code = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=StatusCommon.choices, default=StatusCommon.ACTIVE)

    def __str__(self):
        return self.email


# ---------- Curriculum ----------

class LearningPath(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EducationalStep(TimeStampedModel):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="steps")
    sequence_no = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    expected_duration_days = models.PositiveIntegerField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = ("path", "sequence_no")
        ordering = ["path_id", "sequence_no"]

    def __str__(self):
        return f"{self.path.name} #{self.sequence_no} - {self.title}"


class Resource(TimeStampedModel):
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    url_or_location = models.TextField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Task(TimeStampedModel):
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order_in_step = models.PositiveIntegerField()
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ("step", "order_in_step")
        ordering = ["step_id", "order_in_step"]

    def __str__(self):
        return self.title


# ---------- Enrollments & Groups ----------

class PathEnrollment(TimeStampedModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="path_enrollments")
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="enrollments")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ACTIVE)

    class Meta:
        unique_together = ("learner", "path")

    def __str__(self):
        return f"{self.learner} -> {self.path}"


class MentorPathGroup(TimeStampedModel):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="mentor_groups")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    group_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.group_name or f"Group {self.id} - {self.path.name}"


class MentorPathGroupRole(models.Model):
    mentor_path_group = models.ForeignKey(MentorPathGroup, on_delete=models.CASCADE, related_name="mentor_roles")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="group_roles")
    role = models.CharField(max_length=20, choices=MentorGroupRole.choices, default=MentorGroupRole.PRIMARY)

    class Meta:
        unique_together = ("mentor_path_group", "mentor")


class MentorGroupLearner(TimeStampedModel):
    mentor_path_group = models.ForeignKey(MentorPathGroup, on_delete=models.CASCADE, related_name="learners")
    path_enrollment = models.ForeignKey(PathEnrollment, on_delete=models.CASCADE, related_name="group_memberships")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("mentor_path_group", "path_enrollment")


# ---------- Progress, Extensions & Submissions ----------

class StepProgress(TimeStampedModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="step_progress")
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="progress_records")
    initial_due_date = models.DateField(null=True, blank=True)
    initial_promise_days = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StepProgressStatus.choices, default=StepProgressStatus.NOT_STARTED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("learner", "step")

    def __str__(self):
        return f"{self.learner} - {self.step}"


class StepExtension(TimeStampedModel):
    # Instead of a composite FK, just point to StepProgress
    progress = models.ForeignKey(
        StepProgress,
        on_delete=models.CASCADE,
        related_name="extensions"
    )
    extended_by_days = models.PositiveIntegerField()
    requested_at = models.DateTimeField(default=timezone.now)
    approved_by_mentor = models.BooleanField(default=False)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_at"]

    # Convenient accessors, if you still want them:
    @property
    def learner(self):
        return self.progress.learner

    @property
    def step(self):
        return self.progress.step

    def __str__(self):
        return f"Ext {self.extended_by_days}d for {self.progress}"


class TaskSubmission(TimeStampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="task_submissions")
    submitted_at = models.DateTimeField(default=timezone.now)
    artifact_url_or_file = models.TextField()
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("task", "learner")

    def __str__(self):
        return f"{self.learner} -> {self.task}"


class TaskEvaluation(TimeStampedModel):
    task_submission = models.OneToOneField(TaskSubmission, on_delete=models.CASCADE, related_name="evaluation")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="task_evaluations")
    score = models.CharField(max_length=10, choices=Score.choices)
    evaluated_at = models.DateTimeField(default=timezone.now)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.task_submission} by {self.mentor}"


class VideoSubmission(TimeStampedModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="video_submissions")
    step = models.ForeignKey(EducationalStep, on_delete=models.CASCADE, related_name="video_submissions")
    url_or_file = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.learner} - {self.step}"


class SocialPost(TimeStampedModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="social_posts")
    step = models.ForeignKey(EducationalStep, on_delete=models.SET_NULL, null=True, blank=True, related_name="social_posts")
    platform = models.CharField(max_length=30, choices=SocialPlatform.choices, default=SocialPlatform.OTHER)
    url = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.platform}: {self.url}"


# ---------- Meetings & Attendance ----------

class MeetingType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Session(TimeStampedModel):
    meeting_type = models.ForeignKey(MeetingType, on_delete=models.PROTECT, related_name="sessions")
    mentor_path_group = models.ForeignKey(MentorPathGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")  # for 1:1
    path_enrollment = models.ForeignKey(PathEnrollment, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")  # for 1:1
    step = models.ForeignKey(EducationalStep, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    link = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by_staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_sessions")

    def __str__(self):
        return f"{self.meeting_type.name} @ {self.starts_at}"


class Attendance(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="attendance_records")
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("session", "learner")

    def __str__(self):
        return f"{self.learner} - {self.session} ({self.status})"


# ---------- Subscriptions ----------

class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    price_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency_code = models.CharField(max_length=3)  # or FK to a Currency table
    duration_months = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LearnerSubscription(TimeStampedModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="subscriptions")
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField()
    end_date = models.DateField()
    price_paid = models.DecimalField(max_digits=12, decimal_places=2)
    currency_code = models.CharField(max_length=3)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE)

    def __str__(self):
        return f"{self.learner} -> {self.subscription_plan} ({self.status})"
