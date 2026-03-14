from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


@dataclass
class HistoryItem:
    query: str
    result: Any


class MemoryManager:
    def __init__(self) -> None:
        self._history: List[HistoryItem] = []
        self._last_result: Any = None

    def add(self, query: str, result: Any) -> None:
        self._history.append(HistoryItem(query=query, result=result))
        self._last_result = result

    def clear(self) -> None:
        self._history.clear()
        self._last_result = None

    def last_result(self) -> Any:
        return self._last_result

    def history(self) -> List[HistoryItem]:
        return list(self._history)
