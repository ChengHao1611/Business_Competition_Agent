from __future__ import annotations

from typing import Any

from core.flow.context import FlowContext
from core.flow.state_machine import StateMachine
from core.flow.transition import Transition
from core.ports.state_store import StateStore
import logging

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self, state_store: StateStore, state_machine: StateMachine):
        self._state_store = state_store
        self._state_machine = state_machine

    def handle_message(
        self,
        user_id: str,
        message: str,
        user_name: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Transition:
        acquired = self._state_store.acquire_lock(user_id, user_name)
        if not acquired:
            logger.warning(f"{user_id} 重複發送訊息")
            transition = Transition(
                next_state="",
                replies=[]
            )

            return transition
        try:
            current_state = self._state_store.get_state(user_id, user_name)
            context_data = self._state_store.get_context(user_id)
            context = FlowContext(
                user_id=user_id,
                user_name=user_name,
                message=message,
                data=context_data,
                metadata=metadata or {},
            )
            transition = self._state_machine.execute(current_state, context)

            if transition.data_delta:
                self._state_store.update_context(user_id, transition.data_delta)

            self._state_store.set_state(user_id, transition.next_state)
            return transition
        finally:
            self._state_store.set_lock(user_id, False)
    
        

