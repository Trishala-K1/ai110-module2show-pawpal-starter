from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Set up owner
    owner = Owner("Jordan")

    # Create two pets
    biscuit = Pet("Biscuit", "Golden Retriever")
    luna = Pet("Luna", "Cat")
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    today = date.today()

    # Add tasks out of order to demonstrate sorting
    biscuit.add_task(Task("Evening walk",   "18:00", 30, "daily",  "high",   due_date=today))
    biscuit.add_task(Task("Medication",     "08:30",  5, "daily",  "high",   due_date=today))
    biscuit.add_task(Task("Morning walk",   "08:00", 20, "daily",  "high",   due_date=today))
    biscuit.add_task(Task("Lunch feeding",  "12:00", 10, "daily",  "medium", due_date=today))

    # Luna's "Feeding" is at 08:00 — intentional conflict with Biscuit's morning walk
    luna.add_task(Task("Feeding",   "08:00",  5, "daily",  "high",   due_date=today))
    luna.add_task(Task("Grooming",  "14:00", 15, "weekly", "medium", due_date=today))
    luna.add_task(Task("Playtime",  "20:00", 20, "daily",  "low",    due_date=today))

    scheduler = Scheduler(owner)

    # --- Full sorted schedule with conflict warnings ---
    print("=" * 52)
    print(scheduler.format_schedule())
    print("=" * 52)

    # --- Filter by pet ---
    print("\n--- Biscuit's tasks only (sorted) ---")
    biscuit_tasks = scheduler.sort_by_time(scheduler.filter_by_pet("Biscuit"))
    for pet, task in biscuit_tasks:
        print(f"  {task.time} — {task.description} ({task.duration_minutes} min)")

    # --- Complete a daily task and see recurrence ---
    print("\n--- Completing Biscuit's 'Morning walk' (daily) ---")
    morning_walk = next(t for t in biscuit.tasks if t.description == "Morning walk")
    next_task = scheduler.mark_task_complete(biscuit, morning_walk)
    print(f"  Marked complete: {morning_walk.description} | completed={morning_walk.completed}")
    if next_task:
        print(f"  Recurring task created: '{next_task.description}' due {next_task.due_date}")

    # --- Filter by completion status ---
    print("\n--- Pending tasks ---")
    pending = scheduler.sort_by_time(scheduler.filter_by_status(completed=False))
    for pet, task in pending:
        print(f"  [{pet.name}] {task.time} — {task.description}")

    print("\n--- Completed tasks ---")
    done = scheduler.filter_by_status(completed=True)
    for pet, task in done:
        print(f"  [{pet.name}] {task.time} — {task.description} ✓")


if __name__ == "__main__":
    main()
