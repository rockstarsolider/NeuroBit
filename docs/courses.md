# 🎓 Courses / LMS Domain

This guide explains how Neurobit models **curricula, learners, progress, submissions, sessions, and billing**—and how you operate all of that in **Django Admin with Unfold + WYSIWYG**.

---

## 📑 Table of Contents

1. [Concept Map](#concept-map)  
2. [Entity Relationship Overview](#entity-relationship-overview)  
3. [Model Deep Dive & Gotchas](#model-deep-dive--gotchas)  
4. [Typical Workflows](#typical-workflows)  
5. [Django Admin (Unfold) Setup](#django-admin-unfold-setup)  
6. [Handy ORM Queries](#handy-orm-queries)  
7. [Schema Extensions (Ideas)](#schema-extensions-ideas)  
8. [Migrations & Constraints](#migrations--constraints)  
9. [Glossary](#glossary)  
10. [Admin Power Tips](#admin-power-tips)

---

## 1. Concept Map

| Concept | Description | Core Model(s) |
|--------|-------------|---------------|
| **Learner** | Student using the platform | `Learner` |
| **Mentor / Staff** | Guides & operators | `Mentor`, `Staff` |
| **Learning Path (LP)** | A curriculum track (e.g. “Full‑Stack Basics”) | `LearningPath` |
| **Step** | A module or lesson within a path | `EducationalStep` |
| **Resource / Task** | Materials & assignments inside a step | `Resource`, `Task` |
| **Enrollment & Groups** | Who is in a path and in which mentor group | `PathEnrollment`, `MentorPathGroup`, `MentorGroupLearner`, `MentorPathGroupRole` |
| **Progress / Extension** | Per-learner step progress + deadline extensions | `StepProgress`, `StepExtension` |
| **Submissions / Evaluations** | Task upload & mentor scoring | `TaskSubmission`, `TaskEvaluation` |
| **Sessions / Attendance** | Meetings (group or 1:1) & who attended | `Session`, `Attendance` |
| **Subscriptions** | Pricing plans & purchases | `SubscriptionPlan`, `LearnerSubscription` |

> 💡 Everything timestamped? Yup—most models inherit `TimeStampedModel` (auto `created_at` / `updated_at`).

---

## 2. Entity Relationship Overview

### Mermaid Diagram

```mermaid
erDiagram

    Learner ||--o{ PathEnrollment : enrolls
    LearningPath ||--o{ EducationalStep : has
    EducationalStep ||--o{ Resource : provides
    EducationalStep ||--o{ Task : contains
    Learner ||--o{ StepProgress : tracks
    StepProgress ||--o{ StepExtension : extends
    Task ||--o{ TaskSubmission : submitted_by
    TaskSubmission ||--|| TaskEvaluation : evaluated_by
    Mentor ||--o{ MentorPathGroupRole : serves_in
    MentorPathGroup ||--o{ MentorPathGroupRole : has_role
    PathEnrollment ||--o{ MentorGroupLearner : joins_group
    MentorPathGroup ||--o{ MentorGroupLearner : contains_learner
    Session ||--o{ Attendance : records
    SubscriptionPlan ||--o{ LearnerSubscription : purchased_by
````

> 🧰 We **avoided composite foreign keys** (Django ORM limitation). For example, `StepExtension` references `StepProgress` directly.

---

## 3. Model Deep Dive & Gotchas

### 3.1 `TimeStampedModel`

* `created_at = auto_now_add=True`
* `updated_at = auto_now=True`
* Declared `abstract = True`, so no separate table—fields land in each concrete model.

### 3.2 `StepProgress` & `StepExtension`

* `StepProgress` is **unique per (`learner`, `step`)**.
* `StepExtension` has `progress = ForeignKey(StepProgress)`. Access related learner/step via properties:

  ```python
  extension.progress.learner
  extension.progress.step
  ```
* Bonus: sorting by `requested_at` is implemented (`ordering = ["-requested_at"]`).

### 3.3 Tasks & Evaluations

* `TaskSubmission` → `TaskEvaluation` is **one-to-one**. If you want multiple evaluations (re-reviews), convert it to a FK and add uniqueness constraints as needed.

### 3.4 Groups & Roles

* `MentorPathGroupRole` stitches mentors to groups with a `PRIMARY`/`ASSISTANT` role field.
* `MentorGroupLearner` joins learners (via their `PathEnrollment`) to mentor groups.

### 3.5 Sessions

* `Session` can reference:

  * a whole group,
  * or specific `mentor` + `path_enrollment` for 1:1s,
  * and optionally a `step`.

---

## 4. Typical Workflows

### 4.1 Build a Curriculum

1. Create **Learning Path**.
2. Add **Educational Steps** (`sequence_no` defines the order).
3. Attach **Resources** and **Tasks** to each step.

### 4.2 Enroll Learners

1. Create a **PathEnrollment** (learner ↔ path).
2. (Optional) Put them in a **MentorPathGroup** using **MentorGroupLearner**.
3. Assign mentors to groups with **MentorPathGroupRole**.

### 4.3 Track Progress

1. Create/Update **StepProgress** when a learner starts a step.
2. Need more time? Add a **StepExtension**.
3. On completion, set `completed_at` and `status = DONE`.

### 4.4 Submit & Evaluate

1. Learner uploads a **TaskSubmission**.
2. Mentor evaluates via **TaskEvaluation** (score + feedback).
3. Query pending evaluations (`evaluation__isnull=True`) to batch-review.

### 4.5 Run Sessions & Attendance

* Create **Session** records (with link/notes).
* Add **Attendance** rows per learner.

### 4.6 Bill Learners

* Define **SubscriptionPlan**s.
* Associate with learner via **LearnerSubscription**, track `status` (`ACTIVE` / `EXPIRED` / `CANCELLED`).

---

## 5. Django Admin (Unfold) Setup

* `BaseAdmin` mixin:

  * Readonly timestamps (`created_at`, `updated_at`).
  * `WysiwygWidget` for **every `TextField`** via `formfield_overrides`.

* Useful inlines in `admin.py`:

  * `ResourceInline`, `TaskInline` under `EducationalStep`
  * `StepExtensionInline` under `StepProgress`
  * `TaskEvaluationInline` under `TaskSubmission`
  * Group/role inlines inside `MentorPathGroup`

> ✨ **Tip:** Use `autocomplete_fields` for heavy FKs and `list_filter` with deep lookups like `"step__path"` to slice data fast.

---

## 6. Handy ORM Queries

```python
# Steps of a path, in order
EducationalStep.objects.filter(path=lp).order_by("sequence_no")

# A learner's progress in a specific path
StepProgress.objects.filter(learner=learner, step__path=lp)

# Pending evaluations
TaskSubmission.objects.filter(evaluation__isnull=True)

# Mentor's sessions in the next 7 days
from django.utils import timezone
now = timezone.now()
Session.objects.filter(
    mentor=mentor,
    starts_at__date__gte=now.date(),
    starts_at__date__lte=(now + timezone.timedelta(days=7)).date(),
)
```

---

## 7. Schema Extensions (Ideas)

* **Multiple Evaluation Rounds**: Replace `OneToOneField` with FK + unique constraint on (`task_submission`, `mentor`, maybe `round_no`).
* **Rubrics**: Add `TaskCriterion` (per task) + `CriterionScore` (per evaluation).
* **Tagging Resources**: Add `Tag` and a M2M to `Resource`.
* **Badges/Achievements**: Track learner milestones with a separate model.

---

## 8. Migrations & Constraints

* Always run `python manage.py makemigrations && migrate` after changes.
* Django **does not support composite foreign keys**. If you truly need them, use raw SQL via `migrations.RunSQL`—but beware portability.

---

## 9. Glossary

* **LP** – Learning Path
* **Step** – `EducationalStep` instance
* **Progress** – `StepProgress` row for a learner-step pair
* **Extension** – Extra days granted (`StepExtension`)
* **Session** – Scheduled meeting/lesson; can be group or 1:1

---

## 10. Admin Power Tips

* **Bulk Actions**: e.g., mark selected `StepProgress` as `DONE`.
* **Readonly Extras**: Add fields like `signup_date` to `readonly_fields`.
* **List Display Links**: Control clickable columns with `list_display_links`.
* **Performance**: Add indexes on frequently filtered fields (Django 3.2+ supports `indexes = [...]` in `Meta`).

---

> *“Ship it clean, keep it DRY, and let Unfold make it pretty.”*