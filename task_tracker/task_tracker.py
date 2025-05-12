# -*- coding: utf-8 -*-
"""
Task tracker module.
"""

from typing import Generator
from datetime import datetime
from pathlib import Path
from json import JSONDecodeError, load, dump


class TaskTracker:
    """Track and manage tasks."""

    task_properties = ["id", "createdAt", "updatedAt", "status", "description"]
    task_statuses = ["todo", "in-progress", "done"]

    def __init__(self, cache_file: Path | None = None) -> None:
        self._tasks: dict[str, list[str]] = {}
        self._new_id: int = 1
        self._cache_file: Path = (
            Path(__file__).parent.joinpath("tasks.json")
            if cache_file is None
            else cache_file
        )

    def load(self) -> None:
        """Load tasks from json file."""
        if not self._cache_file.is_file():
            with open(self._cache_file, mode="x", encoding="utf-8") as f:
                dump({}, f, indent=4)
            return
        with open(self._cache_file, mode="r", encoding="utf-8") as f:
            try:
                tasks: dict[str, dict[str, str]] = load(f)
            except JSONDecodeError:
                print("Error: corrupted JSON file.")
                return
        self._tasks = {id: list(task.values()) for id, task in tasks.items()}
        if tasks:
            self._new_id = int(tasks.popitem()[0]) + 1

    def save(self) -> None:
        """Write tasks to a JSON file."""
        with open(self._cache_file, mode="w", encoding="utf-8") as f:
            dump(
                {
                    id: dict(zip(TaskTracker.task_properties[1:], task))
                    for id, task in self._tasks.items()
                },
                f,
                indent=4,
            )

    def add(self, description: str) -> str:
        """
        Usage: add <description>

        Add a new task, return the ID of task.

        Args:
            description (str): A short description of the new task.

        Returns:
            str: The ID of the new task.
        """
        time = datetime.now().isoformat(" ", "seconds")
        self._tasks[id := str(self._new_id)] = [time, time, "todo", description]
        self._new_id += 1
        return id

    def update(self, id: str, description: str) -> None:
        """
        Usage: update <id> <description>

        Update a task's description by ID.

        Args:
            id (str): The ID of the task to be updated.
            description (str): A new short description of the task to be updated.
        """
        if id not in self._tasks:
            print(f"Failed: unknown task ID '{id}'.")
            return
        # update property updatedAt
        self._tasks[id][1] = datetime.now().isoformat(" ", "seconds")
        # update property description
        self._tasks[id][3] = description

    def delete(self, id: str) -> None:
        """
        Usage: delete <id>

        Delete a task by ID.

        Args:
            id (str): The ID of the task to be deleted.
        """
        if id not in self._tasks:
            print(f"Failed: unknown task ID '{id}'.")
            return
        self._tasks.pop(id)

    def mark_status(self, id: str, status: str) -> None:
        """
        Usage: mark <id> {"todo" | "in-progress" | "done"}

        Marking a task as todo, in progress or done.

        Args:
            id (str): The ID of the task to be marked.
            status (str): The new status of the task to be marked.
        """
        if id not in self._tasks:
            print(f"Failed: unknown task ID '{id}'.")
            return
        if status not in TaskTracker.task_statuses:
            print(f"Failed: unknown task status '{status}'.")
            print("Choose a valid statuses from todo, in-progress, done.")
            return
        self._tasks[id][2] = status

    def list_by_status(self, status: str) -> Generator[list[str]] | None:
        """
        Usage: list [{"todo" | "in-progress" | "done" | "not-done" | "all"}]

        If status is "", list all tasks, or list tasks that are on the status.

        Args:
            status (str): The status of the task that to be listed.

        Returns:
            Generator[list[str]] | None: If status is unknown, return None, else return a generator of tasks.
        """
        if status == "":
            return ([id, *task] for id, task in self._tasks.items())
        if status == "not-done":
            return (
                [id, *task] for id, task in self._tasks.items() if task[2] != "done"
            )
        if status in TaskTracker.task_statuses:
            return (
                [id, *task] for id, task in self._tasks.items() if task[2] == status
            )
        print(f"Failed: unknown task status '{status}'.")
        print("Choose a valid status from todo, in-progress, done, not-done.")
        return None
