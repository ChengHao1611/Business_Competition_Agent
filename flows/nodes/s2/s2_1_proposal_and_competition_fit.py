from __future__ import annotations

from core.flow.state_node import StateNode
from core.flow.transition import Transition
from core.flow.context import FlowContext, FlowDeps
import re
import logging

logger = logging.getLogger(__name__)

class S2_1_PAndCFit(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        data = str(context.data)

        messages = [{
            "role": "system",
            "content": "你是一位競賽顧問，負責判斷「團隊是否適合參加指定競賽」。\n"
                        "請根據使用者提供的【團隊基本資料】、【競賽資訊】與【提案內容】，進行審慎評估。\n"
                        "請嚴格依照以下格式輸出，不要加入額外說明、前言或結語：\n\n"

                        "結論: 綠燈 / 黃燈 / 紅燈\n"
                        "主要原因:\n"
                        "1. 資格: （地區 / 身分 / 年限是否符合）\n"
                        "2. 主題: （是否符合競賽主題，或交付物 / 時程是否可行）\n"
                        "3. （可選）其他關鍵限制或風險\n"
                        "「如果你硬要投」會最容易在哪裡被淘汰:\n"
                        "1. （具體原因，1 句）\n"
                        "2. （具體原因，1 句）\n\n"

                        "判斷原則說明：\n"
                        "- 綠燈：資格與主題高度符合，投入風險低\n"
                        "- 黃燈：部分條件勉強符合，但有明顯風險\n"
                        "- 紅燈：資格或核心條件明顯不符，不建議投入"
        },{
            "role": "user",
            "content": data
        }]

        reply = deps.llm_client.send_messages(messages)
        reply_text = str(reply)

        ## 判斷紅綠燈
        match = re.search(r"結論\s*[:：]\s*(綠燈|黃燈|紅燈)", reply_text)
        verdict = match.group(1) if match else None

        if verdict == "綠燈":
            next_state = "S2_2_CompetitionIntrodution"
        elif verdict == "紅燈" or verdict == "黃燈":
            next_state = "S2_1_1_PAndCFitRed"
        else:
            logger.warning("Failed to parse verdict from reply: %s", reply_text)
            next_state = "S2_1_1_PAndCFitRed"

        return Transition(
            next_state=next_state,
            replies=[reply],
            auto_advance=True,
        )
    
class S2_1_1_PAndCFitRed(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:

        reply = (
            "根據目前的資訊判斷，你們的團隊與這個競賽的條件不太相符，若繼續參加，被淘汰的風險會比較高。\n"
            "不過接下來怎麼做，還是由你來決定，我都可以協助你。\n"
            "請選擇你接下來想做的事，回覆「1/2」即可：\n"
            "1 繼續參加這個競賽\n"
            "2 重新尋找其他更適合的競賽\n"
        )

        return Transition(
            next_state="S2_1_2_PAndCCheckRed",
            replies=[reply],
            auto_advance=False,
        )

class S2_1_2_PAndCCheckRed(StateNode):
    def execute(self, context: FlowContext, deps: FlowDeps) -> Transition:
        message = context.message
        reply = ""

        if message == "1":
            next_state = "S2_2_CompetitionIntrodution"
            auto_advance = True
        elif message == "2":
            next_state = "S0_Welcome"
            auto_advance = True
        else:
            logger.warning(f"{context.user_id} 的選擇錯誤")
            next_state = "S2_1_2_PAndCCheckRed"
            reply = ("請回覆「1、2」：\n"
                     "1 繼續參加這個競賽\n"
                     "2 重新尋找其他更適合的競賽\n")
            auto_advance = False

        return Transition(
            next_state=next_state,
            replies=[reply],
            auto_advance=auto_advance,
        )

