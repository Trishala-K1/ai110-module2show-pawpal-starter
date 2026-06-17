# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes based on the real-world entities in the scenario:

- **Task** — a Python dataclass representing one care activity. Attributes: `description`, `time` (HH:MM string), `duration_minutes`, `frequency` ("once"/"daily"/"weekly"), `priority`, `completed`, and `due_date`. Responsibilities: track its own state and produce the next occurrence when marked complete.
- **Pet** — a dataclass that holds a pet's name, species, and a list of `Task` objects. It is responsible for owning tasks and reporting its task count.
- **Owner** — a plain class (not a dataclass, because it manages mutable state) that holds a name and a list of `Pet` objects. It provides `get_all_tasks()` as a flat (pet, task) pair list for the Scheduler to consume.
- **Scheduler** — the "brain" class that takes an `Owner` and provides all algorithmic methods: sorting, filtering, conflict detection, recurrence, and formatted output. It never stores task data directly; it always reads from the Owner's pets.

**b. Design changes**

One meaningful change happened during implementation: I initially planned for `Scheduler` to hold a copy of all tasks internally and keep them in sync. During the CLI demo I noticed this created a stale-data problem — marking a task complete in the `Pet` list didn't update the `Scheduler`'s copy. I switched to a read-through design: every `Scheduler` method calls `self.owner.get_all_tasks()` fresh each time, so there is no state to sync. This is slightly less efficient but far safer for a stateful Streamlit app where the owner object persists across reruns.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Time** — tasks are sorted by their `time` field (HH:MM ascending), so the day's plan is always chronological.
- **Completion status** — `filter_by_status()` lets the owner view only pending or only finished tasks.
- **Recurrence** — `frequency` drives whether completing a task creates a successor (daily → +1 day, weekly → +7 days).
- **Conflict** — two tasks at the same exact time slot produce a warning.

I prioritised time-ordering and conflict visibility because those are the most disorienting for a busy owner: seeing tasks in a random order or missing that two things are booked at the same moment.

**b. Tradeoffs**

The conflict detection checks for exact time-slot equality (e.g., both tasks say "08:00"). It does **not** check whether a 30-minute task overlaps with a task starting at "08:15". This is a deliberate simplification: exact-match detection is O(n) with a dictionary and covers the most common error (duplicate entries), while duration-aware overlap detection requires sorting + interval comparison and is harder for a beginner to verify. For a real app the next step would be to model each task as an `[start, start + duration)` interval and flag any overlapping ranges.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code as a pair programmer throughout the project, mostly in chat mode:

- **Design phase**: I described the four entities and asked for a Mermaid UML class diagram. The AI's first draft included a `SchedulerConfig` object I hadn't asked for. I removed it and simplified.
- **Algorithmic phase**: I asked "How do I sort Task objects by a HH:MM string field?" The suggestion to use `sorted(pairs, key=lambda pt: pt[1].time)` was correct and clean. HH:MM strings sort lexicographically the same way as chronologically, so no `datetime` parsing is needed.
- **Testing phase**: I asked for an initial test plan, then reviewed each proposed test against my actual implementation before saving it.
- **Debugging**: When the recurring task appeared in both "Pending" and "Completed" after `mark_task_complete`, I asked the AI to explain why. It correctly identified that the original task (now complete, due today) and the new task (pending, due tomorrow) are two different objects — expected behaviour, not a bug.

**b. Judgment and verification**

The AI initially suggested using `st.experimental_rerun()` in the Streamlit UI to refresh after marking a task complete. I checked the Streamlit docs and found that `st.experimental_rerun()` was deprecated in favour of `st.rerun()` in Streamlit 1.27. I used the modern API instead. This was a useful reminder that AI suggestions reflect training data cutoffs and should always be verified against current documentation.

---

## 4. Testing and Verification

**a. What you tested**

12 tests across four areas:

1. **OOP basics** — `mark_complete()` flips `completed` to `True`; adding a task increments `task_count`.
2. **Sorting** — tasks added in reverse chronological order come back in correct ascending order.
3. **Recurrence** — daily tasks produce a new task due `today + 1 day`; weekly tasks produce `today + 7 days`; one-time tasks return `None`.
4. **Conflict detection** — two tasks at the same time produce exactly one warning containing the time; two tasks at different times produce no warnings.
5. **Filtering** — `filter_by_pet` returns only the named pet's tasks; `filter_by_status(False)` excludes completed tasks; an empty pet has zero tasks.

These tests matter because they cover the three most user-facing failure modes: a schedule that is out of order is confusing, a recurring task that doesn't re-schedule wastes the owner's time, and a conflict that goes undetected leads to missed care.

**b. Confidence**

⭐⭐⭐⭐ (4/5). All 12 tests pass and cover the happy paths and key edge cases. The main untested scenario is duration-aware conflict (a 60-minute task starting at 08:00 overlaps a task at 08:45, but the current detector won't flag it). I would also add tests for `Owner.get_all_tasks()` with zero pets, and for `Scheduler.get_todays_tasks()` when some tasks are due tomorrow.

---

## 5. Reflection

**a. What went well**

The CLI-first workflow paid off. Building and testing `pawpal_system.py` entirely in `main.py` before touching `app.py` meant that when I wired the Streamlit UI, I had high confidence the backend was correct. Every Streamlit bug I hit was a UI bug (session state initialisation, button key conflicts), not a logic bug.

**b. What you would improve**

I would add a `due_date` picker in the Streamlit UI so users can schedule tasks for future dates, not just today. Currently every task added via the UI is assigned `date.today()`. I would also persist the owner data to a JSON file so the schedule survives a page reload — right now a browser refresh wipes the session.

**c. Key takeaway**

The most important thing I learned is that AI is most effective as a *reviewer*, not just a generator. When I attached my finished `pawpal_system.py` and asked "what's missing or fragile here?", the AI spotted that `filter_by_status` would include tasks from all dates (not just today) — which led me to also build `get_todays_tasks()` as a separate, date-filtered method. The AI's best contribution wasn't writing code from scratch; it was asking questions I hadn't thought to ask.
