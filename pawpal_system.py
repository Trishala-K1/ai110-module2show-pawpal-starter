from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """A single pet care activity."""
    description: str
    time: str  # "HH:MM" 24-hour format
    duration_minutes: int
    frequency: str = "once"   # "once" | "daily" | "weekly"
    priority: str = "medium"  # "low" | "medium" | "high"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next occurrence if recurring, else None."""
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                priority=self.priority,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                priority=self.priority,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None


@dataclass
class Pet:
    """A pet with a name, species, and collection of care tasks."""
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return all tasks assigned to this pet."""
        return self.tasks

    @property
    def task_count(self) -> int:
        """Number of tasks currently assigned to this pet."""
        return len(self.tasks)


class Owner:
    """Manages a collection of pets and provides aggregated task access."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Return (pet, task) pairs for every task across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """Retrieves, sorts, filters, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_todays_tasks(self) -> list:
        """Return all (pet, task) pairs where task.due_date is today."""
        today = date.today()
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.due_date == today
        ]

    def sort_by_time(self, task_pairs: Optional[list] = None) -> list:
        """Sort (pet, task) pairs by task time in ascending HH:MM order."""
        if task_pairs is None:
            task_pairs = self.owner.get_all_tasks()
        return sorted(task_pairs, key=lambda pt: pt[1].time)

    def filter_by_pet(self, pet_name: str, task_pairs: Optional[list] = None) -> list:
        """Return only (pet, task) pairs belonging to the named pet."""
        if task_pairs is None:
            task_pairs = self.owner.get_all_tasks()
        return [(p, t) for p, t in task_pairs if p.name.lower() == pet_name.lower()]

    def filter_by_status(self, completed: bool, task_pairs: Optional[list] = None) -> list:
        """Return (pet, task) pairs filtered by completion status."""
        if task_pairs is None:
            task_pairs = self.owner.get_all_tasks()
        return [(p, t) for p, t in task_pairs if t.completed == completed]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a task done and add the next occurrence to the pet if recurring."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, task_pairs: Optional[list] = None) -> list:
        """Return warning strings for tasks scheduled at the same time slot."""
        if task_pairs is None:
            task_pairs = self.owner.get_all_tasks()
        time_map: dict = {}
        for pet, task in task_pairs:
            time_map.setdefault(task.time, []).append((pet, task))
        warnings = []
        for time_slot, pairs in time_map.items():
            if len(pairs) > 1:
                descs = ", ".join(f"'{t.description}' ({p.name})" for p, t in pairs)
                warnings.append(f"Conflict at {time_slot}: {descs}")
        return warnings

    def get_schedule(self) -> list:
        """Return today's tasks sorted by time."""
        return self.sort_by_time(self.get_todays_tasks())

    def format_schedule(self) -> str:
        """Return a human-readable string of today's sorted schedule with conflict notices."""
        lines = [f"Today's Schedule for {self.owner.name}'s pets:"]
        schedule = self.get_schedule()
        if not schedule:
            lines.append("  (no tasks scheduled for today)")
        else:
            current_pet_name = None
            for pet, task in schedule:
                if pet.name != current_pet_name:
                    lines.append(f"\n  {pet.name} ({pet.species}):")
                    current_pet_name = pet.name
                status = "✓" if task.completed else "○"
                lines.append(
                    f"    {status} {task.time} — {task.description} "
                    f"({task.duration_minutes} min) [{task.priority}] [{task.frequency}]"
                )
        conflicts = self.detect_conflicts(schedule)
        if conflicts:
            lines.append("\n  ⚠️  Conflicts detected:")
            for w in conflicts:
                lines.append(f"    • {w}")
        return "\n".join(lines)
