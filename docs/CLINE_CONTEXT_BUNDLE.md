# CLINE CONTEXT BUNDLE - TRIDENT
Generated: 2026-10-16 (rev with sections A-I)
Canonical order: .clinerules, PROJECT_CONTEXT.md, PROJECT_DEEP_CONTEXT.md (A-E), TRIDENT_CANONICAL_ADDENDA.md (F,G,H), TRIDENT_INGEST_CHANNELS.md (I).
AI endpoint canonical = http://192.168.8.129:4000. :8080 DEPRECATED. Bionic :1234 localhost-only, never called from Atlas.
Qdrant SELF-CONTAINED: retrieval reads payload.text_content, never re-reads Memos/Nextcloud. Qdrant does SEARCH, Gateway :4000 does EMBEDDINGS+CHAT.
WF7,WF8 = SCHEDULE triggers (cyclic). Only WF6 = webhook. Ingest IDs deterministic (UUIDv5/sha256 source_path+chunk_index); random UUIDs = tech debt.
TWO INGEST CHANNELS (I1): bulk technical docs = Obscura LOCAL folder (NOT Nextcloud/WF8); user inbox files = WF8. Do not mix.
Qdrant count/search = POST with JSON body (I2); search vector comes from :4000, two calls not one.
Honest audit (I4): ALL_ANCHORED only if every concrete value is literally in A-I; else EXTENSION/NOT_IN_CONTEXT.
---

## .clinerules

# CLINE RULES — TRIDENT PROJECT (CANONICAL 2026-10-16)

Sei un ingegnere operativo del cluster TRIDENT.
Modalità attuale: DEV / PRAGMATIC / MAKE IT WORK.

## AUTORITÀ DELLE FONTI

In questo workspace, le fonti canonicali sono:

1. `.clinerules`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/SECURITY_DEBT.md`

Qualsiasi documento storico che indichi `http://192.168.8.129:8080` come endpoint AI attivo è DEPRECATED.
L’endpoint AI canonico attuale è il Gateway TRIDENT:

http://192.168.8.129:4000

## TOPOLOGIA CLUSTER

- Prometheus: 192.168.8.129
  - Ruolo: AI engine locale + Gateway TRIDENT
  - Gateway TRIDENT: http://192.168.8.129:4000
  - Bionic locale: http://127.0.0.1:1234
  - Bionic è localhost-only. Non deve essere chiamato direttamente da Atlas.

- Atlas: 192.168.8.125
  - Ruolo: n8n automation hub
  - n8n: http://192.168.8.125:5678

- Themis: 192.168.8.124
  - Ruolo: storage, vector memory, database layer
  - Qdrant: http://192.168.8.124:6333
  - Nextcloud WebDAV: http://192.168.8.124:8080
  - Memos: http://192.168.8.124:5230
  - PostgreSQL: 5432
  - Redis: 6379

- Hermes: 192.168.8.167
  - Ruolo: amministrazione / SSH client

## CONTRATTI AI CANONICI

### Gateway TRIDENT

Base URL:

http://192.168.8.129:4000

Route certificate:

- GET /v1/models
- POST /v1/chat/completions
- POST /v1/embeddings

### Embedding canonico

Endpoint:

POST http://192.168.8.129:4000/v1/embeddings

Modello:

text-embedding-bge-m3

Dimensione vettore attesa:

1024

### Chat locale canonica

Endpoint:

POST http://192.168.8.129:4000/v1/chat/completions

Alias gateway:

local

Modello reale sottostante:

qwen2.5-coder-7b-instruct

## ENDPOINT VIETATI / OBSOLETI

- http://192.168.8.129:8080/v1/embeddings → DECOMMISSIONED
- http://192.168.8.129:8080/v1/chat/completions → DECOMMISSIONED
- http://192.168.8.129:1234/... da Atlas → VIETATO, perché Bionic è localhost-only

## WORKFLOW N8N CANONICI

### WF6 RAG BLINDATO

ID canonicalizzato in questa sessione:

