from __future__ import annotations

import logging
import tempfile
import time
import uuid
from pathlib import Path

from flask import Blueprint, jsonify, render_template, request, session

from app.flow_service import FlowService
from app.message_service import MessageService
from core.ports.pdf_extractor import PdfExtractor
from infra.webapp.message_gateway import WebMessageGateway

logger = logging.getLogger(__name__)

MAX_UPLOAD_MB = 20
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
TRANSCRIPT_KEY = "web_transcript_v1"

##流程區塊
STATE_UI: dict[str, dict[str, object]] = {
    # S0 - Team info
    "StoreContactPerson": {"section": "團隊基本資訊", "label": "稱呼", "editable": True, "multiline": False},
    "StoreContactEmail": {"section": "團隊基本資訊", "label": "Email", "editable": True, "multiline": False},
    "StoreTeamIdentity": {"section": "團隊基本資訊", "label": "身分", "editable": True, "multiline": False},
    "StoreTeamSize": {"section": "團隊基本資訊", "label": "成員人數", "editable": True, "multiline": False},
    "StoreTeamBackground": {"section": "團隊基本資訊", "label": "背景", "editable": True, "multiline": True},
    "StoreTeamHours": {"section": "團隊基本資訊", "label": "每週可投入時間", "editable": True, "multiline": False},
    # S0 - Competition info
    "CheckAndStoreCompetitionInfo": {"section": "競賽資訊", "label": "競賽網址或內容", "editable": True, "multiline": True},
    # S0 - Requirement
    "S0_4_1_RequirementJudge": {"section": "目前狀態", "label": "目前狀態 (1/2)", "editable": True, "multiline": False},
    "S0_5_1_GetProposal": {"section": "提案內容", "label": "提案內容", "editable": True, "multiline": True},
    # S1 - Proposal outline
    "StoreQuestionType": {"section": "題目輪廓", "label": "問題類型", "editable": True, "multiline": False},
    "StoreTA": {"section": "題目輪廓", "label": "主要對象", "editable": True, "multiline": False},
    "StoreImplementMethod": {"section": "題目輪廓", "label": "實作方式", "editable": True, "multiline": False},
    # S1 - Task deepening
    "StoreTaskTA": {"section": "提案細化", "label": "幫助對象", "editable": True, "multiline": True},
    "StoreTaskPainPoint": {"section": "提案細化", "label": "痛點", "editable": True, "multiline": True},
    "StoreTaskMethod": {"section": "提案細化", "label": "解法", "editable": True, "multiline": True},
    "StoreTaskBenefit": {"section": "提案細化", "label": "效益", "editable": True, "multiline": True},
}


