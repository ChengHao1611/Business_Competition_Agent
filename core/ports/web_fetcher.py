from __future__ import annotations

from abc import ABC, abstractmethod


class WebFetcher(ABC):
    @abstractmethod
    def fetch_page_text(self, url: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def search_competition(self, competition_name: str, num_results: int = 10) -> dict:
        raise NotImplementedError

