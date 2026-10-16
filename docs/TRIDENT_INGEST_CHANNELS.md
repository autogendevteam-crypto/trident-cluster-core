# TRIDENT SECTION I - INGEST CHANNELS, QDRANT SYNTAX, DOC CONVENTION, HONEST AUDIT (2026-10-16)
Closes the gaps that made the Level-4 plan over-claim anchoring. These are CANONICAL.

## I1. TWO DISTINCT INGEST CHANNELS (do not mix them)
CHANNEL A - OBSCURA LOCAL PIPELINE (for BULK TECHNICAL DOCUMENTATION):
- Source: a LOCAL folder on Atlas, convention /home/morris2/trident_kb/<domain>/ (e.g. n8n_core_docs, docker_runtime, llm_api_openai, kubernetes_docs).
- Vehicle: an Obscura script (Python/Node) that reads local files, cleans, chunks, embeds via Gateway :4000, upserts via Qdrant :6333.
- Does NOT touch Nextcloud. Does NOT touch WF8. WF8 is irrelevant here.
- Use this channel for: downloaded docs (n8n, Docker, OpenAI, Kubernetes, security, architecture, langchain).

CHANNEL B - WF8 AUTO INGEST (for USER FILES in Nextcloud inbox):
- Source: Nextcloud WebDAV RAG_Inbox/ (http://192.168.8.124:8080/remote.php/dav/files/admin/RAG_Inbox/).
- Vehicle: n8n workflow WF8 (skbAetbUG4I2AKwW), SCHEDULE trigger.
- Tech debt OPEN: hardcoded Nextcloud creds in Code nodes; random UUIDs (non-idempotent). Until fixed, WF8 stays active=false and schedule OFF.
- Use this channel ONLY for: documents a user drops into RAG_Inbox, not for bulk technical docs.

ROUTING RULE: downloaded technical documentation -> CHANNEL A (Obscura local). User inbox files -> CHANNEL B (WF8). Kubernetes docs = CHANNEL A. Therefore a Kubernetes ingest plan must NOT involve Nextcloud RAG_Inbox and must NOT inherit WF8 hardcoded-credential debt. If a plan routes bulk docs through WF8/Nextcloud, it has confused the channels.

## I2. QDRANT CALL SYNTAX (exact, not generic REST)
- COUNT: POST http://192.168.8.124:6333/collections/trade_bot_knowledge/points/count  with body {} (all) or {"filter":{"must":[{"key":"source_type","match":{"value":"<domain>"}}]}} (filtered). It is POST with a JSON body, NOT GET with a ?filter= query string.
- SEARCH: POST .../points/search with body {"vector":[...],"filter":{"must":[{"key":"source_type","match":{"value":"<domain>"}}]},"with_payload":true,"limit":N}. The "vector" MUST come from Gateway :4000/v1/embeddings, NOT from the raw question text. Qdrant searches vectors, not strings.
- SCROLL (inspect payload without a vector): POST .../points/scroll with body {"limit":N,"with_payload":true,"with_vector":false,"filter":{...}}.
- RETRIEVAL FLOW IS TWO CALLS, NOT ONE: (1) embed the question via :4000/v1/embeddings -> take data[0].embedding; (2) search Qdrant with THAT vector + filter. Anyone who writes a single Qdrant call passing the question text is wrong.

## I3. document_type CONVENTION
- Pattern: <domain>_reference | <domain>_tutorial | <domain>_example | <domain>_manifest. Align to existing values (n8n_reference, docker_reference, openai_reference, security_reference, architecture_pattern, project_*).
- For Kubernetes use: kubernetes_reference, kubernetes_manifest, kubernetes_tutorial. Do NOT invent off-pattern values like "yaml-manifest" or "markdown-guide".

## I4. HONEST ANCHORING AUDIT (protocol, fixes the S3/L4 over-claim)
- ALL_ANCHORED is permitted ONLY if every concrete value you used (endpoint, HTTP method, JSON field, enum value, folder path, syntax form) is LITERALLY present in sections A-I.
- If you extended a rule with a detail that is plausible but NOT written in A-I, label it EXTENSION (not anchored), or NOT_IN_CONTEXT. Do not fold it into ALL_ANCHORED.
- Over-claiming anchoring is as serious as hallucinating: it hides the boundary of your memory and lets a half-correct plan pass review. When in doubt, mark EXTENSION.
- Symptom to watch: you feel "sure" because the context is rich. Rich-but-not-exhaustive context is exactly where over-claim happens (S3 recipe, L4 routing+syntax). Silence (empty context) you handle honestly (S2, S4). The danger zone is partial knowledge.
