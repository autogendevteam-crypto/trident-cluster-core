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

