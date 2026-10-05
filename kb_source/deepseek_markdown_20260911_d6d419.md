# SISTEMA DI BACKUP AUTOMATIZZATO — TRIDENT CLUSTER

## 1. PANORAMICA

Il cluster TRIDENT utilizza una strategia di backup **3-2-1** con automazione via cron su Themis.
Tutti i backup sono centralizzati su HDD esterni dedicati e sincronizzati su un mirror ridondante.

**Nodo responsabile:** Themis (192.168.8.124)
**Disco backup primario:** /dev/sda → `/mnt/backup`
**Disco backup ridondante:** /dev/sde1 → `/mnt/backup2`

---

## 2. CRON JOB ATTIVI (utente morris su Themis)

| Orario | Script | Frequenza |
|--------|--------|-----------|
| 0 2 * * * | /home/morris/backup_db.sh | Ogni notte alle 02:00 |
| 30 2 * * * | /home/morris/sync_backup_ridondante.sh | Ogni notte alle 02:30 |
| 0 3 * * 0 | /home/morris/backup_weekly_config.sh | Domenica alle 03:00 |
| 30 3 * * 0 | /home/morris/backup_weekly_atlas.sh | Domenica alle 03:30 |
| 0 4 * * 0 | /home/morris/backup_tutti_i_drive.sh | Domenica alle 04:00 |

---

## 3. DETTAGLIO DEI BACKUP

### 3.1 Backup PostgreSQL (giornaliero)

| Campo | Valore |
|-------|--------|
| Script | /home/morris/backup_db.sh |
| Frequenza | Ogni notte alle 02:00 |
| Contenuto | Dump database PostgreSQL (n8n_db + nextcloud_db) |
| Destinazione | /mnt/backup/postgres_backups/db_backup_YYYYMMDD.sql.gz |
| Formato nome | db_backup_20260825.sql.gz |
| Dimensione tipica | ~1.4 MB compresso (crescita ~100 KB/giorno) |
| Retention | ~30 giorni |

### 3.2 Backup Configurazioni (settimanale)

| Campo | Valore |
|-------|--------|
| Script | /home/morris/backup_weekly_config.sh |
| Frequenza | Domenica alle 03:00 |
| Contenuto | .env, docker-compose.yml, N8N_ENCRYPTION_KEY |
| Destinazione | /mnt/backup/config/ |
| Permessi | 600 (solo morris) |
| Retention | 90 giorni |

**File prodotti:**
- `homelab_YYYYMMDD.env`
- `docker-compose_YYYYMMDD.yml`
- `n8n_encryption_key.txt` (CHIAVE CRITICA — sovrascritta ogni domenica)

### 3.3 Backup n8n su Atlas (settimanale)

| Campo | Valore |
|-------|--------|
| Script | /home/morris/backup_weekly_atlas.sh |
| Frequenza | Domenica alle 03:30 |
| Contenuto | Volume dati completo di n8n su Atlas (sqlite + credenziali + storico) |
| Destinazione | /mnt/backup/atlas/n8n_atlas_YYYYMMDD.tar.gz |
| Metodo | SSH su Atlas → `docker cp n8n:/home/node/.n8n` → tar → scp su Themis |
| Dimensione tipica | ~1.1 MB compresso |
| Retention | 90 giorni |

**Flusso interno:**