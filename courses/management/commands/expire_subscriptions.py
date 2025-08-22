from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import LearnerSubscribePlan

class Command(BaseCommand):
    help = "Mark overdue subscriptions as expired and send notifications."

    def handle(self, *args, **opts):
        n = LearnerSubscribePlan.objects.expire_and_notify(at=timezone.now())
        self.stdout.write(self.style.SUCCESS(f"Expired & notified: {n}"))
