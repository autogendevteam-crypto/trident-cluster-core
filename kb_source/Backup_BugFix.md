# Strategia di Backup 3-2-1 e Fix
- **Primario**: /mnt/backup (SATA) - pg_dump, tar, scp (Giornaliera 02:00)
- **Ridondante**: /mnt/backup2 (USB) - rsync (Giornaliera 02:30)
- **Off-site**: Google Drive - rclone (Domenica 04:00)
- **Fix Applicato**: Verifica integrità post-sync con rclone check e logging su PostgreSQL.
