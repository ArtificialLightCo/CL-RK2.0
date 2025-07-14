# ai_editor.py — CLÆRK Universal AI Editor API

import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
import requests
import difflib

logger = logging.getLogger("claerk.ai_editor")
app = FastAPI(title="CLÆRK AI Editor")

LLM_GATEWAY_URL = os.environ.get("LLM_GATEWAY_URL", "http://llm_gateway:9999/llm/generate")

@app.post("/ai_editor/")
async def ai_editor(
    instruction: str = Form(...),
    content: str = Form(""),
    file: UploadFile = File(None),
    filename: str = Form(None)
):
    # Read content from file or form
    if file:
        text = (await file.read()).decode("utf-8")
        fname = file.filename
    else:
        text = content
        fname = filename or "inline.txt"
    logger.info(f"AI editor editing: {fname} with instruction: {instruction}")

    # Compose LLM prompt
    llm_prompt = f"INSTRUCTION: {instruction}\n---\nCONTENT:\n{text}\n---\nPlease rewrite, edit, or improve the content as instructed. Output the full new version only."

    # Send to LLM Gateway
    resp = requests.post(
        LLM_GATEWAY_URL,
        json={"prompt": llm_prompt, "provider": "ollama", "model": "llama3", "max_tokens": 2048},
        timeout=60
    )
    improved = resp.json().get("response", "")
    # Create a diff (unified)
    diff = "\n".join(difflib.unified_diff(text.splitlines(), improved.splitlines(), fromfile="before", tofile="after", lineterm=""))
    # Optionally: auto-apply and commit (backend logic here)

    return JSONResponse({
        "filename": fname,
        "instruction": instruction,
        "before": text,
        "after": improved,
        "diff": diff
    })
