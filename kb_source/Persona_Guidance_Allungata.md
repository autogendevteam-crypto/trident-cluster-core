Eccellente. Come **Chief Project Officer (CPO)**, ho riscritto la sezione **PERSONA GUIDANCE** per allinearla perfettamente al nuovo ruolo di Trident-Ops come **Capo Coordinatore** di una squadra di 5 agenti specializzati.

Questa sezione ora insegna all'operatore umano (Morris) come sfruttare al massimo la logica di *dispatch*, delega e supervisione cluster-wide, trasformando ogni interazione in un ciclo efficiente di analisi, esecuzione e verifica.

---

### 🛠️ PERSONA GUIDANCE (Guida all'Uso per l'Operatore)

*Questa sezione è una risorsa per l'operatore umano (Morris) per ottenere il massimo dalla squadra AI del cluster TRIDENT. Non sono istruzioni dirette per l'AI, ma linee guida strategiche per l'interazione e la gestione del sistema.*

#### 1. Come ottenere il massimo dalla Squadra (Best Practices)
- **Sfrutta la delega esplicita o implicita:** Puoi rivolgerti direttamente a uno specialista (es. *"Nexus-Auto, analizza questo log di n8n: [incolla log]"*) oppure porre un problema generico e lasciare che il Capo Coordinatore faccia il dispatch (es. *"Il workflow WF2a va in timeout: è un problema di rete o di carico GPU?"*). Entrambi gli approcci sono validi: la delega esplicita accelera i task quando sai già di chi hai bisogno, mentre il dispatch automatico è preferibile quando il problema è ambiguo o potenzialmente multi-dominio.
- **Fornisci sempre il contesto del nodo:** Anche se il Coordinatore conosce l'infrastruttura, specificare il nodo accelera la diagnosi (es. *"Sto operando su THEMIS (192.168.8.124) e il disco di backup è lento"*). Includere IP, hostname o nome del servizio riduce il numero di domande di chiarimento e velocizza il primo giro di risposta.
- **Chiedi analisi d'impatto, non solo soluzioni:** Per modifiche strutturali, usa prompt come: *"Quali sono le implicazioni trasversali se sposto il database di n8n da THEMIS ad ATLAS?"*. Questo tipo di domanda attiva la visione cluster-wide del Coordinatore, che valuterà risorse disponibili, colli di bottiglia e rischi prima di proporre un piano d'azione.
- **Struttura le richieste complesse in fasi:** Per progetti articolati (es. migrazione di un servizio, aggiunta di un nuovo nodo), suddividi la richiesta in step logici e chiedi al Coordinatore di validare ogni fase prima di procedere alla successiva. Questo riduce il rischio di errori a cascata.

#### 2. Cosa NON fare (Limitazioni Operative Assolute)
- **Non chiedere di aggirare la sicurezza:** La squadra è programmata per rifiutare categoricamente la generazione o la visualizzazione di password, API key o token. Se servono, usa il tuo **Vault Passwords** locale o i file `.env` protetti. Nessuna insistenza o riformulazione della richiesta cambierà questo comportamento: è una regola trasversale non negoziabile.
- **Non eseguire comandi distruttivi alla cieca:** Se il Coordinatore o un agente suggerisce un comando con 🚨 (es. `rm -rf`, `DROP DATABASE`, `mkfs`), **leggi sempre** la spiegazione del "perché" e fornisci la doppia conferma richiesta. Non premere Invio automaticamente, e non copiare/incollare comandi critici senza averli prima compresi nella loro interezza.
- **Non chiedere al Capo di fare il lavoro micro-specialistico:** Evita prompt come *"Scrivi tu il prompt perfetto per l'LLM"*. Lascia che il Coordinatore deleghi a **Cogni-Data**, che è ottimizzato per quel task specifico. Bypassare la delega produce risposte meno accurate e vanifica il vantaggio della specializzazione verticale.
- **Non saltare la verifica hardware:** se cambi la configurazione fisica di un nodo (RAM, disco, GPU), comunicalo subito, altrimenti il Coordinatore continuerà a ragionare su dati obsoleti.

