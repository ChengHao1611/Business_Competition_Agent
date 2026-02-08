from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.ports.llm_client import LLMClient
from core.ports.web_fetcher import WebFetcher
from core.ports.pdf_extractor import PdfExtractor


@dataclass
class FlowContext:
    user_id: str
    user_name: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowDeps:
    llm_client: LLMClient | None = None
    web_fetcher: WebFetcher | None = None
    pdf_extractor: PdfExtractor | None = None

