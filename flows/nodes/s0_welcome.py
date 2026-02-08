from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps


class S0Welcome(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        add_friend_reply = (
            "歡迎使用【競賽小幫手】\n"
            "我會依照你的狀況，陪你從「確認競賽是否適合」到「產出完整可投的提案」。\n"
            "不論你現在有沒有提案，我都會帶你走對的流程，補齊缺少的內容、對齊競賽方向。\n"
            "只要照著問題回答或上傳檔案，就能一步步完成參賽準備。\n\n"
            "注意事項：\n"
            "一次傳送一則訊息，等待回覆後再傳送\n"
        )

        return Transition(
            next_state="S0_1_team_info",
            replies=[add_friend_reply],
            auto_advance=True,
        )