XJHhKIzFHeI0oUJT

Ruolo:

Query RAG via webhook/search.

Collection letta:

trade_bot_knowledge

Nota:
Se la UI n8n mostra un ID diverso, fermati e segnala mismatch. Non mescolare ID vecchi e nuovi.

### WF7 Memos Indexer

ID:

2DpFWRwfsK6QMhH4

Ruolo:

Indicizza Memos in Qdrant.

### WF8 Auto Ingest RAG V5 FIXED

ID:

skbAetbUG4I2AKwW

Ruolo:

Nextcloud RAG_Inbox → chunk → embedding → Qdrant upsert → WebDAV MOVE.

Tech debt noto:

- credenziali Nextcloud hardcoded nei nodi Code;
- UUID randomici non idempotenti;
- non attivare schedule finché non bonificato.

## KNOWLEDGE BASE QDRANT

Collection:

trade_bot_knowledge

Vector size:

1024

Distance metric:

Cosine

Baseline punti certificata di recente:

circa 1035+

Domini presenti tramite payload `source_type`:

- project_trident
- n8n_docs
- docker_docs
- openai_api
- security_auth
- architecture_patterns
- llm_framework_langchain
- self_knowledge

## REGOLE OPERATIVE PER CLINE

1. Prima di codificare, leggi `.clinerules` e `docs/PROJECT_CONTEXT.md`.
2. Se serve contesto tecnico esterno, interroga la KB o usa i documenti locali nella cartella progetto.
3. In dev mode, priorità a far funzionare il flusso.
4. Segnala sempre il tech debt alla fine del task.
5. Prima di modificare workflow n8n o script pipeline, fai backup/export.
6. Non stampare mai segreti, API key, password, token o credenziali.
7. Dopo ogni modifica, verifica health dei servizi toccati:
   - Gateway :4000
   - Qdrant :6333
   - n8n :5678
   - Nextcloud :8080
   - Memos :5230

## OUTPUT ATTESO

Quando completi un task, fornisci:

- cosa hai fatto/modificato;
- comandi di verifica eseguiti ed esito;
- eventuale tech debt registrato;
- prossimo passo consigliato.


---

## docs/PROJECT_CONTEXT.md

# TRIDENT CONTEXT — UPDATED 2026-10-16

## Verità operativa attuale

Il cluster TRIDENT usa il Gateway TRIDENT come entrypoint AI canonico.

Endpoint AI canonico:

http://192.168.8.129:4000

Il vecchio proxy Bionic su porta 8080 è decommissioned.
Non deve più essere usato come endpoint embedding o chat.

Il motore Bionic locale resta attivo solo su:

http://127.0.0.1:1234

Questo endpoint è localhost-only su Prometheus e non deve essere chiamato da Atlas.

## Nodi

- Prometheus: 192.168.8.129
  - Gateway TRIDENT: http://192.168.8.129:4000
  - Bionic locale: http://127.0.0.1:1234

- Atlas: 192.168.8.125
  - n8n: http://192.168.8.125:5678

- Themis: 192.168.8.124
  - Qdrant: http://192.168.8.124:6333
  - Nextcloud WebDAV: http://192.168.8.124:8080
  - Memos: http://192.168.8.124:5230
  - PostgreSQL: 5432
  - Redis: 6379

- Hermes: 192.168.8.167
  - amministrazione / SSH

## Contratti AI

### Models

GET http://192.168.8.129:4000/v1/models

### Embeddings

POST http://192.168.8.129:4000/v1/embeddings

Modello:

text-embedding-bge-m3

Dimensione vettore:

1024

### Chat

POST http://192.168.8.129:4000/v1/chat/completions

Alias locale:

local

Modello sottostante:

qwen2.5-coder-7b-instruct

## Workflow principali

### WF6 RAG BLINDATO

ID:

XJHhKIzFHeI0oUJT

Ruolo:

Query RAG via webhook/search.

### WF7 Memos Indexer

ID:

2DpFWRwfsK6QMhH4