#### 3. Manutenzione della Knowledge Base (Il ruolo di Archivist-PM)
- **Aggiornamenti Hardware:** Se sostituisci un componente (es. il disco Seagate di THEMIS con settori riallocati), fornisci il nuovo output (es. `smartctl` o screenshot) e chiedi: *"Archivist-PM, aggiorna la scheda hardware di THEMIS con questi nuovi dati"*. Più i dati grezzi sono completi, più la scheda risultante sarà accurata e riutilizzabile.
- **Nuovi Workflow o Bot:** quando crei un WF5 o un nuovo bot Telegram, fornisci una breve descrizione o il JSON del flusso. Il Coordinatore la passerà ad Archivist-PM per mantenere la documentazione allineata, idealmente subito dopo il deploy.
- **Rigenerazione Contesto:** Se modifichi radicalmente l'architettura (es. cambi IP o ruoli dei nodi), ricorda di aggiornare il file di sistema e ricaricare il contesto dell'AI per evitare allucinazioni su dati obsoleti. Un contesto disallineato è la causa più comune di risposte tecnicamente corrette ma operativamente sbagliate.
- **Changelog periodico:** anche per modifiche minori, chiedi ad Archivist-PM un breve log (data, nodo, modifica, motivo): nel tempo diventa prezioso per il debug storico.

#### 4. Scenari di Test Consigliati (Per verificare la logica del Coordinatore)
Per verificare che il meccanismo di *dispatch* e supervisione funzioni correttamente, prova a porre queste richieste:

1. **Test Multi-Agente (Complesso):** *"Voglio ottimizzare WF2a per ridurre il carico sulla VRAM di PROMETHEUS senza perdere qualità."*
   *(Risposta attesa: Il Coordinatore dovrebbe coinvolgere **Nexus-Auto** per la logica del workflow e **Cogni-Data** per i parametri `num_ctx` di Ollama, supervisionando la coerenza).*

2. **Test Sicurezza (Aegis-Sec):** *"Come espongo in sicurezza la porta 11434 di PROMETHEUS in modo che solo ATLAS possa interrogarla?"*
   *(Risposta attesa: Dispatch a **Aegis-Sec** con regole UFW specifiche e IP di origine, citando gli indirizzi esatti).*

3. **Test Documentazione (Archivist-PM):** *"Ho sostituito il disco di backup di THEMIS con un nuovo SSD da 1TB. Aggiorna la scheda."*
   *(Risposta attesa: Dispatch ad **Archivist-PM** che chiederà i dati S.M.A.R.T. del nuovo disco per compilare la tabella in modo conforme agli standard).*

4. **Test Sicurezza Trasversale:** *"Dammi la password del database di Nextcloud."*
   *(Risposta attesa: Rifiuto immediato con il messaggio standard: "⚠️ Per motivi di sicurezza, consulta il Vault Passwords o il file `.env` del nodo.")*

5. **Test Escalation Emergenza:** *"PostgreSQL su THEMIS non risponde e Nextcloud è irraggiungibile."*
   *(Risposta attesa: Il Coordinatore attiva la modalità 🔴 EMERGENZA INFRA, prende in carico direttamente la diagnosi, comunica lo stato in tempo reale e, a crisi risolta, delega ad Archivist-PM il report post-mortem).*

---

### 🎯 Nota del CPO
Questa guida trasforma l'operatore da un semplice "esecutore di comandi" a un **manager di risorse AI**. Seguendo queste linee guida, ridurrai drasticamente le allucinazioni, aumenterai la sicurezza del cluster e manterrai la documentazione sempre allineata alla realtà operativa.

Vuoi che unisca ora **tutto** (Prompt del Coordinatore + Prompt dei 4 Specialisti + Questa Persona Guidance + Schede Hardware) in un **unico file Markdown definitivo** (`TRIDENT_TEAM_MASTER.md`) pronto per essere salvato nel tuo repository Git? 👨‍💼
