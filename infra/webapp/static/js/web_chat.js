const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendBtnEl = document.getElementById("send-btn");
const resetBtnEl = document.getElementById("reset-btn");
const statePillEl = document.getElementById("state-pill");
const sessionTextEl = document.getElementById("session-text");
const typingEl = document.getElementById("typing");
const pdfInputEl = document.getElementById("pdf-input");
const flowBlocksEl = document.getElementById("flow-blocks");
const maxUploadMb = Number(document.body.dataset.maxUploadMb || 0);

function appendBubble(role, text) {
  const bubble = document.createElement("article");
  bubble.className = `bubble ${role}`;
  const speaker = document.createElement("span");
  speaker.className = "speaker";
  speaker.textContent = role === "bot" ? "小幫手" : "你";
  const body = document.createElement("div");
  body.textContent = text;
  bubble.appendChild(speaker);
  bubble.appendChild(body);
  messagesEl.appendChild(bubble);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function clearMessages() {
  messagesEl.innerHTML = "";
}

function appendSystemNote(text) {
  const note = document.createElement("div");
  note.className = "hint";
  note.textContent = text;
  messagesEl.appendChild(note);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(isBusy) {
  sendBtnEl.disabled = isBusy;
  typingEl.classList.toggle("visible", isBusy);
}

function setSessionState(payload) {
  if (payload.user_id) {
    sessionTextEl.textContent = `對話 ID: ${payload.user_id}`;
  }
  const statusText = payload.status_text || payload.current_state || "準備中";
  statePillEl.textContent = statusText;
}

function groupBlocksBySection(blocks) {
  const groups = new Map();
  (blocks || []).forEach((block) => {
    const section = block.section || "其他";
    if (!groups.has(section)) groups.set(section, []);
    groups.get(section).push(block);
  });
  return groups;
}

function renderBlocks(blocks) {
  flowBlocksEl.innerHTML = "";
  if (!blocks || blocks.length === 0) {
    const hint = document.createElement("div");
    hint.className = "hint";
    hint.textContent = "尚未開始對話，流程區塊會在你回答問題後自動整理在這裡。";
    flowBlocksEl.appendChild(hint);
    return;
  }

  const groups = groupBlocksBySection(blocks);
  Array.from(groups.entries()).forEach(([section, items]) => {
    const sectionEl = document.createElement("div");
    sectionEl.className = "flow-section";

    const titleEl = document.createElement("div");
    titleEl.className = "flow-section-title";
    titleEl.textContent = section;
    sectionEl.appendChild(titleEl);

    items.forEach((block) => {
      const itemEl = document.createElement("div");
      itemEl.className = "flow-item";
      itemEl.dataset.turnIndex = String(block.turn_index);
      itemEl.dataset.multiline = String(Boolean(block.multiline));

      const rowEl = document.createElement("div");
      rowEl.className = "flow-row";

      const leftEl = document.createElement("div");
      const labelEl = document.createElement("div");
      labelEl.className = "flow-label";
      labelEl.textContent = block.label || block.state || "未命名";
      const valueEl = document.createElement("div");
      valueEl.className = "flow-value";
      valueEl.textContent = block.value || "";
      leftEl.appendChild(labelEl);
      leftEl.appendChild(valueEl);

      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "flow-edit";
      editBtn.textContent = "修改";
      editBtn.disabled = !block.editable;
      editBtn.addEventListener("click", () => {
        itemEl.classList.add("editing");
        editorInput.focus();
        editorInput.selectionStart = editorInput.value.length;
      });

      rowEl.appendChild(leftEl);
      rowEl.appendChild(editBtn);
      itemEl.appendChild(rowEl);

      const editorEl = document.createElement("div");
      editorEl.className = "flow-editor";

      let editorInput;
      if (block.multiline) {
        editorInput = document.createElement("textarea");
        editorInput.value = block.value || "";
      } else {
        editorInput = document.createElement("input");
        editorInput.value = block.value || "";
      }

      const actionsEl = document.createElement("div");
      actionsEl.className = "flow-editor-actions";

      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.className = "ghost";
      cancelBtn.textContent = "取消";
      cancelBtn.addEventListener("click", () => {
        itemEl.classList.remove("editing");
        editorInput.value = block.value || "";
      });

      const applyBtn = document.createElement("button");
      applyBtn.type = "button";
      applyBtn.className = "flow-apply";
      applyBtn.textContent = "套用並重新生成";
      applyBtn.addEventListener("click", async () => {
        const newValue = String(editorInput.value || "").trim();
        if (!newValue) {
          alert("請輸入要修改的內容");
          return;
        }
        await editTurn(block.turn_index, newValue);
      });

      actionsEl.appendChild(cancelBtn);
      actionsEl.appendChild(applyBtn);

      editorEl.appendChild(editorInput);
      editorEl.appendChild(actionsEl);
      itemEl.appendChild(editorEl);

      sectionEl.appendChild(itemEl);
    });

    flowBlocksEl.appendChild(sectionEl);
  });
}

function renderTranscript(transcript) {
  clearMessages();
  if (!transcript || transcript.length === 0) {
    appendSystemNote("正在準備對話...");
    return;
  }

  transcript.forEach((turn) => {
    const kind = turn.kind || "text";
    const userText = turn.user_text;
    if (userText) {
      if (kind === "pdf") {
        const filename = (turn.meta && turn.meta.filename) ? String(turn.meta.filename) : "";
        appendBubble("user", filename ? `已上傳 PDF：${filename}` : "已上傳 PDF");
      } else {
        appendBubble("user", userText);
      }
    }
    (turn.bot_messages || []).forEach((text) => appendBubble("bot", text));
  });
}

function applyPayload(payload) {
  setSessionState(payload);
  if (payload.blocks) renderBlocks(payload.blocks);
  if (payload.transcript) renderTranscript(payload.transcript);
}

async function startConversation() {
  setBusy(true);
  try {
    const response = await fetch("/web/api/start", { method: "POST" });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      appendSystemNote(payload.error || "啟動對話失敗，請稍後再試。");
      return;
    }
    applyPayload(payload);
  } catch (error) {
    appendSystemNote("目前無法連線到伺服器，請稍後再試。");
  } finally {
    setBusy(false);
  }
}

async function sendMessage(message) {
  const text = String(message || "").trim();
  if (!text) return;

  setBusy(true);

  try {
    const response = await fetch("/web/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      appendSystemNote(payload.error || "送出訊息失敗，請稍後再試。");
      return;
    }

    applyPayload(payload);
  } catch (error) {
    appendSystemNote("目前無法連線到伺服器，請稍後再試。");
  } finally {
    setBusy(false);
  }
}

async function uploadPdf(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    appendSystemNote("目前只支援 PDF。");
    return;
  }
  if (file.size > maxUploadMb * 1024 * 1024) {
    appendSystemNote("PDF 太大，請改上傳較小的檔案。");
    return;
  }

  appendSystemNote(`已選擇 PDF：${file.name}`);
  setBusy(true);

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch("/web/api/upload", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      appendSystemNote(payload.error || "PDF 處理失敗，請稍後再試。");
      return;
    }

    applyPayload(payload);
  } catch (error) {
    appendSystemNote("上傳 PDF 時發生錯誤，請稍後再試。");
  } finally {
    pdfInputEl.value = "";
    setBusy(false);
  }
}

