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
