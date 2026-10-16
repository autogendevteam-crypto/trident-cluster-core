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
