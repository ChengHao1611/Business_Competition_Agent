from __future__ import annotations

import logging
import time

from pypdf import PdfReader

from core.ports.pdf_extractor import PdfExtractor

logger = logging.getLogger(__name__)


class PyPdfExtractor(PdfExtractor):
    def extract_text(self, path: str) -> str:
        start_time = time.perf_counter()
        try:
            reader = PdfReader(str(path))
        except Exception as e:
            raise ValueError("failed to open PDF") from e

        open_time = time.perf_counter()
        texts: list[str] = []
        total_chars = 0
        page_count = len(reader.pages)

        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    texts.append(page_text)
                    total_chars += len(page_text)
            except Exception:
                logger.warning("failed to extract text from page %d | file=%s", i, path)
                continue

        extract_time = time.perf_counter()

        if not texts:
            raise ValueError("PDF contains no extractable text")

        full_text = "\n".join(texts)
        end_time = time.perf_counter()

        logger.info(
            "PDF parsed | file=%s | pages=%d | chars=%d | "
            "open=%.3fs | extract=%.3fs | total=%.3fs",
            path,
            page_count,
            total_chars,
            open_time - start_time,
            extract_time - open_time,
            end_time - start_time,
        )

        return full_text

