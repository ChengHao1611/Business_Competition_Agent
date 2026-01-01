from . import proposal_template as pt
from agent.crawl_web_page import search_competition_with_serpapi
from ollamaLLM import send_messages_to_LLM
import logging
from db.db_op import (
    set_user_message_history,
    get_user_message_history,
    clear_user_message_history
)

logger = logging.getLogger(__name__)

# messages = [{
#     "role": "system",
#     "content": pt.system_role
# },{
#     "role": "user",
#     "content": """
#     我想要做一個能夠改善商業競賽的agent，
#     讓參加競賽的使用者能夠完善他們的競賽，
#     能夠幫助他們釐清提案邏輯
#     並整理提案架構
#     """
# },{
#     "role": "assistant",
#     "content": """
#     總分100分，你拿到13分
#     現況與問題：7
#     解決方案構想：6
#     市場規模與趨勢：0
#     競爭者分析：0
#     商業模式：0

#     建議方向：
#     1. 現況與問題：說明痛點會怎樣影響參賽者（如提案失敗率、時間成本）。
#     2. 解決方案：具體描述 agent 如何運作（例如 AI 分析、模板生成、即時回饋），並說明有何創新點與現有工 具差別。
#     3. 市場規模：列出目標使用者數量、相關產業的市場規模（如商業競賽平台、創業加速器），提供資料來源或合理推估依據，說明成長趨勢。
#     4. 競爭者分析：列舉目前市場上類似的提案輔助工具，分析其優缺點，說明你的方案在功能、成本或使用者體驗上如何差異化，並指出尚未被滿足的需求。
#     5. 商業模式：說明收入來源（訂閱、付費升級、企業授權等），主要成本（開發、雲端運算、行銷），以及價值如何透過平台、API 或合作夥伴傳遞給客戶。


#     感謝您提供的提案。依照五大評分構面，您的總分只有 13 分，主要因為缺少對痛點影響的說明、具體的執行方 法、任何市場或競爭資訊，以及完整的商業模式描述。上面列出的 missing_points 與 improvement_suggestions 可協助您逐項補強，讓提案更完整、說服力更強。祝您修正順利！
#     """
# },{
#     "role": "user",
#     "content": """
#     使用者的痛點是不知道完整的提案架構，浪費了許多時間在不必要的細節，
#     透過這個agent能夠讓他們在正確的架構下討論並思考自己忽略了那些因素
#     """
# },{
#     "role": "assistant",
#     "content": """
#     了解！看來參賽者常因不清楚完整的提案架構，
#     花了大量時間在不必要的細節上。
#     透過這個 agent，他們可以快速得到標準化的提案框架，
#     提醒哪些關鍵要素還沒被考慮，讓討論更聚焦、效率更高。
#     這樣一來，大家就能省下 時間、避免走冤枉路，專心在創意與執行上。
#     """
# },{
#     "role": "user",
#     "content": """
#     你覺得商業模式要用訂閱的好還是授權給其他公司來做收權利金?
#     """
# },{
#     "role": "assistant",
#     "content": """
#     兩種模式各有優缺點，選哪個要看你的產品特性、目標客群和長期目標。若你的 agent 需要持續更新、提供線上支援、收集使用者回饋，訂閱制比較適合，因為可以穩定的現金流、降低用戶一次性投入的門檻，同時也方便你 持續迭代功能。相對的，授權給其他公司收權利金的方式適合你已經有成熟、相對固定的核心技術，想快速擴散 到不同市場或與大型平台合作，讓對方負責行銷、客服等，換來一次性的授權費或持續的版稅。實務上也可以混 合使用：基礎功能走訂閱，進階或客製化模組授權給企業，這樣既能保證穩定收入，又能開拓大客戶的合作機會 。建議先評估產品的更新頻率、客戶願意承擔的成本，以及你自己想要投入的資源，再決定主打哪一條路線，或 是兩條路一起走。
#     """
# }]
def initialize_user_history(user_name: str):
    clear_user_message_history(user_name)
    set_user_message_history(user_name, "system", pt.system_role)