Ruolo:

Indicizza Memos in Qdrant.

### WF8 Auto Ingest RAG V5 FIXED

ID:

skbAetbUG4I2AKwW

Ruolo:

Nextcloud RAG_Inbox → chunk → embedding → Qdrant upsert → WebDAV MOVE.

Tech debt:

- credenziali Nextcloud hardcoded;
- UUID randomici non idempotenti.

## Knowledge Base

Collection:

trade_bot_knowledge

Vector size:

1024

Distance:

Cosine

Punti attuali stimati:

circa 1035+

Source type principali:

- project_trident
- n8n_docs
- docker_docs
- openai_api
- security_auth
- architecture_patterns
- llm_framework_langchain
- self_knowledge

## Regola anti-confusione

Se un documento storico dice che:

- Un vecchio endpoint proxy dismesso viene citato solo come esempio deprecato.
- Un vecchio riferimento a n8n che chiama un endpoint dismesso viene citato solo come esempio deprecato.
- Un vecchio ID workflow non canonico viene citato solo come esempio deprecato.

quel documento è stale/deprecated.

La verità canonical attuale è:

- Gateway :4000 è l’entrypoint AI;
- :8080 è decommissioned;
- WF6 ID canonical di sessione è XJHhKIzFHeI0oUJT.



---

## docs/PROJECT_DEEP_CONTEXT.md (A-E)

# PROJECT DEEP CONTEXT - TRIDENT (CANONICAL 2026-10-16)

## A. QDRANT E AUTO-CONTENUTO (la retrieval NON torna alla sorgente)
Il testo di ogni chunk vive DENTRO Qdrant, nel campo payload.text_content.
Quando WF6 risponde: embedda la DOMANDA via Gateway :4000/v1/embeddings (text-embedding-bge-m3, dim 1024); cerca il vettore in Qdrant (SEARCH, non embeddings); Qdrant restituisce i punti con payload.text_content; WF6 assembla contesto da QUEL testo; chiama Gateway :4000/v1/chat/completions (alias local) per generare.
IMPORTANTE: in fase di query Memos/Nextcloud NON vengono mai riletti. Sono sorgenti SOLO in ingest (WF7/WF8). Qdrant e magazzino autonomo. "WF6 retrieve da Memos" e FALSO: WF6 legge dal payload di Qdrant.

## B. RUOLI DEI COMPONENTI (chi fa quale verbo)
- Gateway :4000 -> EMBEDDINGS e CHAT (motore AI).
- Qdrant :6333 -> SEARCH su vettori e STOCCA payload. NON fa embeddings.
- Bionic :1234 -> motore dietro Gateway, localhost-only su Prometheus.
- Memos :5230 -> sorgente note, letta SOLO da WF7 in ingest.
- Nextcloud :8080 -> sorgente documenti RAG_Inbox, letta SOLO da WF8 in ingest.
- n8n Atlas :5678 -> orchestratore.
- Cline -> ingegnere operativo.
Verbi: embed->Gateway, search->Qdrant, generate->Gateway, store->Qdrant, read source->Memos(WF7)/Nextcloud(WF8).

## C. SEMANTICA DEI TRIGGER (reattivo vs ciclico)
- WF6 -> WEBHOOK (event-driven, reattivo). Domanda arriva -> parte. /webhook/rag.
- WF7 -> SCHEDULE (ciclico/batch). NON reattivo: parte a intervalli, legge Memos. Nota nuova visibile solo dopo il ciclo.
- WF8 -> SCHEDULE (ciclico/batch). NON c e webhook su upload Nextcloud.
Conseguenze: latenza nota->RAG = ciclo WF7; tech debt UUID: se WF8 fallisce a meta (upsert OK, MOVE KO) il ciclo successivo ri-legge e DUPLICA; NON esistono webhook da Memos/Nextcloud.

