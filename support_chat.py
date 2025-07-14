# support_chat.py
from fastapi import FastAPI, Request
import requests
app = FastAPI()
LLM_URL = "http://llm_gateway:9999/llm/generate"
@app.post("/support_chat/")
async def support_chat(req: Request):
    body = await req.json()
    prompt = f"Support Chatbot: {body['message']}"
    r = requests.post(LLM_URL, json={"prompt": prompt, "max_tokens": 256})
    reply = r.json().get("response", "Sorry, I couldn't help.")
    return {"reply": reply}
