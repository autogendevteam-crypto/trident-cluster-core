# TRIDENT AGENTS REGISTRY v1.0
<!-- TOPOLOGY_VERSION: 2026-10-09 -->
<!-- Ultima revisione: Nexus CPO — 10/10/2026 -->

## 🗺️ Mapping Agenti ↔ File ↔ Mistral

| Agente | File | Ruolo | Mistral ID | Modello | Temp | Max Tokens |
|--------|------|-------|------------|---------|------|------------|
| **NEXUS** | `nexus.md` | CPO — Strategia e Coordinamento | `ag_01a078898a1f726d9630f3ce4b85dc35` | `mistral-medium-latest` | 0.5 | 2048 |
| **AXIOM** | `axiom.md` | Database & Data Architect | `ag_01a078c6cc7e776c97133875cca050b3` | `mistral-small-latest` | 0.3 | 1024 |
| **SYNAPSE** | `synapse.md` | n8n Workflow Specialist | `ag_01a078ca005a7098aa9cecf0a0872763` | `mistral-small-latest` | 0.2 | 2048 |
| **VANGUARD** | `vanguard.md` | Infrastructure, Hardware, DevOps, GitHub | `ag_01a078cbfe4b77a49bfe85ffb350acab` | `mistral-small-latest` | 0.3 | 1500 |
| **CORTEX** | `cortex.md` | Knowledge Architect & DPCC (RAG) | `ag_01a078cd851571199752bd6355db27d8` | `mistral-medium-latest` | 0.4 | 2048 |
| **SENTINEL** | `sentinel.md` | Monitoring & SRE Specialist | `ag_01a078cece5f772aa93d15850d4f66aa` | `mistral-small-latest` | 0.2 | 1024 |
| **HERMES** | `hermes.md` | Documentation & Edge Intake Coordinator | `ag_01a078d100397796a03385b4302b9295` | `mistral-medium-latest` | 0.6 | 2048 |

**Totale agenti Mistral: 7**

## 📜 Regole Anti-Drift
1. Ogni file in `agents/` DEVE iniziare con l'header di versionamento.
2. Quando si aggiorna la topologia, incrementare la data in **tutti** i 7 file.
3. Il comando `Select-String -Path agents\*.md -Pattern "TOPOLOGY_VERSION"` deve restituire 7 date IDENTICHE.

## 📊 Stato Allineamento Topologia (Verità Certificate)

| Dato | Valore Certificato | Data Certificazione |
|------|---------------------|---------------------|
| Hardware Themis | Intel Core i5-8400T, 16GB DDR4 | 09/10/2026 |
| AI Locale Prometheus | Solo Bionic 8080 (no Ollama) | 09/10/2026 |
| Qdrant threshold Memos | 0.40 | 08/10/2026 |
| Alibaba Key Token Plan | Scadenza 13/10/2026 18:00 | 09/10/2026 |
| WF5 WhatsApp ID | `quA8GIPC1v2FTeZr` | 10/10/2026 |
| WF6 RAG ID | `UmTftmqCzVELOJeN` | 08/10/2026 |
| UPS Vultech | 1500VA con shutdown graceful | 10/10/2026 |
| Telegram Bot | `@tridentsmartnotes_bot` | 10/10/2026 |
| Monorepo GitHub | `trident-cluster-core` | 08/10/2026 |