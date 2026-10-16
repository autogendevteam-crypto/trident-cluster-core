# 🔱 TRIDENT COMMANDER

Dashboard desktop (Windows, dark mode) per controllare **LM Studio** e il **TRIDENT Gateway** senza aprire finestre PowerShell.

## File del progetto

| File | Ruolo |
|---|---|
| `main_app.py` | Interfaccia grafica (CustomTkinter) + icona nella system tray |
| `trident_core.py` | Logica pura: processi, monitor, health check, log. Testabile da CLI |
| `config.json` | Percorsi, porte, parametri dell'health check |
| `requirements.txt` | Dipendenze Python |
| `setup.bat` | Crea il venv `.venv` e installa le dipendenze |
| `avvia.bat` | Lancia l'app senza console (esegue il setup al primo avvio) |
| `build_exe.bat` | Compila `dist\TRIDENT_Commander.exe` con PyInstaller |

## Installazione (3 passi)

1. Copia la cartella dove vuoi (es. `C:\ecosistema\TRIDENT_Project\commander`).
2. Controlla i percorsi in `config.json` (vedi sotto).
3. Doppio clic su **`avvia.bat`**. Al primo avvio crea l'ambiente e installa tutto da solo (serve Python 3.9+ nel PATH).

In alternativa, a mano: `pip install -r requirements.txt` e poi `python main_app.py`.

## Configurazione (`config.json`)

| Chiave | Significato |
|---|---|
| `paths.gateway_script` / `paths.work_dir` | `gateway.py` e relativa cartella di lavoro |
| `paths.lm_studio_exe` | Percorso di `LM Studio.exe`. Se sbagliato, l'app prova i percorsi standard e poi ti fa scegliere il file (e lo salva) |
| `paths.python_exe` | Python da usare per il Gateway. Vuoto = `python` dal PATH. **Consigliato** se usi un venv del gateway |
| `paths.lms_cli` | Opzionale: percorso di `lms.exe` (CLI di LM Studio) per avviare/fermare il server in automatico |
| `ports.gateway` / `ports.lm_studio` | 4000 / 1234 |
| `commands.start_gateway` | Comando di avvio, eseguito in `work_dir` |
| `health.model`, `health.prompt` | Modello e prompt del ping (default `bionic` / `ping`) |
| `health.max_latency_s` | Sotto questa soglia l'inferenza locale è considerata OK (default 5) |
| `health.api_key_env` | Riservato: lasciare vuoto. I valori delle chiavi non vengono mai letti né mostrati; Commander segnala solo `present`/`MISSING` per le variabili segrete del `.env` |
| `options.stop_gateway_on_exit` | Ferma il Gateway quando esci da Commander (default `true`) |
| `options.kill_lm_studio_on_exit` | Chiude anche LM Studio all'uscita (default `false`) |
| `options.max_log_lines` | Righe massime nella console (default 1000) |

Il pulsante **⚙ Config** nell'header apre il file. Le modifiche si applicano al riavvio dell'app.

## Come si usa

| Elemento | Cosa fa |
|---|---|
| **Card LM STUDIO / GATEWAY** | LED + stato (verde online, arancione in avvio, rosso offline) e pulsanti Start / Stop / Restart |
| **RUN HEALTH CHECK** | 3 livelli: L1 API LM Studio, L2 API Gateway, L3 ping di inferenza. Esito tipo `✅ 3/3 PASS` più diagnosi: `GATEWAY DOWN` (L2 ko) oppure `BACKEND DOWN` (L2 ok, L3 ko) |
| **STOP ALL SERVICES** | Ferma Gateway e LM Studio |
| **Console** | stdout/stderr del Gateway e eventi dell'app, colorati per livello. Auto-scroll on/off, Clear Logs, buffer a 1000 righe |
| **Header** | `ALL SYSTEMS GO` / `DEGRADED` / `OFFLINE` |
| **Tray** | La **X** minimizza nella tray. Tasto destro: Show Window, Restart Gateway, Stop All Services, Exit Application. L'icona cambia colore con lo stato |

### Casi critici gestiti

- **Processi zombie**: all'uscita (anche via `atexit` e segnali) il Gateway figlio viene chiuso con tutto il suo albero di processi. Se l'app crolla di colpo, al riavvio la porta occupata viene rilevata.
- **Porta occupata**: errore in rosso nei log e finestra "Force Kill Port Owner?" con nome e PID del processo.
- **LM Studio spento**: l'health check distingue *Gateway Down* da *Backend Down*.
- **Istanza singola**: una seconda copia di Commander non si avvia.

## Test da riga di comando (senza GUI)

```
python trident_core.py status
python trident_core.py health
python trident_core.py run            # avvia il gateway e mostra i log, Ctrl+C per uscire
python trident_core.py start-lm | stop-lm | stop-gateway
```

## Creare l'eseguibile

Doppio clic su `build_exe.bat`. Ottieni `dist\TRIDENT_Commander.exe` e una copia di `config.json` accanto: tienili nella stessa cartella.

## Problemi comuni

| Sintomo | Causa / rimedio |
|---|---|
| "Python non trovato" | Imposta `paths.python_exe` con il percorso di `python.exe` |
| `python` apre il Microsoft Store | Disattiva gli alias "App execution aliases" per Python, oppure usa `paths.python_exe` |
| LM Studio si apre ma il LED resta arancione | Il server locale non è attivo: avvialo dalla scheda *Developer*, oppure imposta `paths.lms_cli` |
| Health check: L2 fallisce con `HTTP 401` | Il gateway richiede un'autenticazione che Commander (fase 1) non invia: verifica la configurazione del gateway |
| Modello `bionic` "non elencato" | Avviso, non errore: cambia `health.model` se l'alias è diverso (per il locale: `bionic`, `local` o `coder`) |
| L'app non parte con `pythonw` | Controlla `crash.log` nella cartella dell'app |

## Fase 2 (non inclusa)

Switch del modello attivo nel `.env` / integrazione con Cline: da valutare dopo aver stabilizzato la fase 1.
