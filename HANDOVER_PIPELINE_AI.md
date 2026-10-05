
# 🛡️ AGGIORNAMENTO ARCHITETTURA E PROCEDURE (v2.1 - Ottobre 2026)

## 1. 🗺️ Mappatura Aggiornata dei Servizi e Porte
*Attenzione: Le porte esposte sono state razionalizzate per sicurezza e coerenza con il nuovo proxy.*

| Servizio | Nodo | Porta Interna | Porta Esterna / Proxy | Note |
| :--- | :--- | :--- | :--- | :--- |
| **Nextcloud** | Themis (192.168.8.124) | 8080 | 8080 | WebDAV e interfaccia web |
| **Qdrant** | Themis (192.168.8.124) | 6333 | 6333 | Vector Database (KB) |
| **Bionic (LLM/Embedder)** | Prometheus (192.168.8.129) | 1234 | **8080** | **CORRETTO:** L'accesso esterno/Documentato avviene ora tramite proxy sulla 8080. La porta 1235 è **DEPRECATATA E RIMOSSA**. |
| **n8n** | Atlas (192.168.8.125) | 5678 | 443 (HTTPS) | Esposto tramite Cloudflare Tunnel |
| **Memos** | Themis (192.168.8.124) | 5230 | 5230 | Gestione note rapide |

---

## 2. 📱 Integrazione Workflow WF5 (WhatsApp Bot)
Il workflow **WF5** è ora parte integrante della pipeline di notifica e interazione.
- **Trigger:** Webhook in ingresso da provider WhatsApp.
- **Funzione:** Ricezione comandi testuali, inoltro a WF2 (Analisi AI) o WF6 (RAG), e risposta diretta all'utente.
- **Credenziali:** Gestite esclusivamente tramite l'archivio credenziali di n8n. **Mai** hardcoded nei nodi.

---

## 3. 🌐 Configurazione Tunnel Cloudflare
L'accesso pubblico a n8n non avviene più tramite porte forwardate sul router, ma tramite un tunnel sicuro.
- **Dominio:** `n8n.trade-bot-solutions.com`
- **Nodo di terminazione:** Atlas (192.168.8.125)
- **Vantaggio:** Nessuna porta aperta sul firewall locale, HTTPS gestito automaticamente, protezione DDoS di base.

---

## 4. 🚨 Procedura di Disaster Recovery (DR) per n8n
*Lezione appresa: La perdita del volume di dati di n8n comporta la perdita di workflow, credenziali e cronologie di esecuzione.*

**Politica di Backup:**
1. Il volume Docker `infra_n8n_data` deve essere incluso nel backup giornaliero automatico.
2. I file JSON dei workflow sono versionati in questa singola repository come backup secondario e fonte di verità per il deployment.

---

## 5. 🔒 Regole di Sicurezza GitHub (CI/CD)
La repository è protetta da GitHub Actions:
- ✅ **Validazione JSON:** Qualsiasi push di file `.json` viene validato sintatticamente.
- ✅ **Secret Scanning:** Il push viene bloccato automaticamente se vengono rilevati pattern di token o password in chiaro.
