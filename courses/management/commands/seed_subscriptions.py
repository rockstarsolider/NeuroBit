from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from courses import models as m

"""
Seeds realistic subscription data without changing schema.

It will:
1) Ensure SubscriptionPlan rows for Basic/Plus/Pro (price_amount + 30 days).
2) Ensure LearningPath rows exist for given names (default: Backend, Frontend, AI).
3) Ensure each path has enrollments:
   - If there are none, it will create demo Learners (and CustomUsers if needed)
     and enroll them.
4) For each enrollment, generate 0..3 subscription cycles between the given dates,
   picking plans randomly, applying first-month discount per plan:
       Pro 25%, Plus 20%, Basic 15%.

USAGE:
  python manage.py seed_subscriptions --paths Backend Frontend AI \
      --start 2025-05-23 --end 2025-08-23 --seed 123 --per-path 25
"""

PLAN_DEF = {
    "Pro":   {"price_amount": 8_000_000, "duration_in_days": 30, "first_month_disc": 25},
    "Plus":  {"price_amount": 4_000_000, "duration_in_days": 30, "first_month_disc": 20},
    "Basic": {"price_amount": 2_000_000, "duration_in_days": 30, "first_month_disc": 15},
}

DEFAULT_PATHS = ["Backend", "Frontend", "AI"]
DATE_RANGE = ("2025-05-23", "2025-08-23")


def _aware(dt: datetime):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


class Command(BaseCommand):
    help = "Populate sample subscriptions, enrollments, and plans for analytics testing."

    def add_arguments(self, parser):
        parser.add_argument("--paths", nargs="*", default=DEFAULT_PATHS)
        parser.add_argument("--start", default=DATE_RANGE[0], help="YYYY-MM-DD")
        parser.add_argument("--end", default=DATE_RANGE[1], help="YYYY-MM-DD")
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--per-path", dest="per_path", type=int, default=20,
                            help="Minimum enrollments per path (if missing).")

    def handle(self, *args, **opts):
        random.seed(opts["seed"])

        start_bound = _aware(datetime.strptime(opts["start"], "%Y-%m-%d").replace(hour=9, minute=0))
        end_bound = _aware(datetime.strptime(opts["end"], "%Y-%m-%d").replace(hour=18, minute=0))

        self.stdout.write(self.style.WARNING("Ensuring plans exist …"))
        plans = self._ensure_plans()

        self.stdout.write(self.style.WARNING("Ensuring learning paths …"))
        paths = self._ensure_paths(opts["paths"])

        self.stdout.write(self.style.WARNING("Ensuring enrollments …"))
        self._ensure_enrollments(paths, min_per_path=opts["per_path"])

        enrollments = (
            m.LearnerEnrollment.objects
            .filter(learning_path__in=paths)
            .select_related("learner__user", "learning_path")
        )
        if not enrollments.exists():
            self.stdout.write(self.style.ERROR("No LearnerEnrollment rows could be found/created. Aborting."))
            return

        created = 0
        with transaction.atomic():
            for enr in enrollments:
                behavior = random.choices([0, 1, 2, 3], weights=[15, 45, 35, 5], k=1)[0]
                if behavior == 0:
                    continue

                plan_name = random.choice(list(plans.keys()))
                plan = plans[plan_name]

                first_start = self._random_datetime(start_bound, end_bound)
                created += self._create_subscription(enr, plan, first_start, is_first_month=True)

                last_start = first_start
                for _ in range(1, behavior):
                    gap_days = random.randint(0, 5)
                    next_start = last_start + timedelta(days=plan.duration_in_days + gap_days)
                    created += self._create_subscription(enr, plan, next_start, is_first_month=False)
                    last_start = next_start

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} subscription cycles."))

    # ---------------- helpers ----------------

    def _ensure_plans(self) -> Dict[str, m.SubscriptionPlan]:
        out: Dict[str, m.SubscriptionPlan] = {}
        for name, cfg in PLAN_DEF.items():
            plan, _ = m.SubscriptionPlan.objects.get_or_create(
                name=name,
                defaults=dict(
                    price_amount=cfg["price_amount"],
                    duration_in_days=cfg["duration_in_days"],
                    is_active=True,
                ),
            )
            changed = False
            if plan.duration_in_days != cfg["duration_in_days"]:
                plan.duration_in_days = cfg["duration_in_days"]; changed = True
            if getattr(plan, "price_amount", None) != cfg["price_amount"]:
                plan.price_amount = cfg["price_amount"]; changed = True
            if not plan.is_active:
                plan.is_active = True; changed = True
            if changed:
                plan.save(update_fields=["duration_in_days", "price_amount", "is_active"])
            plan.first_month_disc = cfg["first_month_disc"]
            out[name] = plan
        return out

    def _ensure_paths(self, names: List[str]) -> List[m.LearningPath]:
        paths: List[m.LearningPath] = []
        for n in names:
            lp, _ = m.LearningPath.objects.get_or_create(name=n, defaults={"description": f"{n} path"})
            paths.append(lp)
        return paths

    def _ensure_enrollments(self, paths: List[m.LearningPath], min_per_path: int = 20):
        User = get_user_model()

        for lp in paths:
            existing = m.LearnerEnrollment.objects.filter(learning_path=lp).count()
            if existing >= min_per_path:
                continue

            need = min_per_path - existing
            learners_qs = m.Learner.objects.select_related("user")
            learners = list(learners_qs[:need])

            created_learners: List[m.Learner] = []
            if len(learners) < need:
                to_make = need - len(learners)
                for _ in range(to_make):
                    idx = random.randint(1000, 9999)
                    u = User.objects.create_user(
                        username=f"demo{lp.name.lower()}_{idx}",
                        first_name=f"Demo{lp.name[:1]}",
                        last_name=f"User{idx}",
                        password="demo1234",
                    )
                    # Optional demo birthdate for age scatter
                    try:
                        if hasattr(u, "birthdate"):
                            years = random.randint(15, 35)
                            now = timezone.now().date()
                            bd = now.replace(year=now.year - years)
                            u.birthdate = bd
                            u.save(update_fields=["birthdate"])
                    except Exception:
                        pass
                    created_learners.append(m.Learner.objects.create(user=u))
            learners.extend(created_learners)

            for ln in learners:
                m.LearnerEnrollment.objects.get_or_create(
                    learner=ln, learning_path=lp, defaults={}
                )

    def _random_datetime(self, start: datetime, end: datetime) -> datetime:
        total_seconds = max(int((end - start).total_seconds()), 1)
        offset = random.randint(0, total_seconds)
        dt = start + timedelta(seconds=offset)
        hour = random.choice([9, 10, 11, 14, 15, 16, 17])
        return dt.replace(hour=hour, minute=0, second=0, microsecond=0)

    def _create_subscription(self, enrolment: m.LearnerEnrollment, plan: m.SubscriptionPlan,
                             start_dt: datetime, is_first_month: bool) -> int:
        if start_dt > timezone.now() + timedelta(days=60):
            return 0
        discount = plan.first_month_disc if is_first_month else 0
        sub = m.LearnerSubscribePlan(
            learner_enrollment=enrolment,
            subscription_plan=plan,
            start_datetime=start_dt,
            discount=discount,
            status=m.LearnerSubscribePlan.STATUS_ACTIVE,
        )
        sub.save()
        return 1



# python manage.py seed_subscriptions --paths Backend Frontend AI --start 2025-05-23 --end 2025-08-23 --seed 123 --per-path 25
