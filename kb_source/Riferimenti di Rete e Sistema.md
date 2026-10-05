# 🌐 Trade Bot Solutions — Riferimenti di Rete e Sistema

**Data aggiornamento:** 19 Agosto 2026
**Manutentore:** Morris / Team Sistemistico
**Stato:** Produzione

---

## 🏠 Rete Locale (LAN)

### THEMIS — Server (192.168.8.124)

| Servizio | Indirizzo | Note |
|---|---|---|
| Nextcloud Web | `http://192.168.8.124:8080` | Interfaccia web + WebDAV |
| Nextcloud WebDAV | `http://192.168.8.124:8080/remote.php/dav/` | API file (WF1, WF3) |
| Memos UI | `http://192.168.8.124:5230` | Note rapide |
| Memos API | `http://192.168.8.124:5230/api/v1/memos` | POST note (WF4) |
| PostgreSQL | `192.168.8.124:5432` | DB `cluster_db` |
| Qdrant | `http://192.168.8.124:6333` | Vector DB (RAG futuro) |
| SSH | `ssh morris@192.168.8.124` | Accesso remoto |

### ATLAS — Workstation (192.168.8.125)

| Servizio | Indirizzo | Note |
|---|---|---|
| n8n (LAN) | `http://192.168.8.125:5678` | Solo rete locale |
| n8n (pubblico) | `https://n8n.trade-bot-solutions.com/` | Via Cloudflare Tunnel |
| SSH | `ssh morris2@192.168.8.125` | Accesso remoto |

---

## 🌍 Accesso Pubblico

| Servizio | URL | Note |
|---|---|---|
| n8n UI + Webhook | `https://n8n.trade-bot-solutions.com/` | Cloudflare Tunnel (container `cloudflared` su Atlas) |

**Tunnel:** nessuna porta aperta sul router. Se i webhook muoiono: `docker restart tunnel` su Atlas.

---

## 🤖 Bot Telegram

| Bot | Username | Credenziale n8n | Uso |
|---|---|---|---|
| Smart Notes Bot | `@tridentsmartnotes_bot` | `Smart Notes Bot` | WF4 input note |
| Trident Notifiche | `@trident_notif_bot` | `Telegram account` | Notifiche WF2a/WF3 |

### ID Utenti Autorizzati

| Utente | ID Telegram | Ruolo |
|---|---|---|
| Morris | `708137568` | Owner |
| Angela | `6249861407` | Collaboratrice |
| Giovanna | ⏳ PENDING | Acquisire via `@userinfobot` |

---

## 🧩 Workflow n8n (ID e Stato)

| Workflow | ID | Active | Funzione |
|---|---|---|---|
| 1_Ingestione_Dati | `UXmbneyUWCAWCquW` | 🟢 | Cron 20:00 → leggi notes.txt → chiama WF2a |
| 2_Analisi_AI_MultiProvider | `1gDPjUGSAEzJo48d` | 🟢 | Analisi Gemini → report Markdown |
| 3_Consegna_Notifica | `6vJnOJ4PzmKfU3nO` | 🟢 | Upload report Nextcloud + Telegram |
| 4_SmartNotes_Telegram |