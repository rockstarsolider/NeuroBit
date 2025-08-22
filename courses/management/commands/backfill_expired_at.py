from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import LearnerSubscribePlan, SubscribePlanStatus
from django.db import models

class Command(BaseCommand):
    help = "Backfill expired_at := end_datetime where status is expired and expired_at is null."

    def handle(self, *args, **opts):
        qs = LearnerSubscribePlan.objects.filter(
            status=SubscribePlanStatus.EXPIRED, expired_at__isnull=True, end_datetime__isnull=False
        )
        n = qs.update(expired_at=models.F("end_datetime"))
        self.stdout.write(self.style.SUCCESS(f"Backfilled {n} rows."))
