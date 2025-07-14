# llm_gateway.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Configurable endpoints from .env or defaults
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
LOCALAI_URL = os.getenv("LOCALAI_URL", "http://localhost:8080/v1/chat/completions")
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
HF_URL = os.getenv("HUGGINGFACE_URL", "https://api-inference.huggingface.co/models/")
HF_API_KEY = os.getenv("HUGGINGFACE_TOKEN", "")

class LLMRequest(BaseModel):
    prompt: str
    provider: str = "ollama"         # ollama | localai | lmstudio | huggingface
    model: str = "llama3"            # default; can override per provider
    max_tokens: int = 512

@app.post("/llm/generate")
def generate(req: LLMRequest):
    prompt = req.prompt
    provider = req.provider.lower()
    model = req.model

    if provider == "ollama":
        # Ollama simple completion API
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        try:
            r = requests.post(OLLAMA_URL, json=data, timeout=60)
            r.raise_for_status()
            out = r.json()
            return {"response": out.get("response", out.get("message", ""))}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama error: {e}")

    elif provider in ("localai", "lmstudio"):
        # OpenAI-compatible API (chat/completions)
        api_url = LOCALAI_URL if provider == "localai" else LMSTUDIO_URL
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": req.max_tokens,
            "temperature": 0.7,
        }
        try:
            r = requests.post(api_url, json=data, timeout=90)
            r.raise_for_status()
            out = r.json()
            # Both LMStudio/LocalAI return choices list
            return {"response": out["choices"][0]["message"]["content"]}
        except Exception as e:
            raise HTTP