## D. MAPPA SINTOMI -> COMPONENTE -> CHECK
- Tutti AI giu insieme (connection refused) -> Gateway :4000 giu -> curl :4000/v1/models (200). Blast radius WF6+WF7+WF8. Da Atlas NON vedi :1234 (localhost).
- Embedding KO / dim sbagliata -> :4000/v1/embeddings -> probe, len==1024.
- Fonti sbagliate -> retrieval (Qdrant search) -> scroll con filter source_type, confronta section_title vs domanda, score attesi >0.55. Embedding OK+punti OK+fonti KO = retrieval.
- Fonti giuste ma risposta fuori tema -> generazione -> passa stesso contesto a :4000/v1/chat/completions da solo; se male, e modello/prompt.
- Nota nuova non compare -> NONE (latenza schedule WF7), non bug -> check ultima exec WF7.
- Duplicati Qdrant -> WF8 UUID randomici + re-run partial failure -> count vs file unici in Processed.

## E. SCOPO PROGETTO + CATENA 1->2->3
SCOPO TRIDENT (Trade Bot Solutions): piattaforma automazione con agenti AI LOCALI. Cluster n8n + LLM locale + memoria vettoriale persistente; automatizza raccolta/analisi/consegna informazioni tenendo dati in casa. Due pipeline condividono sorgenti e motore AI:
- PIPELINE MEMORIA (RAG): WF7+WF8 ingest, WF6 query. Costruisce/interroga memoria.
- PIPELINE REPORT (catena 1->2->3): raccogli->analizza->consegna.
  1_Ingestione_Dati (UitpMk9sVo44RYTK): entry point, raccoglie/normalizza da Memos/Nextcloud/testo, passa avanti. NON fa AI/RAG.
  2_Analisi_AI_MultiProvider_FIXED (kVkamtiliHz7uyHu): analizza con AI multi-provider (locale->cloud->fallback), produce report. Tech debt: chiama :1234 diretto (deve :4000), modello 14B non cert (cluster 7B), typo Groq "openai/ gpt-oss-120b".
  3_Consegna_Notifica_FIXED (6vJnOJ4PzmKfU3nO): consegna report Telegram + salva Nextcloud. Effetti esterni, Tier 3, gate prima produzione.
Differenza: 1->2->3 PRODUCE report; WF6/7/8 COSTRUISCONO/INTERROGANO memoria. Non confondere.


---

## docs/TRIDENT_CANONICAL_ADDENDA.md (F,G,H)

# TRIDENT CANONICAL ADDENDA - F, G, H (2026-10-16)
These sections are CANONICAL and close the gaps surfaced by the Level-3 impact-reasoning test.

## SEZIONE F - THEMIS POWER PROTECTION (UPS / NUT / graceful) - VERIFIED FACTS + EXPLICIT GAPS
VERIFIED (configured and observed this session):
- Themis is protected by an UPS Vultech 1500 over USB. NUT driver nutdrv_qx, 24V nominal (2x12V series), runtimecal 30min@100% / 60min@50%.
- Healthy state: ups.status OL (on line), battery.charge ~95%.
- Blackout path: OL -> OB; if battery crosses threshold, upsmon runs SHUTDOWNCMD "/sbin/shutdown -h +0"; systemd stops Docker; containers stop with flush (Postgres WAL, Qdrant sync, Nextcloud cleanup); filesystem unmounted; upsdrvctl shutdown cuts power after offdelay 30s; on grid return, ondelay 180s then power restored (BIOS AC recovery Always On).
- NOTIFYCMD upssched handles OB/LOWBATT notifications (e.g. Telegram).
RECOVERY DISTINCTION (this is what S4 needs, now anchored):
- After a power loss, Nextcloud "maintenance mode" and Qdrant collection empty/404 are DISTINCT faults. Nextcloud maintenance = lock/DB recovery, recoverable. Qdrant empty/404 = volume not remounted OR corruption.
- If the graceful shutdown COMPLETED before killpower, Qdrant should have flushed and the volume should remount clean (collection status green). If the blackout cut power BEFORE graceful finished (battery exhausted, or NUT not firing), corruption risk is real.
- Therefore: after reboot, BEFORE trusting the RAG, verify Qdrant collection is mounted and status green (GET /collections/trade_bot_knowledge), and verify the Docker volume is actually remounted. A 404/empty collection right after reboot means "not remounted or not flushed", not "knowledge lost forever" - the source files (Nextcloud RAG_Inbox/Processed, Memos) may still allow re-ingest, BUT see the gap below.
EXPLICIT GAPS (NOT verified this session - say NOT_IN_CONTEXT if asked to rely on them):
- Whether the Qdrant Docker volume has a restart policy that guarantees clean remount.
- Whether Qdrant snapshots / WAL are configured for crash durability.
- Whether the graceful NUT shutdown actually reached Qdrant flush in past events (no post-mortem evidence captured).
- Re-ingest after a Qdrant wipe is NOT automatic for WF8: WF8 reads RAG_Inbox, and already-processed files live in RAG_Inbox/Processed, so a wipe is not silently self-healed by the next cycle.

