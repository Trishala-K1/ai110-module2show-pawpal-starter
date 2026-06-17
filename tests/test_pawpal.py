import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ── helpers ───────────────────────────────────────────────────────────────────

def make_owner_with_pets():
    """Return an Owner with two pets, each having a few tasks due today."""
    owner = Owner("Jordan")
    today = date.today()

    biscuit = Pet("Biscuit", "dog")
    biscuit.add_task(Task("Evening walk", "18:00", 30, "daily", "high",   due_date=today))
    biscuit.add_task(Task("Medication",   "08:30",  5, "daily", "high",   due_date=today))
    biscuit.add_task(Task("Morning walk", "08:00", 20, "daily", "high",   due_date=today))

    luna = Pet("Luna", "cat")
    luna.add_task(Task("Feeding",  "12:00",  5, "daily",  "high",   due_date=today))
    luna.add_task(Task("Grooming", "14:00", 15, "weekly", "medium", due_date=today))

    owner.add_pet(biscuit)
    owner.add_pet(luna)
    return owner, biscuit, luna, Scheduler(owner)


# ── Phase 2 — basic OOP tests ─────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task("Walk", "09:00", 20, due_date=date.today())
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_add_task_increases_pet_task_count():
    """Adding tasks should increase pet.task_count by one each time."""
    pet = Pet("Luna", "cat")
    assert pet.task_count == 0
    pet.add_task(Task("Feeding", "08:00", 5, due_date=date.today()))
    assert pet.task_count == 1
    pet.add_task(Task("Grooming", "14:00", 15, due_date=date.today()))
    assert pet.task_count == 2


# ── Phase 4 — sorting ─────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() must return tasks in ascending HH:MM order."""
    owner, biscuit, luna, scheduler = make_owner_with_pets()
    sorted_pairs = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_pairs]
    assert times == sorted(times), f"Times not sorted: {times}"


def test_sort_by_time_with_explicit_pairs():
    """Passing an explicit list to sort_by_time() should also work."""
    owner = Owner("Test")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    today = date.today()
    pet.add_task(Task("Z task", "20:00", 10, due_date=today))
    pet.add_task(Task("A task", "06:00", 10, due_date=today))
    pet.add_task(Task("M task", "12:00", 10, due_date=today))
    scheduler = Scheduler(owner)
    sorted_pairs = scheduler.sort_by_time()
    times = [t.time for _, t in sorted_pairs]
    assert times == ["06:00", "12:00", "20:00"]


# ── Phase 4 — recurrence ──────────────────────────────────────────────────────

def test_daily_task_creates_next_day_on_completion():
    """Completing a daily task must create a new task due tomorrow."""
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    today = date.today()
    daily = Task("Daily walk", "08:00", 20, "daily", due_date=today)
    pet.add_task(daily)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(pet, daily)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert not next_task.completed


def test_weekly_task_creates_next_week_on_completion():
    """Completing a weekly task must create a new task due in 7 days."""
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    today = date.today()
    weekly = Task("Bath", "10:00", 30, "weekly", due_date=today)
    pet.add_task(weekly)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(pet, weekly)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_returns_none_on_completion():
    """Completing a one-time task must return None (no recurrence)."""
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    once = Task("Vet visit", "09:00", 60, "once", due_date=date.today())
    pet.add_task(once)
    scheduler = Scheduler(owner)

    result = scheduler.mark_task_complete(pet, once)
    assert result is None


# ── Phase 4 — conflict detection ─────────────────────────────────────────────

def test_conflict_detected_for_same_time():
    """Two tasks at the same time should produce one conflict warning."""
    owner = Owner("Test")
    pet1, pet2 = Pet("Dog", "dog"), Pet("Cat", "cat")
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    today = date.today()
    pet1.add_task(Task("Walk",    "08:00", 20, due_date=today))
    pet2.add_task(Task("Feeding", "08:00",  5, due_date=today))
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_no_conflict_for_different_times():
    """Tasks at different times should produce no conflict warnings."""
    owner = Owner("Test")
    pet = Pet("Solo", "dog")
    owner.add_pet(pet)
    today = date.today()
    pet.add_task(Task("Walk",    "08:00", 20, due_date=today))
    pet.add_task(Task("Feeding", "12:00", 10, due_date=today))
    scheduler = Scheduler(owner)

    assert scheduler.detect_conflicts() == []


# ── Phase 4 — filtering ───────────────────────────────────────────────────────

def test_filter_by_pet_returns_only_that_pets_tasks():
    """filter_by_pet() should return only tasks for the named pet."""
    owner, biscuit, luna, scheduler = make_owner_with_pets()
    result = scheduler.filter_by_pet("Biscuit")
    assert all(pet.name == "Biscuit" for pet, _ in result)
    assert len(result) == 3


def test_filter_by_status_pending():
    """filter_by_status(False) should return only incomplete tasks."""
    owner, biscuit, luna, scheduler = make_owner_with_pets()
    # Complete one task
    biscuit.tasks[0].mark_complete()
    pending = scheduler.filter_by_status(completed=False)
    assert all(not task.completed for _, task in pending)


def test_empty_pet_has_no_tasks():
    """A pet with no tasks added should have task_count == 0."""
    pet = Pet("Ghost", "dog")
    assert pet.task_count == 0
    assert pet.get_tasks() == []