class Tool:
    @staticmethod
    def LLM_choose_tool(user_name: str, user_message: str) -> str:
        try:
            messages = [{"role": "user", "content": pt.LLM_choose_template + user_message}]
            response = send_messages_to_LLM(messages)
            print(response)
            tool = (response["tool"])
            input_word = response["input_word"]
            if tool == "find_completion":
                return Tool.find_completion(user_name, input_word)
            elif tool == "discuss_proposal":
                return Tool.discuss_proposal(user_name, input_word)
            elif tool == "organize_proposal":
                return Tool.organize_proposal(user_name, input_word)
            elif tool == "score_proposal":
                return Tool.score_proposal(user_name, input_word)
            return "錯誤工具"
        except Exception as e:
            logger.warning("LLM_choose_tool出現問題")
            print(e)
            return "出現莫名錯誤"

    @staticmethod
    def find_completion(user_name: str, user_message: str) -> str:
        try:
            initialize_user_history(user_name)
            messages = get_user_message_history(user_name)
            #print(f"找到{user_message}競賽")
            get_web_info = search_competition_with_serpapi(user_message)
            #print(get_web_info)
            result_message = get_web_info["pages"][0]["text"] + get_web_info["pages"][1]["text"]
            #print(result_message)
            set_user_message_history(user_name, "user", result_message)
            messages.append({"role": "user", "content": f"{result_message} + {pt.completion_info}"})
            response = send_messages_to_LLM(messages)
            LLM_response = response["reply_to_user"]
            set_user_message_history(user_name, "assistant", LLM_response)
            return LLM_response
        except Exception as e:
            logger.warning("find_completion出現問題")
            print(e)
            return "出現莫名錯誤"

    @staticmethod
    def discuss_proposal(user_name: str, user_message: str) -> str:
        try:
            messages = get_user_message_history(user_name)
            result_message = f"{user_message}" + pt.discussion
            messages.append({"role" : "user", "content": result_message})
            set_user_message_history(user_name, "user", user_message)
            response = send_messages_to_LLM(messages)
            LLM_response = response["reply_to_user"]
            set_user_message_history(user_name, "assistant", LLM_response)
            return LLM_response
        except Exception as e:
            logger.warning("discuss_proposal出現問題")
            print(e)
            return "出現莫名錯誤"

    @staticmethod
    def organize_proposal(user_name: str, user_message: str) -> str:
        try:
            messages = get_user_message_history(user_name)
            result_message = pt.proposal_integrated_template
            messages.append({"role" : "user", "content": result_message})
            set_user_message_history(user_name, "user", user_message)
            response = send_messages_to_LLM(messages)
            LLM_response = response["reply_to_user"]
            set_user_message_history(user_name, "assistant", LLM_response)
            return LLM_response
        except Exception as e:
            logger.warning("organize_proposal出現問題")
            print(e)
            return "出現莫名錯誤"
    
    def score_proposal(user_name: str, user_message: str) -> str:
        try:
            messages = get_user_message_history(user_name)
            result_message = pt.sysetm_promt + pt.proposal_reply_format + f"{user_message}"
            messages.append({"role" : "user", "content": result_message})
            set_user_message_history(user_name, "user", user_message)
            response = send_messages_to_LLM(messages)
            LLM_response = f"""總分100分，你拿到{response["scores"]["total_score"]}分
現況與問題：{response["scores"]["problem_analysis"]}
解決方案構想：{response["scores"]["solution_design"]}
市場規模與趨勢：{response["scores"]["market_analysis"]}
競爭者分析：{response["scores"]["business_model"]}
商業模式：{response["scores"]["competitor_analysis"]}

建議方向：
{response["improvement_suggestions"]["detailed_version"]}


{response["reply_to_user"]}
"""
            set_user_message_history(user_name, "assistant", LLM_response)
            return LLM_response
        except Exception as e:
            logger.warning("score_proposal出現問題")
            print(e)
            return "出現莫名錯誤"