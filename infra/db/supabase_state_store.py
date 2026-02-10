from __future__ import annotations

import logging
from typing import Any

from supabase import create_client

from config import settings
from core.ports.state_store import StateStore

logger = logging.getLogger(__name__)


class SupabaseStateStore(StateStore):
    def __init__(self, start_state: str | None = None):
        url = settings.get_env("SUPABASE_URL")
        key = settings.get_env("SUPABASE_SECRET_KEY")
        table = settings.get_env("SUPABASE_TABLE_NAME")
        if not url or not key or not table:
            raise RuntimeError("SUPABASE_URL / SUPABASE_SECRET_KEY / SUPABASE_TABLE_NAME must be set")

        self._supabase = create_client(url, key)
        self._table = table
        self._start_state = start_state or "S0_welcome"

    def _create_user(self, user_id: str, user_name: str) -> None:
        data = {
            "line_id": user_id,
            "line_name": user_name,
            "current_state": self._start_state,
            "data": {
                "team_identity": "",
                "team_size": "",
                "team_background": "",
                "team_hours": "",
                "competition": "",
                "competition_fit": "",
                "proposal": "",
                "question_type": "",
                "TA": "",
                "method": "",
                "three_outline": "",
                "pain_point": "",
                "benefit": "",
            },
        }
        self._supabase.table(self._table).insert(data).execute()
        logger.info("user created: %s", user_id)

    def get_state(self, user_id: str, user_name: str = "") -> str:
        try:
            res = (
                self._supabase
                .table(self._table)
                .select("current_state")
                .eq("line_id", user_id)
                .single()
                .execute()
            )
            return res.data["current_state"]
        except Exception:
            logger.warning("user missing; creating user: %s", user_id)
            self._create_user(user_id, user_name)
            return self._start_state

    def set_state(self, user_id: str, new_state: str) -> None:
        (
            self._supabase
            .table(self._table)
            .update({"current_state": new_state})
            .eq("line_id", user_id)
            .execute()
        )

    def get_context(self, user_id: str) -> dict[str, Any]:
        try:
            res = (
                self._supabase
                .table(self._table)
                .select("data")
                .eq("line_id", user_id)
                .single()
                .execute()
            )
            return res.data.get("data") or {}
        except Exception:
            return {}

    def update_context(self, user_id: str, delta: dict[str, Any]) -> None:
        current = self.get_context(user_id)
        merged = {**current, **delta}
        (
            self._supabase
            .table(self._table)
            .update({"data": merged})
            .eq("line_id", user_id)
            .execute()
        )