def create_web_blueprint(
    flow_service: FlowService,
    state_store,
    pdf_extractor: PdfExtractor,
) -> Blueprint:
    blueprint = Blueprint(
        "web_chat",
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/web/static",
    )

    def _now() -> float:
        return time.time()

    def _ensure_web_user_id() -> str:
        user_id = session.get("web_user_id")
        if not user_id:
            user_id = f"web-{uuid.uuid4()}"
            session["web_user_id"] = user_id
        return user_id

    def _get_transcript(user_id: str) -> list[dict]:
        ctx = state_store.get_context(user_id) or {}
        transcript = ctx.get(TRANSCRIPT_KEY) or []
        if isinstance(transcript, list):
            return transcript
        return []

    def _save_transcript(user_id: str, transcript: list[dict]) -> None:
        try:
            state_store.update_context(user_id, {TRANSCRIPT_KEY: transcript})
        except Exception:
            logger.exception("Failed to persist transcript for user_id=%s", user_id)

    def _format_turn_for_blocks(turn: dict, turn_index: int) -> dict | None:
        """
        Convert user-input messages into stored blocks.
        """
        user_text = turn.get("user_text")
        if not user_text:
            return None
        kind = str(turn.get("kind") or "text")
        state_before = str(turn.get("state_before") or "")
        meta = STATE_UI.get(state_before) or {
            "section": "其他",
            "label": state_before or "未命名",
            "editable": True,
            "multiline": True,
        }
        display_value = str(user_text)
        editable = bool(meta.get("editable", True))
        multiline = bool(meta.get("multiline", True))
        if kind == "pdf":
            filename = ""
            try:
                filename = str((turn.get("meta") or {}).get("filename") or "")
            except Exception:
                filename = ""
            display_value = f"[PDF] {filename}".strip()
            editable = False
            multiline = False
        return {
            "turn_index": turn_index,
            "state": state_before,
            "section": str(meta.get("section")),
            "label": str(meta.get("label")),
            "value": display_value,
            "editable": editable,
            "multiline": multiline,
        }

    def _build_blocks(transcript: list[dict]) -> list[dict]:
        """
        procsee block
        """
        blocks: list[dict] = []
        for idx, turn in enumerate(transcript):
            block = _format_turn_for_blocks(turn, idx)
            if block:
                blocks.append(block)
        return blocks

    def _status_text(state: str) -> str:
        state = state or ""
        meta = STATE_UI.get(state)
        if meta:
            return f"下一步：{meta.get('label')}"
        if state.endswith("Judge") or "CheckSelection" in state or "Choice" in state:
            return "下一步：請依提示選擇"
        if not state:
            return "準備中"
        return "對話進行中"

    def _delete_user_context(user_id: str) -> None:
        """
        之後要修改，在port的state_store處理
        """
        supabase = getattr(state_store, "_supabase", None)
        table = getattr(state_store, "_table", None)
        if supabase is None or not table:
            return
        supabase.table(table).delete().eq("line_id", user_id).execute()

    def _make_message_service() -> tuple[MessageService, WebMessageGateway]:
        gateway = WebMessageGateway()
        service = MessageService(
            flow_service=flow_service,
            message_gateway=gateway,
            pdf_extractor=pdf_extractor,
        )
        return service, gateway

    def _current_state(user_id: str) -> str:
        """
        之後要修改，在port的state_store處理
        """
        try:
            supabase = getattr(state_store, "_supabase", None)
            table = getattr(state_store, "_table", None)
            if supabase is None or not table:
                return ""
            res = (
                supabase
                .table(table)
                .select("current_state")
                .eq("line_id", user_id)
                .execute()
            )
            if res.data:
                return res.data[0]["current_state"]
        except Exception:
            logger.exception("Failed to read web current_state for user_id=%s", user_id)
        return ""

    def _run_text_message(user_id: str, text: str, reply_token: str) -> tuple[str, str, list[str]]:
        state_before = state_store.get_state(user_id)
        service, gateway = _make_message_service()
        gateway.drain_messages()
        service.handle_text(reply_token, user_id, text)
        messages = gateway.drain_messages()
        state_after = _current_state(user_id)
        return state_before, state_after, messages

    def _append_turn(user_id: str, turn: dict) -> list[dict]:
        transcript = _get_transcript(user_id)
        transcript.append(turn)
        _save_transcript(user_id, transcript)
        return transcript

    @blueprint.get("/web")
    def web_home():
        user_id = _ensure_web_user_id()
        return render_template("web_chat.html", user_id=user_id, max_upload_mb=MAX_UPLOAD_MB)

    @blueprint.get("/web/api/session")
    def web_session():
        user_id = _ensure_web_user_id()
        current_state = _current_state(user_id)
        return jsonify({
            "ok": True,
            "user_id": user_id,
            "current_state": current_state,
            "status_text": _status_text(current_state),
        })

    @blueprint.get("/web/api/transcript")
    def web_transcript():
        user_id = _ensure_web_user_id()
        transcript = _get_transcript(user_id)
        current_state = _current_state(user_id)
        return jsonify({
            "ok": True,
            "user_id": user_id,
            "current_state": current_state,
            "status_text": _status_text(current_state),
            "transcript": transcript,
            "blocks": _build_blocks(transcript),
        })

    @blueprint.post("/web/api/start")
    def web_start():
        user_id = _ensure_web_user_id()
        transcript = _get_transcript(user_id)
        if transcript:
            current_state = _current_state(user_id)
            return jsonify({
                "ok": True,
                "user_id": user_id,
                "messages": [],
                "current_state": current_state,
                "status_text": _status_text(current_state),
                "transcript": transcript,
                "blocks": _build_blocks(transcript),
            })

        state_before, state_after, messages = _run_text_message(user_id, "", "web-start-token")

        turn = {
            "kind": "start",
            "ts": _now(),
            "state_before": state_before,
            "state_after": state_after,
            "user_text": None,
            "bot_messages": messages,
        }
        transcript = _append_turn(user_id, turn)

        return jsonify({
            "ok": True,
            "user_id": user_id,
            "messages": messages,
            "current_state": state_after,
            "status_text": _status_text(state_after),
            "transcript": transcript,
            "blocks": _build_blocks(transcript),
        })

    @blueprint.post("/web/api/chat")
    def web_chat():
        user_id = _ensure_web_user_id()
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("message") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "請輸入訊息"}), 400

        transcript = _get_transcript(user_id)
        if not transcript:
            sb, sa, msgs = _run_text_message(user_id, "", "web-start-token")
            start_turn = {
                "kind": "start",
                "ts": _now(),
                "state_before": sb,
                "state_after": sa,
                "user_text": None,
                "bot_messages": msgs,
            }
            transcript = _append_turn(user_id, start_turn)

        state_before, state_after, messages = _run_text_message(user_id, text, "web-reply-token")

        turn = {
            "kind": "text",
            "ts": _now(),
            "state_before": state_before,
            "state_after": state_after,
            "user_text": text,
            "bot_messages": messages,
        }
        transcript = _append_turn(user_id, turn)

        return jsonify({
            "ok": True,
            "user_id": user_id,
            "messages": messages,
            "current_state": state_after,
            "status_text": _status_text(state_after),
            "transcript": transcript,
            "blocks": _build_blocks(transcript),
        })

    @blueprint.post("/web/api/upload")
    def web_upload():
        user_id = _ensure_web_user_id()
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            return jsonify({"ok": False, "error": "請選擇 PDF 檔案"}), 400

        filename = upload.filename.lower()
        if not filename.endswith(".pdf"):
            return jsonify({"ok": False, "error": "目前只支援 PDF"}), 400

        upload.seek(0, 2)
        size = upload.tell()
        upload.seek(0)
        if size > MAX_UPLOAD_BYTES:
            return jsonify({"ok": False, "error": f"檔案太大，請上傳 {MAX_UPLOAD_MB}MB 以下的 PDF"}), 400

        tmp_path = None
        try:
            transcript = _get_transcript(user_id)
            if not transcript:
                sb, sa, msgs = _run_text_message(user_id, "", "web-start-token")
                start_turn = {
                    "kind": "start",
                    "ts": _now(),
                    "state_before": sb,
                    "state_after": sa,
                    "user_text": None,
                    "bot_messages": msgs,
                }
                transcript = _append_turn(user_id, start_turn)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                upload.save(tmp)
                tmp_path = tmp.name

            extracted_text = pdf_extractor.extract_text(tmp_path)
            state_before, state_after, messages = _run_text_message(user_id, extracted_text, "web-upload-token")

            turn = {
                "kind": "pdf",
                "ts": _now(),
                "state_before": state_before,
                "state_after": state_after,
                "user_text": extracted_text,
                "bot_messages": messages,
                "meta": {"filename": upload.filename},
            }
            transcript = _append_turn(user_id, turn)

            return jsonify({
                "ok": True,
                "user_id": user_id,
                "messages": messages,
                "current_state": state_after,
                "status_text": _status_text(state_after),
                "transcript": transcript,
                "blocks": _build_blocks(transcript),
            })
        except Exception:
            logger.exception("Web upload failed for user_id=%s", user_id)
            return jsonify({"ok": False, "error": "處理 PDF 時發生錯誤，請稍後再試"}), 500
        finally:
            if tmp_path and Path(tmp_path).exists():
                Path(tmp_path).unlink(missing_ok=True)

    @blueprint.post("/web/api/edit")
    def web_edit():
        user_id = _ensure_web_user_id()
        payload = request.get_json(silent=True) or {}
        try:
            turn_index = int(payload.get("turn_index"))
        except Exception:
            return jsonify({"ok": False, "error": "turn_index 格式錯誤"}), 400

        value = str(payload.get("value") or "").strip()
        if not value:
            return jsonify({"ok": False, "error": "請輸入要修改的內容"}), 400

        transcript = _get_transcript(user_id)
        if not transcript:
            return jsonify({"ok": False, "error": "目前沒有可修改的內容"}), 400
        if turn_index < 0 or turn_index >= len(transcript):
            return jsonify({"ok": False, "error": "turn_index 超出範圍"}), 400

        target_turn = transcript[turn_index]
        kind = str(target_turn.get("kind") or "")
        if kind == "start":
            return jsonify({"ok": False, "error": "此步驟不可修改"}), 400
        if kind == "pdf":
            return jsonify({"ok": False, "error": "PDF 步驟不可修改"}), 400
        state_before = str(target_turn.get("state_before") or "")
        editable = bool((STATE_UI.get(state_before) or {}).get("editable", True))
        if not editable:
            return jsonify({"ok": False, "error": "此步驟不可修改"}), 400

        target_turn["user_text"] = value

        # Replay all turns to rebuild state/context downstream of the edited step.
        replay_turns = list(transcript)
        if not replay_turns or str(replay_turns[0].get("kind") or "") != "start":
            replay_turns.insert(0, {"kind": "start"})
        _delete_user_context(user_id)
        _save_transcript(user_id, [])

        new_transcript: list[dict] = []
        for idx, turn in enumerate(replay_turns):
            kind = str(turn.get("kind") or "")
            if idx == 0 and kind == "start":
                sb, sa, msgs = _run_text_message(user_id, "", "web-replay-start")
                new_turn = {
                    "kind": "start",
                    "ts": _now(),
                    "state_before": sb,
                    "state_after": sa,
                    "user_text": None,
                    "bot_messages": msgs,
                }
            else:
                user_text = str(turn.get("user_text") or "")
                sb, sa, msgs = _run_text_message(user_id, user_text, f"web-replay-{idx}")
                new_turn = {
                    "kind": kind or "text",
                    "ts": _now(),
                    "state_before": sb,
                    "state_after": sa,
                    "user_text": user_text,
                    "bot_messages": msgs,
                    "meta": turn.get("meta") or {},
                }
            new_transcript.append(new_turn)

        _save_transcript(user_id, new_transcript)
        current_state = _current_state(user_id)
        return jsonify({
            "ok": True,
            "user_id": user_id,
            "current_state": current_state,
            "status_text": _status_text(current_state),
            "transcript": new_transcript,
            "blocks": _build_blocks(new_transcript),
        })

    @blueprint.post("/web/api/reset")
    def web_reset():
        old_user_id = session.get("web_user_id")
        if old_user_id:
            _delete_user_context(old_user_id)

        session["web_user_id"] = f"web-{uuid.uuid4()}"
        return jsonify({
            "ok": True,
            "user_id": session["web_user_id"],
            "current_state": "",
            "status_text": "準備中",
            "transcript": [],
            "blocks": [],
        })

    return blueprint
