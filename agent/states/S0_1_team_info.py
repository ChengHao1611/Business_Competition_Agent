from Linebot.linebot_reply_str import ADD_FRIEND_REPLY
from agent.state import State

class S0_1_Team_Info(State):
    def execute(self, context):
        return ("S0-1_team_info", ADD_FRIEND_REPLY)