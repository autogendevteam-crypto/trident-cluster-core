# EMBEDDER_SPEC v1.1 — Specifica Embedder text-embedding-bge-m3 Prometheus

## §A — Identità dell'Embedder

- **Software**: LM Studio (nome interno: Bionic)
- **Host**: Prometheus (192.168.8.129)
- **URL LAN**: http://192.168.8.129:1234/v1/embeddings
- **URL locale**: http://localhost:1234/v1/embeddings
- **Model ID**: text-embedding-bge-m3
- **Quantizzazione**: Q4_K_M (437.78 MB)
- **Percorso modello**: D:\AI_Models\gpustack\bge-m3-GGUF\
- **Dimensione vettore**: 1024
- **Metrica Qdrant**: Cosine
- **Modalità server**: OpenAI-compatible, JIT loading ATTIVO
- **Binding**: 0.0.0.0:1234 (ponte netsh → 127.0.0.1:1235)

## §B — Contratto API (OpenAI-Compatible)

### Request
```json
{
  "model": "text-embedding-bge-m3",
  "input": "testo del chunk o della query"
}