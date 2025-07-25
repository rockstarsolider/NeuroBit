Below is a **concise “admin‑quick‑start” guide** you can drop into `README.md`.
Follow the order and you’ll never run into missing‑FK errors while entering data.

---

## 0  Prep

```bash
python manage.py createsuperuser   # if you haven’t already
python manage.py runserver
```

Log in at `http://127.0.0.1:8000/admin/` with your superuser.
Everything below happens in the Django‑Unfold admin UI.

---

## 1  One‑time lookup tables (no dependencies)

| Model                 | What to add                                   | Why first?                    |
| --------------------- | --------------------------------------------- | ----------------------------- |
| **Feature**           | e.g. *“Weekly 1‑on‑1”*, *“24 h support”*      | Needed when you define plans. |
| **Subscription Plan** | *Basic / Plus / Pro* (+ price & duration)     | Linked later to learners.     |
| **Session Type**      | *private / public / meta…* (+ FA name/length) | Used by session templates.    |

---

## 2  Build the curriculum

1. **Learning Path**
2. Inside the path → add **Educational Steps**
   *While editing the path you already see the inline form.*
3. Inside each step → add **Tasks** and **Resources**
   *(click the step; both inlines are ready)*

> ✅ At this point the “course skeleton” is complete.

---

## 3  Add your staff & students

| Order | Model       | Notes                               |
| ----- | ----------- | ----------------------------------- |
| 1     | **Mentor**  | Phone, specialties JSON, hire date. |
| 2     | **Learner** | Email must be unique.               |

---

## 4  Enroll learners & bind mentors

1. **Learner Enrolment**
   *Pick learner + learning path + enroll date.*
2. In the enrolment page’s inline → create a **Mentor Assignment**
   *Start date today; leave end date blank.*

---

## 5  Schedule sessions

1. **Session Template**
   *Choose the mentor assignment, learning path & session type; select weekday and Meet link.*
2. Inside the template (or directly in **Session Occurrence**) add calendar entries.
   *Occurrences carry actual dates & times; participants can be added later.*

---

## 6  Track progress

*Optional—skip until the learner reaches a step.*

| Model               | Typical moment                                 |
| ------------------- | ---------------------------------------------- |
| **Step Progress**   | When the learner starts a step (set due date). |
| **Step Extension**  | If they request more time.                     |
| **Task Submission** | When they upload work (files/links).           |
| **Task Evaluation** | Mentor gives a 1‑5 score & feedback.           |
| **Social Post**     | Log Rocket.Chat / LinkedIn proof‑of‑work.      |

All these live under their respective parent objects as inlines, so navigation is quick.

---

## 7  Handle subscriptions

1. From the learner’s enrolment page → add a **Learner Subscribe Plan**
   *Pick the previously created Subscription Plan, set discount if any.*
2. If they freeze their account → open that subscription and add a **Freeze** inline row.

---

## 8  Quick cheat‑sheet (dependencies graph)

```text
Feature ─┐
         ├─> SubscriptionPlan ─┐
         │                     ├─> LearnerSubscribePlan ──┐
SessionType ─┐                 │                         │
             ├─> SessionTemplate ─> SessionOccurrence ─> SessionParticipant
LearningPath ─> EducationalStep ─> Task / Resource
                                 │
                   LearnerEnrolment ─> StepProgress ─> TaskSubmission
                   │          │                       │
                   │          └─> MentorAssignment    └─> TaskEvaluation
                   └─> LearnerSubscribePlan (see 7)
```

Read the arrows as “needs”. If you stick to the top‑to‑bottom order you’ll never hit a blank FK drop‑down.

---

### Tips & tricks

* **Search boxes everywhere** – every model that appears as `autocomplete_fields` supports fast typing rather than long select lists.
* **WYSIWYG editor** – any long text (descriptions, bios, notes) opens Unfold’s rich‑text editor.
* **Inline counts** – list pages show how many children (e.g., steps in a path) at a glance.
* Feel free to deactivate or delete lookup rows later—referential integrity keeps existing data safe.

Happy data‑seeding!
