from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def execute(self, context: str, user_id: str="", user_name: str="") -> tuple[str, str]:
        """
        Args:
          context: user message
        Returns:
          (next_state_name, reply_message)
        """
        
        pass