content = '''import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()
app = FastAPI(title="TRIDENT Agent Gateway")

LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "qwen2.5-coder-7b-instruct")
LOCAL_PORT = os.getenv("LOCAL_PORT", "1234")

AGENT_MAP = {
    "nexus": {"provider": "mistral", "model_id": os.getenv("MISTRAL_AGENT_NEXUS", "nexus")},
    "axiom": {"provider": "mistral", "model_id": os.getenv("MISTRAL_AGENT_AXIOM", "axiom")},
    "qwen-plus": {"provider": "alibaba", "model_id": "qwen-plus"},
    "qwen-max": {"provider": "alibaba", "model_id": "qwen-max"},
    "alibaba": {"provider": "alibaba", "model_id": "qwen-plus"},
    "bionic": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    "local": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
    "coder": {"provider": "bionic", "model_id": LOCAL_MODEL_ID},
}

TARGETS = {
    "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "key": os.getenv("MISTRAL_API_KEY")},
    "alibaba": {"url": os.getenv("ALIBABA_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"), "key": os.getenv("ALIBABA_API_KEY")},
    "bionic": {"url": f"http://127.0.0.1:{LOCAL_PORT}/v1/chat/completions", "key": "dummy"},
}

def recompose_sse(text):
    parts, cid, model, created, finish, usage, saw_chunk = [], None, None, None, None, None, False
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
            d = ch.get("delta") or {}
            if d.get("content"):
                parts.append(d["content"])
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
        "usage": usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

@app.get("/v1/models")
async def list_models():
    models = [{"id": n, "object": "model", "owned_by": "trident-gateway"} for n in AGENT_MAP.keys()]
    return {"data": models, "object": "list"}

@app.get("/debug/backend")
async def debug_backend():
    url = f"http://127.0.0.1:{LOCAL_PORT}/v1/models"
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url)
        return PlainTextResponse(content=f"TARGET: {url}\\nSTATUS: {r.status_code}\\nBODY:\\n{r.text}")
    except Exception as e:
        return PlainTextResponse(content=f"TARGET: {url}\\nERROR: {e}")

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model", "bionic")
    route = AGENT_MAP.get(model_name, {"provider": "alibaba", "model_id": model_name})
    provider = route["provider"]
    target = TARGETS.get(provider)
    if not target:
        raise HTTPException(status_code=500, detail=f"Provider sconosciuto: {provider}")
    if not target["key"] and provider != "bionic":
        raise HTTPException(status_code=500, detail=f"Chiave API mancante per {provider}. Controlla .env")

    body["model"] = route["model_id"]
    wants_stream = bool(body.get("stream", False))
    headers = {"Authorization": f"Bearer {target['key']}", "Content-Type": "application/json"}

    # === RAMO 1: PASSTHROUGH STREAMING (Cline chiede stream=true) ===
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

    # === RAMO 2: RISPOSTA IN BLOCCO (curl / client non-streaming) ===
    try:
        async with httpx.AsyncClient(timeout=180.0) as c:
            response = await c.post(target["url"], json=body, headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Backend {provider} irraggiungibile su {target['url']}: {e}")
    if response.status_code != 200:
        return PlainTextResponse(status_code=response.status_code, content=response.text)
    try:
        data = response.json()
    except Exception:
        data = recompose_sse(response.text)
        if data is None:
            return PlainTextResponse(status_code=502, content=f"Risposta non-JSON e non-SSE da {provider}: {response.text[:2000]}")
    return JSONResponse(status_code=200, content=data)

if __name__ == "__main__":
    print(f"🚀 TRIDENT Gateway :4000 | backend :{LOCAL_PORT} | modello '{LOCAL_MODEL_ID}' | STREAM-PASSTHROUGH ATTIVO")
    uvicorn.run(app, host="0.0.0.0", port=4000)
'''

with open("gateway.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: gateway.py riscritto con PASSTHROUGH streaming (ramo stream=true + ramo blocco).")