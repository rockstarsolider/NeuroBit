from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from courses import models as m

"""
Populate realistic PROGRESS data so you can test the new charts.

What it creates:
  - (If missing) 3 learning paths with ~5 steps each, 3 tasks/step.
  - 4 demo mentors (users auto-created if needed).
  - Enroll ~N learners/path, create MentorAssignment to random mentor.
  - For each learner & step, create StepProgress with:
      * initial_promise_date spread across a window
      * some extensions
      * some completions (task_completion_date)
      * some submissions + evaluations with scores
Usage:
  python manage.py seed_progress --paths Backend Frontend AI \
      --start 2025-05-01 --end 2025-08-24 --per-path 25 --seed 42
"""

DEFAULT_PATHS = ["Backend", "Frontend", "AI"]
DATE_RANGE = ("2025-05-01", "2025-08-24")

class Command(BaseCommand):
    help = "Populate progress/steps/tasks/assignments/submissions/evaluations for analytics testing."

    def add_arguments(self, parser):
        parser.add_argument("--paths", nargs="*", default=DEFAULT_PATHS)
        parser.add_argument("--start", default=DATE_RANGE[0])
        parser.add_argument("--end", default=DATE_RANGE[1])
        parser.add_argument("--per-path", dest="per_path", type=int, default=20)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **opts):
        random.seed(opts["seed"])
        from datetime import datetime
        start_dt = timezone.make_aware(datetime.strptime(opts["start"], "%Y-%m-%d"))
        end_dt = timezone.make_aware(datetime.strptime(opts["end"], "%Y-%m-%d"))

        self.stdout.write(self.style.WARNING("Ensuring learning paths/steps/tasks …"))
        paths = self._ensure_paths(opts["paths"])
        steps_by_lp = {lp.id: self._ensure_steps_and_tasks(lp) for lp in paths}

        self.stdout.write(self.style.WARNING("Ensuring mentors …"))
        mentors = self._ensure_mentors()

        self.stdout.write(self.style.WARNING("Ensuring enrollments + assignments …"))
        learners_by_lp = self._ensure_learners_enrollments(paths, min_per_path=opts["per_path"])
        self._ensure_assignments(learners_by_lp, mentors)

        self.stdout.write(self.style.WARNING("Generating step progresses + submissions …"))
        created_sp, created_sub, created_eval = 0, 0, 0

        with transaction.atomic():
            for lp in paths:
                steps = steps_by_lp[lp.id]
                enrollments = (
                    m.LearnerEnrollment.objects
                    .filter(learning_path=lp)
                    .select_related("learner__user")
                )
                for enr in enrollments:
                    # pick the active assignment (latest)
                    ma = (
                        m.MentorAssignment.objects
                        .filter(enrollment=enr)
                        .order_by("-start_date")
                        .first()
                    )
                    if not ma:
                        continue

                    # for each step, create StepProgress
                    for step in steps:
                        sp = m.StepProgress.objects.create(
                            mentor_assignment=ma,
                            educational_step=step,
                            skipped=False,
                            initial_promise_date=self._random_dt(start_dt, end_dt),
                            initial_promise_days=random.randint(3, 10),
                            repromise_count=random.choice([0, 0, 0, 1, 2]),
                        )
                        created_sp += 1

                        # maybe extensions
                        if random.random() < 0.30:
                            ext_days = random.randint(1, 5)
                            m.StepExtension.objects.create(
                                step_progress=sp,
                                extended_by_days=ext_days,
                                approved_by_mentor=True,
                                reason="Demo extension",
                                requested_at=sp.initial_promise_date + timedelta(days=random.randint(1, 3)),
                            )

                        # maybe submit 1..3 tasks with optional evaluation
                        num_tasks = random.randint(1, 3)
                        tasks = list(step.tasks.all()) or self._ensure_tasks_for_step(step)
                        for t in tasks[:num_tasks]:
                            sub = m.TaskSubmission.objects.create(
                                task=t, step_progress=sp,
                                submitted_at=sp.initial_promise_date + timedelta(days=random.randint(1, 10)),
                                artifact_url="https://example.com/artifact",
                            )
                            created_sub += 1

                            if random.random() < 0.70:  # 70% get evaluated
                                ev = m.TaskEvaluation.objects.create(
                                    submission=sub, mentor=ma.mentor,
                                    score=random.randint(1, 5),
                                    feedback="Looks good 👍",
                                    evaluated_at=sub.submitted_at + timedelta(days=random.randint(0, 2)),
                                )
                                created_eval += 1
                                # infer completion date from evaluation occasionally
                                if random.random() < 0.60 and not sp.task_completion_date:
                                    sp.task_completion_date = ev.evaluated_at
                                    sp.save(update_fields=["task_completion_date"])

                        # maybe explicit completion (if not already set)
                        if not sp.task_completion_date and random.random() < 0.40:
                            sp.task_completion_date = sp.initial_promise_date + timedelta(days=random.randint(2, 14))
                            sp.save(update_fields=["task_completion_date"])

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created_sp} StepProgress, {created_sub} submissions, {created_eval} evaluations."
        ))

    # ---------------- helpers ----------------
    def _ensure_paths(self, names: List[str]) -> List[m.LearningPath]:
        out = []
        for n in names:
            lp, _ = m.LearningPath.objects.get_or_create(name=n, defaults={"description": f"{n} learning path"})
            out.append(lp)
        return out

    def _ensure_steps_and_tasks(self, lp: m.LearningPath):
        steps = list(m.EducationalStep.objects.filter(learning_path=lp).order_by("sequence_no"))
        if not steps:
            for i in range(1, 6):
                step = m.EducationalStep.objects.create(
                    learning_path=lp, sequence_no=i, title=f"Step {i}",
                    description="Demo step", expected_duration_days=random.randint(5, 12), is_mandatory=True
                )
                self._ensure_tasks_for_step(step)
            steps = list(m.EducationalStep.objects.filter(learning_path=lp).order_by("sequence_no"))
        return steps

    def _ensure_tasks_for_step(self, step: m.EducationalStep):
        if step.tasks.count() == 0:
            for idx in range(1, 4):
                m.Task.objects.create(step=step, title=f"Task {idx}", order_in_step=idx, is_required=(idx != 3))
        return list(step.tasks.all())

    def _ensure_mentors(self):
        User = get_user_model()
        mentors = list(m.Mentor.objects.select_related("user")[:4])
        need = max(0, 4 - len(mentors))
        for _ in range(need):
            idx = random.randint(2000, 9999)
            u = User.objects.create_user(
                username=f"mentor_{idx}", first_name="Mentor", last_name=str(idx),
                email=f"mentor{idx}@demo.local", password="demo1234"
            )
            mentors.append(m.Mentor.objects.create(user=u))
        return mentors

    def _ensure_learners_enrollments(self, paths: List[m.LearningPath], min_per_path: int = 20):
        User = get_user_model()
        out = {}
        for lp in paths:
            learners = list(m.Learner.objects.select_related("user")[:min_per_path])
            if len(learners) < min_per_path:
                for _ in range(min_per_path - len(learners)):
                    idx = random.randint(1000, 9999)
                    u = User.objects.create_user(
                        username=f"learner_{idx}", first_name="Learner", last_name=str(idx),
                        email=f"learner{idx}@demo.local", password="demo1234"
                    )
                    # give some birthdates to feed age-based charts if needed
                    try:
                        if hasattr(u, "birthdate"):
                            now = timezone.now().date()
                            years = random.randint(16, 32)
                            u.birthdate = now.replace(year=now.year - years)
                            u.save(update_fields=["birthdate"])
                    except Exception:
                        pass
                    learners.append(m.Learner.objects.create(user=u))
            # enroll each into lp if not already
            for ln in learners:
                m.LearnerEnrollment.objects.get_or_create(learner=ln, learning_path=lp, defaults={})
            out[lp.id] = learners
        return out

    def _ensure_assignments(self, learners_by_lp, mentors: List[m.Mentor]):
        for lp_id, learners in learners_by_lp.items():
            for ln in learners:
                enr = m.LearnerEnrollment.objects.get(learner=ln, learning_path_id=lp_id)
                m.MentorAssignment.objects.get_or_create(
                    enrollment=enr, mentor=random.choice(mentors),
                    defaults={}
                )

    def _random_dt(self, start, end):
        delta = (end - start).total_seconds()
        offset = random.randint(0, int(delta))
        return start + timedelta(seconds=offset)


# python manage.py seed_progress --paths Backend Frontend AI --start 2025-05-01 --end 2025-08-24 --per-path 25 --seed 42