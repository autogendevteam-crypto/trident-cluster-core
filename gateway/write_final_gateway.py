content = '''import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()
app = FastAPI(title="TRIDENT Agent Gateway")

# --- CONFIGURAZIONE VARIABILI D'AMBIENTE (DEFAULT SICURI) ---
LOCAL_PORT = os.getenv("LOCAL_PORT", "1234")
LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "qwen2.5-coder-7b-instruct")

ALIBABA_BASE_URL = os.getenv("ALIBABA_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
ALIBABA_CHAT_URL = f"{ALIBABA_BASE_URL}/chat/completions"
ALIBABA_API_KEY = os.getenv("ALIBABA_API_KEY", "")

MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1").rstrip("/")
MISTRAL_CHAT_URL = f"{MISTRAL_BASE_URL}/chat/completions"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

AGENT_MAP = {
    # Local / Bionic
    "bionic": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    "local": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    
    # Alibaba Cloud
    "qwen-plus": {"provider": "alibaba", "model_id": "qwen-plus"},
    "qwen-max": {"provider": "alibaba", "model_id": "qwen-max"},
    
    # Mistral Standard Models (Niente agenti ag_)
    "m-small": {"provider": "mistral", "model_id": "mistral-small-latest"},
    "m-large": {"provider": "mistral", "model_id": "mistral-large-latest"},
}

TARGETS = {
    "bionic": {"url": f"http://127.0.0.1:{LOCAL_PORT}/v1/chat/completions", "key": "dummy"},
    "alibaba": {"url": ALIBABA_CHAT_URL, "key": ALIBABA_API_KEY},
    "mistral": {"url": MISTRAL_CHAT_URL, "key": MISTRAL_API_KEY}
}

def recompose_sse(text: str):
    parts = []
    cid = None
    model = None
    created = None
    finish = None
    usage = None
    saw_chunk = False

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            continue
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        
        saw_chunk = True
        cid = cid or obj.get("id")
        model = model or obj.get("model")
        created = created or obj.get("created")
        
        for ch in obj.get("choices", []):
            delta = ch.get("delta") or {}
            if delta.get("content"):
                parts.append(delta["content"])
            if ch.get("finish_reason"):
                finish = ch["finish_reason"]
        
        if obj.get("usage"):
            usage = obj["usage"]
            
    full = "".join(parts)
    if not saw_chunk and not full:
        return None
        
    return {
        "id": cid or "trident-recomposed",
        "object": "chat.completion",
        "created": created or 0,
        "model": model or "unknown",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": full}, "finish_reason": finish or "stop"}],
        "usage": usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

@app.get("/v1/models")
async def list_models():
    models = [{"id": name, "object": "model", "owned_by": "trident-gateway"} for name in AGENT_MAP.keys()]
    return {"data": models, "object": "list"}

@app.get("/debug/config")
async def debug_config():
    return {
        "local_port": LOCAL_PORT,
        "local_model_id": LOCAL_MODEL_ID,
        "alibaba_chat_url": ALIBABA_CHAT_URL,
        "alibaba_key_present": bool(ALIBABA_API_KEY),
        "mistral_chat_url": MISTRAL_CHAT_URL,
        "mistral_key_present": bool(MISTRAL_API_KEY),
        "mapped_models": list(AGENT_MAP.keys())
    }

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model", "bionic")
    route = AGENT_MAP.get(model_name)

    if not route:
        raise HTTPException(status_code=400, detail=f"Modello non mappato: {model_name}")

    provider = route["provider"]
    target = TARGETS.get(provider)

    if not target:
        raise HTTPException(status_code=500, detail=f"Provider sconosciuto: {provider}")

    if provider != "bionic" and not target["key"]:
        raise HTTPException(status_code=500, detail=f"Chiave API mancante per {provider}. Controlla .env")

    body["model"] = route["model_id"]
    wants_stream = bool(body.get("stream", False))
    
    headers = {
        "Authorization": f"Bearer {target['key']}",
        "Content-Type": "application/json"
    }

    # RAMO STREAMING
    if wants_stream:
        client = httpx.AsyncClient(timeout=180.0)
        try:
            req = client.build_request("POST", target["url"], json=body, headers=headers)
            resp = await client.send(req, stream=True)
        except httpx.RequestError as e:
            await client.aclose()
            raise HTTPException(status_code=502, detail=f"Backend {provider} irraggiungibile: {e}")

        if resp.status_code != 200:
            raw = await resp.aread()
            await resp.aclose(); await client.aclose()
            return PlainTextResponse(status_code=resp.status_code, content=raw.decode(errors="replace"))

        media = resp.headers.get("content-type", "text/event-stream")
        async def gen():
            try:
                async for chunk in resp.aiter_raw():
                    yield chunk
            finally:
                await resp.aclose()
                await client.aclose()
        return StreamingResponse(gen(), media_type=media, status_code=resp.status_code)

    # RAMO NON-STREAMING
    try:
        async with httpx.AsyncClient(timeout=180.0) as c:
            response = await c.post(target["url"], json=body, headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Backend {provider} irraggiungibile: {e}")

    if response.status_code != 200:
        return PlainTextResponse(status_code=response.status_code, content=response.text)

    try:
        data = response.json()
    except Exception:
        data = recompose_sse(response.text)
        if data is None:
            return PlainTextResponse(status_code=502, content=f"Risposta non-JSON da {provider}: {response.text[:2000]}")

    return JSONResponse(status_code=200, content=data)

if __name__ == "__main__":
    print(f"🚀 TRIDENT Gateway :4000 | local :{LOCAL_PORT} | STREAM-PASSTHROUGH ATTIVO")
    uvicorn.run(app, host="0.0.0.0", port=4000)
'''

with open("gateway.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ FILE SCRITTO PERFETTAMENTE SU DISCO.")