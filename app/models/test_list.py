from __future__ import annotations

import uuid
from typing import Optional

from app.constants import TestStatus
from app.models.test_item import TestItem


class TestList:
    def __init__(self, name: str = "New Test List", list_id: Optional[str] = None) -> None:
        self.id: str = list_id or str(uuid.uuid4())
        self.name: str = name
        self.items: list[TestItem] = []

    def add_item(self, name: str, session_id: str = "") -> TestItem:
        item = TestItem(session_id=session_id, system_name=name)
        self.items.append(item)
        return item

    def remove_item(self, item_id: str) -> None:
        self.items = [i for i in self.items if i.id != item_id]

    def get_item(self, item_id: str) -> Optional[TestItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def reorder(self, new_order: list[str]) -> None:
        lookup = {i.id: i for i in self.items}
        reordered = [lookup[iid] for iid in new_order if iid in lookup]
        # preserve any items not in the new_order list at the end
        existing_ids = set(new_order)
        reordered += [i for i in self.items if i.id not in existing_ids]
        self.items = reordered

    def move_item(self, item_id: str, direction: int) -> bool:
        """Move an item up (-1) or down (+1).  Returns True if it actually moved."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                new_pos = i + direction
                if 0 <= new_pos < len(self.items):
                    self.items.pop(i)
                    self.items.insert(new_pos, item)
                    return True
                return False
        return False

    def all_passed(self) -> bool:
        return bool(self.items) and all(i.status == TestStatus.PASS for i in self.items)

    def summary(self) -> dict:
        counts = {s: 0 for s in TestStatus.ALL}
        for item in self.items:
            if item.status in counts:
                counts[item.status] += 1
        return counts