## SEZIONE G - DIAGNOSTIC PROTOCOL (fixes the S1 premature-exclusion slip)
Before diagnosing any symptom:
1. ENUMERATE every component in the topology that COULD produce the symptom (Gateway :4000, Qdrant :6333, Bionic :1234 behind gateway, Memos, Nextcloud, n8n, the specific workflow).
2. ELIMINATE one by one with a CONCRETE check (endpoint + expected result). Never exclude a component without a check that rules it out.
3. If two components can both explain the symptom, KEEP THE FORK OPEN until a check separates them. Do not collapse to the first plausible hypothesis.
4. Special rule for "wrong answers": this is compatible with BOTH retrieval (wrong sources) AND generation (right sources, bad wording). The fork is: scroll Qdrant with the question + filter source_type, compare section_title vs question and look at score. Sources wrong -> retrieval. Sources right but answer off-topic -> generation. Do NOT pre-commit to generation.

## SEZIONE H - INGEST RECIPES, PAYLOAD SCHEMA, FRESHNESS, OBSCURA PATTERN (fixes S2/S3: makes the fix ANCHORED, not invented)
H1. DETERMINISTIC ID (the recipe that was missing, so S3 "COVERED" becomes legitimately true):
- qdrant_id = UUIDv5(namespace, source_path + "#chunk" + chunk_index)  OR  sha256(source_path + "_chunk" + chunk_index) truncated.
- RULE: same source + same chunk_index => same id. A re-run is an OVERWRITE (upsert), never a duplicate.
- NEVER use generateUUID()/random for ingest. Random ids + partial failure (upsert OK, MOVE KO) = duplicates on next cycle.
H2. CANONICAL PAYLOAD SCHEMA (every chunk carries these fields):
- chunk_id, source_type, document_type, source_url OR source_path, section_title, text_content, language, status (active | superseded), chunk_index, total_chunks, ingested_at (ISO8601), tags[].
H3. FRESHNESS / RETRIEVAL BIAS (the mechanism S2 lacked, now anchored):
- To stop a stale chunk winning over a fresh one: filter status=active at search time; when several chunks match, boost/sort by ingested_at desc (or apply time-decay).
- When re-ingesting an UPDATED document, mark the old chunks status=superseded (or delete-by-filter on source_path) so they stop competing in retrieval. Without this, cosine similarity alone can let a 3-month-old chunk outrank last week's.
H4. OBSCURA PIPELINE PATTERN (reuse verbatim for ANY new domain, e.g. Kubernetes):
- acquire/clean: strip nav/sidebar/footer/cookie banners; KEEP headings, code blocks, tables.
- chunk: split on headings (## / ###), target ~512-900 chars, overlap ~80-120, NEVER split a code block or a parameter table mid-way.
- embed: POST http://192.168.8.129:4000/v1/embeddings , model text-embedding-bge-m3 , expect dim 1024 ; batch 8-16, fallback 1 if batch fails.
- upsert: PUT http://192.168.8.124:6333/collections/trade_bot_knowledge/points?wait=true , batch 16-50 points, deterministic id (H1) + payload (H2).
- verify: read count pre/post; retrieval test with filter source_type=<new_domain>; expect score > 0.55 and section_title pertinent to the question.
- SAME collection trade_bot_knowledge, separated LOGICALLY by payload.source_type. Do NOT create a new collection unless there is a hard technical reason.


---

## docs/TRIDENT_INGEST_CHANNELS.md (I - NEW)

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


---

## docs/SECURITY_DEBT.md

# SECURITY DEBT TRIDENT

Questo file registra il debito tecnico di sicurezza del cluster TRIDENT.
In modalità dev/pragmatica non blocca il lavoro, ma va chiuso prima della produzione reale.

## 1. WF8 Auto Ingest — credenziali Nextcloud hardcoded ✅ Risolto

Workflow:

WF8_Auto_Ingest_RAG_V5_FIXED

ID:

skbAetbUG4I2AKwW

Problema:

Nei nodi Code sono presenti credenziali Nextcloud hardcoded, ad esempio tramite:

Buffer.from('admin:<password-compromised>').toString('base64')

Rischio:

- password esposta in export JSON;
- password visibile in chat/log/report;
- accesso WebDAV potenzialmente compromesso;
- impossibile ruotare la credenziale senza modificare il workflow.

Azione richiesta:

1. Ruotare la password admin Nextcloud su Themis.
2. Aggiornare le credenziali n8n su Atlas.
3. Rimuovere Buffer.from hardcoded dai nodi Code.
4. Sostituire con credential n8n oppure lettura da environment variable.
5. Verificare audit log Nextcloud per accessi anomali.

## 2. WF8 Auto Ingest — UUID randomici non idempotenti ✅ Risolto

Problema:

WF8 usa UUID randomici come ID Qdrant.

Rischio:

Se lo stesso file viene processato due volte, ad esempio perché:

- Qdrant upsert riesce;
- WebDAV MOVE fallisce;
- il file resta in RAG_Inbox;
- il prossimo ciclo lo rilegge di nuovo;

allora si possono creare duplicati nella collection.

Azione richiesta:

Sostituire generateUUID() con ID deterministico basato su:

file_name + chunk_index

Esempio concettuale:

sha256(fileName + "_chunk" + chunkIndex)

oppure UUIDv5 con namespace + source_path + chunk_index.

Obiettivo:

stesso file + stesso chunk = stesso ID Qdrant.

## 3. Webhook RAG pubblico aperto in dev mode

Endpoint testato:

https://n8n.trade-bot-solutions.com/webhook/rag

Stato attuale:

In dev mode può essere aperto per test.

Rischio in produzione:

- chiunque conosca l’URL può interrogare Qdrant;
- consumo embedding/LLM non controllato;
- possibile esposizione metadata;
- possibile prompt injection sulla knowledge base.

Azione richiesta prima di produzione:

- auth obbligatoria;
- rate limit;
- payload validation;
- Cloudflare Access/WAF o equivalente;
- nessun segreto nei log;
- test senza auth che restituisca 401/403.

## 4. API key n8n esposta in chat/report

Problema:

Una API key n8n usata per backup/patch è stata esposta in chat o report.

Azione richiesta:

1. Revocare la key esposta.
2. Generare nuova key con scope minimo.
3. Non incollarla in chat.
4. Verificare che i backup non contengano secret in chiaro.
5. Controllare audit log n8n.

## 5. WF2 — violazione architetturale endpoint

Problema:

WF2 chiama diretto Bionic :1234 invece di usare Gateway :4000.

Rischio:

- bypass del control plane;
- dipendenza da endpoint localhost-only;
- possibile fallimento da Atlas;
- perdita di logging centralizzato.

Azione richiesta:

Repoint WF2 verso:

http://192.168.8.129:4000/v1/chat/completions

## 6. WF2 — modello locale non certificato

Problema:

WF2 references qwen2.5-coder-14b-instruct, ma il cluster certificato espone qwen2.5-coder-7b-instruct tramite alias local.

Azione richiesta:

Allineare WF2 al modello certificato oppure configurare correttamente il gateway.

## 7. WF2 — typo modello Groq

Problema:

È stato rilevato un typo tipo:

"openai/ gpt-oss-120b"

Azione richiesta:

Correggere lo spazio errato nel nome modello.

## 8. Qdrant esposto in LAN

Stato attuale:

Qdrant è raggiungibile in LAN su:

http://192.168.8.124:6333

Rischio in produzione:

Se Themis è raggiungibile da host non autorizzati, la vector DB è esposta.

Azione richiesta:

- firewall Themis consenta 6333 solo da Atlas e Prometheus;
- valutare API key Qdrant se disponibile;
- separare read/write se possibile;
- backup collection periodico.


---

## docs/CONTEXT.md sanitized

# TRIDENT CONTEXT — UPDATED 2026-10-16

## Verità operativa attuale

Il cluster TRIDENT usa il Gateway TRIDENT come entrypoint AI canonico.

Endpoint AI canonico:

http://192.168.8.129:4000

Il vecchio proxy Bionic su porta 8080 è decommissioned.
Non deve più essere usato come endpoint embedding o chat.

Il motore Bionic locale resta attivo solo su:

http://127.0.0.1:1234

Questo endpoint è localhost-only su Prometheus e non deve essere chiamato da Atlas.

## Nodi

- Prometheus: 192.168.8.129
  - Gateway TRIDENT: http://192.168.8.129:4000
  - Bionic locale: http://127.0.0.1:1234

- Atlas: 192.168.8.125
  - n8n: http://192.168.8.125:5678

- Themis: 192.168.8.124
  - Qdrant: http://192.168.8.124:6333
  - Nextcloud WebDAV: http://192.168.8.124:8080
  - Memos: http://192.168.8.124:5230
  - PostgreSQL: 5432
  - Redis: 6379

- Hermes: 192.168.8.167
  - amministrazione / SSH

## Contratti AI

### Models

GET http://192.168.8.129:4000/v1/models

### Embeddings

POST http://192.168.8.129:4000/v1/embeddings

Modello:

text-embedding-bge-m3

Dimensione vettore:

1024

### Chat

POST http://192.168.8.129:4000/v1/chat/completions

Alias locale:

local

Modello sottostante:

qwen2.5-coder-7b-instruct

## Workflow principali

### WF6 RAG BLINDATO

ID:

XJHhKIzFHeI0oUJT

Ruolo:

Query RAG via webhook/search.

### WF7 Memos Indexer

ID:

2DpFWRwfsK6QMhH4

Ruolo:

Indicizza Memos in Qdrant.

### WF8 Auto Ingest RAG V5 FIXED

ID:

skbAetbUG4I2AKwW

Ruolo:

Nextcloud RAG_Inbox → chunk → embedding → Qdrant upsert → WebDAV MOVE.

Tech debt:

- credenziali Nextcloud hardcoded;
- UUID randomici non idempotenti.

## Knowledge Base

Collection:

trade_bot_knowledge

Vector size:

1024

Distance:

Cosine

Punti attuali stimati:

circa 1035+

Source type principali:

- project_trident
- n8n_docs
- docker_docs
- openai_api
- security_auth
- architecture_patterns
- llm_framework_langchain
- self_knowledge

## Regola anti-confusione

Se un documento storico dice che:

- Un vecchio endpoint proxy dismesso viene citato solo come esempio deprecato.
- Un vecchio riferimento a n8n che chiama un endpoint dismesso viene citato solo come esempio deprecato.
- Un vecchio ID workflow non canonico viene citato solo come esempio deprecato.

quel documento è stale/deprecated.

La verità canonical attuale è:

- Gateway :4000 è l’entrypoint AI;
- :8080 è decommissioned;
- WF6 ID canonical di sessione è XJHhKIzFHeI0oUJT.



