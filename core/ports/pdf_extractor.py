from __future__ import annotations

from abc import ABC, abstractmethod


class PdfExtractor(ABC):
    @abstractmethod
    def extract_text(self, path: str) -> str:
        raise NotImplementedError