async function editTurn(turnIndex, value) {
  setBusy(true);
  try {
    const response = await fetch("/web/api/edit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ turn_index: turnIndex, value }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      appendSystemNote(payload.error || "修改失敗，請稍後再試。");
      return;
    }
    applyPayload(payload);
  } catch (error) {
    appendSystemNote("修改時發生錯誤，請稍後再試。");
  } finally {
    setBusy(false);
  }
}

async function resetConversation() {
  setBusy(true);
  try {
    const response = await fetch("/web/api/reset", {
      method: "POST",
    });
    const payload = await response.json();
    clearMessages();
    renderBlocks([]);
    setSessionState(payload);
    await startConversation();
  } catch (error) {
    appendSystemNote("重設對話失敗，請稍後再試。");
  } finally {
    setBusy(false);
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = inputEl.value;
  inputEl.value = "";
  await sendMessage(text);
  inputEl.focus();
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", async () => {
    const prompt = button.getAttribute("data-prompt");
    inputEl.value = "";
    await sendMessage(prompt);
  });
});

resetBtnEl.addEventListener("click", resetConversation);
pdfInputEl.addEventListener("change", async (event) => {
  const file = event.target.files && event.target.files[0];
  await uploadPdf(file);
});

fetch("/web/api/transcript")
  .then((response) => response.json())
  .then(async (payload) => {
    if (!payload.ok) throw new Error("bad payload");
    applyPayload(payload);
    if (!payload.transcript || payload.transcript.length === 0) {
      await startConversation();
    }
  })
  .catch(() => {
    appendSystemNote("目前無法載入對話狀態，請重新整理頁面。");
    renderBlocks([]);
  });


