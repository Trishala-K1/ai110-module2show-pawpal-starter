# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

## 🖥️ Sample Output

Output from `python main.py`:

```
====================================================
Today's Schedule for Jordan's pets:

  Biscuit (Golden Retriever):
    ○ 08:00 — Morning walk (20 min) [high] [daily]

  Luna (Cat):
    ○ 08:00 — Feeding (5 min) [high] [daily]

  Biscuit (Golden Retriever):
    ○ 08:30 — Medication (5 min) [high] [daily]
    ○ 12:00 — Lunch feeding (10 min) [medium] [daily]

  Luna (Cat):
    ○ 14:00 — Grooming (15 min) [medium] [weekly]

  Biscuit (Golden Retriever):
    ○ 18:00 — Evening walk (30 min) [high] [daily]

  Luna (Cat):
    ○ 20:00 — Playtime (20 min) [low] [daily]

  ⚠️  Conflicts detected:
    • Conflict at 08:00: 'Morning walk' (Biscuit), 'Feeding' (Luna)
====================================================

--- Biscuit's tasks only (sorted) ---
  08:00 — Morning walk (20 min)
  08:30 — Medication (5 min)
  12:00 — Lunch feeding (10 min)
  18:00 — Evening walk (30 min)

--- Completing Biscuit's 'Morning walk' (daily) ---
  Marked complete: Morning walk | completed=True
  Recurring task created: 'Morning walk' due 2026-06-18

--- Pending tasks ---
  [Biscuit] 08:00 — Morning walk
  [Luna] 08:00 — Feeding
  [Biscuit] 08:30 — Medication
  [Biscuit] 12:00 — Lunch feeding
  [Luna] 14:00 — Grooming
  [Biscuit] 18:00 — Evening walk
  [Luna] 20:00 — Playtime

--- Completed tasks ---
  [Biscuit] 08:00 — Morning walk ✓
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/ -v
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0
collected 12 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  8%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 16%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 25%]
tests/test_pawpal.py::test_sort_by_time_with_explicit_pairs PASSED       [ 33%]
tests/test_pawpal.py::test_daily_task_creates_next_day_on_completion PASSED [ 41%]
tests/test_pawpal.py::test_weekly_task_creates_next_week_on_completion PASSED [ 50%]
tests/test_pawpal.py::test_once_task_returns_none_on_completion PASSED   [ 58%]
tests/test_pawpal.py::test_conflict_detected_for_same_time PASSED        [ 66%]
tests/test_pawpal.py::test_no_conflict_for_different_times PASSED        [ 75%]
tests/test_pawpal.py::test_filter_by_pet_returns_only_that_pets_tasks PASSED [ 83%]
tests/test_pawpal.py::test_filter_by_status_pending PASSED               [ 91%]
tests/test_pawpal.py::test_empty_pet_has_no_tasks PASSED                 [100%]

============================== 12 passed in 0.02s ==============================
```

**Confidence Level: ⭐⭐⭐⭐** (4/5)

The 12 tests cover all core behaviours — sorting, recurrence (daily and weekly), conflict detection, and filtering. The main gap is duration-aware overlap: currently two tasks at "08:00" conflict even if they last only 5 minutes each and never truly overlap. A future test suite would model time windows to catch only genuine overlaps.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting by time | `Scheduler.sort_by_time()` | Uses Python `sorted()` with a lambda key on the HH:MM string |
| Filter by pet | `Scheduler.filter_by_pet()` | Case-insensitive name match |
| Filter by completion status | `Scheduler.filter_by_status()` | Pass `completed=True` or `False` |
| Conflict detection | `Scheduler.detect_conflicts()` | Flags tasks sharing an exact time slot; returns human-readable warning strings |
| Recurring tasks | `Task.next_occurrence()` + `Scheduler.mark_task_complete()` | Completing a daily/weekly task auto-creates the next occurrence using `timedelta` |

## 📸 Demo Walkthrough

1. **Set your name** — Enter your name in the sidebar and click **Set Owner**. This creates an `Owner` object stored in `st.session_state` so data persists across Streamlit reruns.

2. **Add pets** — Use the sidebar form to add one or more pets (name + species). Each creates a `Pet` object attached to the owner.

3. **Add tasks** — In the right panel, select a pet, fill in description, time (HH:MM), duration, frequency (once/daily/weekly), and priority, then click **Add Task**. The task is stored as a `Task` dataclass on the pet.

4. **View today's schedule** — The left panel calls `Scheduler.get_schedule()` to show today's tasks sorted chronologically. Any time-slot conflicts appear as orange warning banners above the list.

5. **Mark tasks complete** — Click **Done ✓** on any pending task. If it's a daily or weekly task, `Scheduler.mark_task_complete()` automatically schedules the next occurrence using Python's `timedelta`.

6. **Filter tasks** — The filter panel on the right lets you narrow the task list by pet name and/or completion status using `Scheduler.filter_by_pet()` and `Scheduler.filter_by_status()`. Results are sorted and displayed in a table.

**Key Scheduler behaviours demonstrated:**
- Sorting: tasks always appear in HH:MM ascending order regardless of insertion order
- Conflict warnings: two tasks at the same time slot trigger a `st.warning()` banner
- Recurrence: completing a daily task creates a new task for tomorrow without manual re-entry
