from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import formats

from courses.models import (
    TaskSubmission, TaskEvaluation,
    StepExtension, MentorGroupSessionOccurrence,
    MentorGroupSessionParticipant, MentorAssignment,
    LearnerSubscribePlan, LearnerSubscribePlanFreeze
)

from notifications.models import Event, Notification


# -------------------------------------------------------
# Signals to create notification(sms, email and internal)
# -------------------------------------------------------

@receiver(post_save, sender=TaskEvaluation)
def notify_evaluation_added(sender, instance, created, **kwargs):
    if created:
        learner = instance.submission.step_progress.mentor_assignment.enrollment.learner.user
        Notification.objects.create(
            user=learner,
            event=Event.NEW_EVALUATION,
            title="Your task has been evaluated",
            message=f"{instance.mentor.user} evaluated your submission with score {instance.score}/5.",
            send_internal = True
        )


@receiver(post_save, sender=TaskSubmission)
def notify_submission_created(sender, instance, created, **kwargs):
    if created:
        mentor = instance.step_progress.mentor_assignment.mentor.user
        learner = instance.step_progress.mentor_assignment.enrollment.learner.user

        Notification.objects.create(
            user=mentor,
            event=Event.NEW_SUBMISSION,
            title="New task submission",
            message=f"{learner} submitted a new task.",
            send_internal = True
        )


@receiver(post_save, sender=StepExtension)
def notify_extension_requested(sender, instance, created, **kwargs):
    if created:
        mentor = instance.step_progress.mentor_assignment.mentor.user
        learner = instance.step_progress.mentor_assignment.enrollment.learner.user

        Notification.objects.create(
            user=mentor,
            event=Event.EXTENSION_REQUESTED,
            title="Extension requested",
            message=f"{learner} requested a deadline extension.",
            send_internal = True
        )

@receiver(post_save, sender=MentorGroupSessionOccurrence)
def notify_group_session_rescheduled(sender, instance, created, **kwargs):
    if not instance.occurence_datetime_changed:
        return

    session = instance.mentor_group_session
    mentor = session.mentor
    learning_path = session.learning_path

    # all learners assigned to this mentor within this learning path
    mentor_assignments = mentor.assignments.filter(
        enrollment__learning_path=learning_path,
        enrollment__status="active"
    )

    for ma in mentor_assignments:
        user = ma.enrollment.learner.user
        Notification.objects.create(
            user=user,
            event=Event.GROUP_SESSION_RESCHEDULED,
            title="Group session rescheduled",
            message=(
                f"The group session with {mentor.user} has been rescheduled. "
                f"New datetime: {formats.date_format(instance.new_datetime, "m-d H:i") or instance.occurence_datetime}"
            ),
            send_internal = True
        )


@receiver(post_save, sender=MentorGroupSessionParticipant)
def notify_marked_absent(sender, instance, created, **kwargs):
    if not instance.learner_was_present:
        user = instance.mentor_assignment.enrollment.learner.user
        Notification.objects.create(
            user=user,
            event=Event.MARKED_ABSENT,
            title="You were marked absent",
            message="You were marked absent for a group session.",
            send_internal = True
        )


@receiver(post_save, sender=MentorAssignment)
def notify_mentor_assigned(sender, instance, created, **kwargs):
    if created:
        mentor = instance.mentor.user
        learner = instance.enrollment.learner.user

        Notification.objects.create(
            user=mentor,
            event=Event.MENTOR_ASSIGNED,
            title="New learner assigned",
            message=f"You have been assigned to mentor {learner}.",
            send_internal = True
        )

        Notification.objects.create(
            user=learner,
            event=Event.MENTOR_ASSIGNED,
            title="Mentor assigned",
            message=f"{mentor} has been assigned as your mentor.",
            send_internal = True
        )


@receiver(post_save, sender=LearnerSubscribePlan)
def notify_subscription_purchased(sender, instance, created, **kwargs):
    if created:
        user = instance.learner_enrollment.learner.user
        Notification.objects.create(
            user=user,
            event=Event.SUBSCRIPTION_PURCHASED,
            title="Subscription activated",
            message=f"Your subscription to {instance.subscription_plan.name} is now active.",
            send_internal = True
        )


@receiver(post_save, sender=LearnerSubscribePlanFreeze)
def notify_subscription_frozen(sender, instance, created, **kwargs):
    if created:
        user = instance.subscribe_plan.learner_enrollment.learner.user
        Notification.objects.create(
            user=user,
            event=Event.SUBSCRIPTION_FROZEN,
            title="Subscription frozen",
            message=f"Your subscription has been frozen for {instance.duration} days.",
            send_internal = True
        )


def notify_deadline_approaching(user, step_progress):
    Notification.objects.create(
        user=user,
        event=Event.DEADLINE_APPROACHING,
        title="Deadline approaching",
        message=f"Your deadline for step {step_progress.educational_step.title} is near.",
        send_internal = True
    )

def notify_subscription_expiring(plan):
    user = plan.learner_enrollment.learner.user
    Notification.objects.create(
        user=user,
        event=Event.SUBSCRIPTION_EXPIRING,
        title="Subscription expiring soon",
        message="Your subscription will expire soon. Consider renewing.",
        send_internal = True
    )

def notify_subscription_expired(plan):
    user = plan.learner_enrollment.learner.user
    Notification.objects.create(
        user=user,
        event=Event.SUBSCRIPTION_EXPIRED,
        title="Subscription expired",
        message="Your subscription has expired.",
        send_internal = True
    )