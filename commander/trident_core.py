"""
TRIDENT Commander - logica PURA (nessuna dipendenza dalla GUI).

Classi:
  Config          config.json + stato delle chiavi del .env (solo present/missing)
  LogBus          coda thread-safe dei log, colorazione per livello, redazione dei segreti
  PortMonitor     chi occupa una porta (PID + nome), kill, attesa liberazione
  ProcessManager  Gateway (figlio di Commander) e LM Studio (exe o CLI 'lms')
  HealthChecker   3 livelli: API LM Studio, API Gateway, ping di inferenza
  TridentCore     facciata usata dalla GUI e dalla CLI

CLI di test (senza GUI):
    python trident_core.py status | health | run | start-lm | stop-lm | stop-gateway

Sicurezza: i VALORI delle chiavi API non vengono mai stampati, loggati o salvati.
Il .env del gateway e' letto solo in sola lettura, per i booleani present/missing e per
costruire il filtro che oscura eventuali segreti presenti nei log del gateway.
"""
from __future__ import annotations

import argparse
import atexit
import copy
import json
import os
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import psutil
from dotenv import dotenv_values

APP_NAME = "TRIDENT Commander"
APP_VERSION = "1.1.0"
IS_WIN = sys.platform == "win32"

RUNNING, STARTING, STOPPED = "RUNNING", "STARTING", "STOPPED"
LM_PROCESS_KEYS = ("lm studio", "lm-studio", "lmstudio")
LM_EXTRA_NAMES = ("lms", "llmster")


# --------------------------------------------------------------------------- #
# Configurazione
# --------------------------------------------------------------------------- #
def app_dir() -> Path:
    """Cartella dell'app (accanto all'exe se compilato, altrimenti allo script)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


DEFAULT_CONFIG: dict = {
    "paths": {
        "gateway_script": r"C:\ecosistema\TRIDENT_Project\gateway\gateway.py",
        "work_dir": r"C:\ecosistema\TRIDENT_Project\gateway",
        "lm_studio_exe": "",
        "python_exe": "",
        "_note_python_exe": "Vuoto = python dal PATH. Se il gateway usa un venv proprio, imposta qui il suo python.exe.",
        "lms_cli": "",
    },
    "ports": {"gateway": 4000, "lm_studio": 1234},
    "commands": {
        "start_gateway": ["python", "gateway.py"],
        "check_health_endpoint": "http://localhost:4000/v1/models",
    },
    "health": {
        "model": "bionic",
        "prompt": "ping",
        "max_latency_s": 5,
        "timeout_s": 30,
        "api_key_env": "",
    },
    "options": {
        "max_log_lines": 1000,
        "poll_interval_s": 2,
        "stop_gateway_on_exit": True,
        "kill_lm_studio_on_exit": False,
    },
}

_SECRET_NAME = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD)", re.I)


def deep_merge(base: dict, override: dict) -> dict:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


# --------------------------------------------------------------------------- #
# Log bus
# --------------------------------------------------------------------------- #
# Pattern come da specifica: rosso / giallo / verde neon, altrimenti INFO.
_RE_ERR = re.compile(r"(\b(error|critical|fatal|traceback|exception)\b|❌|\b502\b)", re.I)
_RE_WARN = re.compile(r"(\b(warn|warning)\b|⚠|\b429\b)", re.I)
_RE_OK = re.compile(r"(\b(success|passed?)\b|✅|application startup complete|uvicorn running)", re.I)
_RE_OK_CS = re.compile(r"\bOK\b")  # 'OK' maiuscolo (evita "ok" nel testo comune)


def detect_level(line: str) -> str:
    if _RE_ERR.search(line):
        return "ERROR"
    if _RE_WARN.search(line):
        return "WARNING"
    if _RE_OK.search(line) or _RE_OK_CS.search(line):
        return "SUCCESS"
    return "INFO"


class LogBus:
    """Coda thread-safe: (timestamp, sorgente, livello, testo). Oscura i segreti noti."""

    def __init__(self) -> None:
        self.q: queue.Queue = queue.Queue()
        self._secrets: list[str] = []

    def set_secrets(self, values: list[str]) -> None:
        # solo in memoria; i piu' lunghi per primi per evitare sostituzioni parziali
        self._secrets = sorted({v for v in values if len(v) >= 6}, key=len, reverse=True)

    def emit(self, source: str, message: str, level: str | None = None) -> None:
        text = str(message)
        for s in self._secrets:
            if s in text:
                text = text.replace(s, "***")
        for line in text.splitlines():
            if not line.strip():
                continue
            self.q.put((time.strftime("%H:%M:%S"), source, level or detect_level(line), line.rstrip()))


# --------------------------------------------------------------------------- #
# Config loader
# --------------------------------------------------------------------------- #
class Config:
    def __init__(self, path: str | Path | None, bus: LogBus) -> None:
        self.path = Path(path) if path else app_dir() / "config.json"
        self.bus = bus
        self.data: dict = copy.deepcopy(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        try:
            if self.path.exists():
                deep_merge(self.data, json.loads(self.path.read_text(encoding="utf-8-sig")))
            else:
                self.save()
                self.bus.emit("CFG", f"Creato config.json di default: {self.path}", "INFO")
        except Exception as e:  # JSON rotto, permessi...
            self.bus.emit("CFG", f"config.json non leggibile ({e}): uso i valori di default", "ERROR")

    def save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            self.bus.emit("CFG", f"Impossibile salvare config.json: {e}", "ERROR")

    @property
    def env_path(self) -> Path:
        return Path(self.data["paths"]["work_dir"]) / ".env"

    def _read_env(self) -> dict:
        try:
            return dict(dotenv_values(self.env_path)) if self.env_path.is_file() else {}
        except Exception:
            return {}

    def env_status(self) -> dict[str, bool]:
        """Nome variabile segreta -> True se valorizzata. MAI i valori."""
        env = self._read_env()
        return {k: bool((v or "").strip()) for k, v in sorted(env.items()) if _SECRET_NAME.search(k)}

    def secret_values(self) -> list[str]:
        """Solo per il filtro di redazione dei log; non esce mai da questo processo."""
        return [v for k, v in self._read_env().items() if v and _SECRET_NAME.search(k)]

    def validate(self) -> list[tuple[str, str]]:
        p, issues = self.data["paths"], []
        if not Path(p["work_dir"]).is_dir():
            issues.append(("ERROR", f"work_dir non trovata: {p['work_dir']}"))
        if not Path(p["gateway_script"]).is_file():
            issues.append(("ERROR", f"gateway_script non trovato: {p['gateway_script']}"))
        if not self.env_path.is_file():
            issues.append(("WARNING", ".env del gateway non trovato (solo informativo)"))
        return issues


# --------------------------------------------------------------------------- #
# Porte e processi (helper)
# --------------------------------------------------------------------------- #
def _win_flags(*names: str) -> int:
    if not IS_WIN:
        return 0
    flags = 0
    for n in names:
        flags |= getattr(subprocess, n, 0)
    return flags


def _safe_name(proc: psutil.Process) -> str:
    try:
        return proc.name()
    except psutil.Error:
        return "?"


def is_lm_name(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in LM_PROCESS_KEYS) or n.rsplit(".", 1)[0] in LM_EXTRA_NAMES


def find_lm_processes() -> list[psutil.Process]:
    out = []
    for p in psutil.process_iter(["name"]):
        if is_lm_name(p.info.get("name") or ""):
            out.append(p)
    return out


def kill_tree(proc: psutil.Process, timeout: float = 5.0) -> int:
    """Termina un processo e tutti i suoi figli (terminate -> kill). Ritorna quanti ne ha toccati."""
    try:
        targets = proc.children(recursive=True) + [proc]
    except psutil.Error:
        targets = [proc]
    for p in targets:
        try:
            p.terminate()
        except psutil.Error:
            pass
    _, alive = psutil.wait_procs(targets, timeout=timeout)
    for p in alive:
        try:
            p.kill()
        except psutil.Error:
            pass
    if alive:
        psutil.wait_procs(alive, timeout=2.0)
    return len(targets)


def _describe_exc(e: Exception) -> str:
    if isinstance(e, httpx.ConnectError):
        return "connessione rifiutata"
    if isinstance(e, httpx.TimeoutException):
        return "timeout"
    return f"{type(e).__name__}: {e}"


class PortMonitor:
    """Chi occupa una porta TCP e come liberarla."""

    def __init__(self, bus: LogBus) -> None:
        self.bus = bus

    @staticmethod
    def is_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.4) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    @staticmethod
    def _procs(port: int) -> list[psutil.Process]:
        pids: set[int] = set()
        try:
            for c in psutil.net_connections(kind="inet"):
                if c.status == psutil.CONN_LISTEN and c.laddr and c.laddr.port == port and c.pid:
                    pids.add(c.pid)
        except (psutil.AccessDenied, OSError):
            pass
        out = []
        for pid in pids:
            try:
                out.append(psutil.Process(pid))
            except psutil.Error:
                pass
        return out

    def owners(self, port: int) -> list[tuple[int, str]]:
        """[(PID, nome)] dei processi in ascolto sulla porta."""
        return [(p.pid, _safe_name(p)) for p in self._procs(port)]

    def wait_free(self, port: int, timeout: float = 5.0) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if not self.is_listening(port):
                return True
            time.sleep(0.2)
        return not self.is_listening(port)

    def kill_owner(self, port: int) -> list[tuple[int, str]]:
        killed = []
        for proc in self._procs(port):
            if proc.pid <= 4 or proc.pid == os.getpid():
                self.bus.emit("APP", f"Salto PID {proc.pid}: processo protetto", "WARNING")
                continue
            name = _safe_name(proc)
            self.bus.emit("APP", f"Termino {name} (PID {proc.pid}) sulla porta {port}…", "WARNING")
            kill_tree(proc)
            killed.append((proc.pid, name))
        if killed and not self.wait_free(port, 4.0):
            self.bus.emit("APP", f"La porta {port} risulta ancora occupata.", "ERROR")
        return killed


# --------------------------------------------------------------------------- #
# Risultati
# --------------------------------------------------------------------------- #
@dataclass
class ActionResult:
    ok: bool
    code: str
    message: str
    owners: list = field(default_factory=list)  # [(pid, nome)]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    warn: bool = False


@dataclass
class HealthReport:
    checks: list
    diagnosis: str
    elapsed: float

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.ok)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def all_ok(self) -> bool:
        return self.passed == self.total

    @property
    def summary(self) -> str:
        return f"{'✅' if self.all_ok else '❌'} {self.passed}/{self.total}" + (" PASS" if self.all_ok else "")


# --------------------------------------------------------------------------- #
# ProcessManager
# --------------------------------------------------------------------------- #
class ProcessManager:
    def __init__(self, cfg: Config, bus: LogBus, ports: PortMonitor) -> None:
        self.c, self.bus, self.ports = cfg, bus, ports
        self._lock = threading.RLock()
        self._gw_proc: subprocess.Popen | None = None
        self._expected_exit: set[int] = set()

    @property
    def cfg(self) -> dict:
        return self.c.data

    @property
    def gw_port(self) -> int:
        return int(self.cfg["ports"]["gateway"])

    @property
    def lm_port(self) -> int:
        return int(self.cfg["ports"]["lm_studio"])

    # ---- stato ----------------------------------------------------------- #
    def gateway_alive(self) -> bool:
        proc = self._gw_proc
        return proc is not None and proc.poll() is None

    def gateway_state(self) -> tuple[str, str]:
        proc = self._gw_proc
        alive = proc is not None and proc.poll() is None
        if self.ports.is_listening(self.gw_port):
            return RUNNING, (f"avviato da Commander · PID {proc.pid}" if alive else "attivo (processo esterno)")
        if alive:
            return STARTING, "in avvio…"
        return STOPPED, "spento"

    def lm_state(self) -> tuple[str, str]:
        if self.ports.is_listening(self.lm_port):
            return RUNNING, "server in ascolto"
        if find_lm_processes():
            return STARTING, "app aperta · server non attivo"
        return STOPPED, "spento"

    # ---- Gateway --------------------------------------------------------- #
    def _resolve_python(self, exe: str) -> str | None:
        if exe.lower() not in ("python", "python.exe", "python3", "py"):
            return exe
        configured = self.cfg["paths"].get("python_exe") or ""
        if configured and Path(configured).is_file():
            return configured
        found = shutil.which("python") or shutil.which("python3")
        if found:
            return found
        return None if getattr(sys, "frozen", False) else sys.executable

    def start_gateway(self) -> ActionResult:
        p = self.cfg["paths"]
        with self._lock:
            if self.gateway_alive():
                return ActionResult(True, "ALREADY_RUNNING", "Il Gateway è già in esecuzione (avviato da Commander).")
            work_dir = Path(p["work_dir"])
            if not work_dir.is_dir():
                return ActionResult(False, "WORKDIR_MISSING", f"Cartella di lavoro non trovata: {work_dir}")
            if not Path(p["gateway_script"]).is_file():
                return ActionResult(False, "SCRIPT_MISSING", f"gateway.py non trovato: {p['gateway_script']}")
            if self.ports.is_listening(self.gw_port):
                owners = self.ports.owners(self.gw_port)
                who = ", ".join(f"{n} (PID {pid})" for pid, n in owners) or "processo sconosciuto"
                return ActionResult(False, "PORT_BUSY", f"Porta {self.gw_port} già occupata da: {who}", owners)

            cmd = list(self.cfg["commands"]["start_gateway"])
            exe = self._resolve_python(cmd[0])
            if not exe:
                return ActionResult(False, "PYTHON_MISSING", "Python non trovato: imposta paths.python_exe in config.json")
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            try:
                proc = subprocess.Popen(
                    [exe] + cmd[1:], cwd=str(work_dir),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  # stdout+stderr uniti
                    text=True, encoding="utf-8", errors="replace", bufsize=1, env=env,
                    creationflags=_win_flags("CREATE_NO_WINDOW", "CREATE_NEW_PROCESS_GROUP"),
                )
            except OSError as e:
                return ActionResult(False, "SPAWN_FAILED", f"Avvio Gateway fallito: {e}")
            self._gw_proc = proc
            threading.Thread(target=self._pump, args=(proc,), daemon=True, name="gw-log").start()
        self.bus.emit("APP", f"Gateway avviato (PID {proc.pid}): {' '.join([os.path.basename(exe)] + cmd[1:])}", "INFO")
        return ActionResult(True, "STARTED", f"Gateway avviato (PID {proc.pid}).")

    def _pump(self, proc: subprocess.Popen) -> None:
        """Reader thread: riga per riga -> LogBus (il bus e' thread-safe, la GUI lo consuma nel mainloop)."""
        try:
            for line in proc.stdout:  # type: ignore[union-attr]
                self.bus.emit("GW", line)
        except Exception as e:
            self.bus.emit("GW", f"Lettura log interrotta: {e}", "WARNING")
        finally:
            rc = proc.wait()
            if proc.pid in self._expected_exit:
                self._expected_exit.discard(proc.pid)
                self.bus.emit("GW", f"Processo arrestato (exit code {rc})", "INFO")
            elif rc == 0:
                self.bus.emit("GW", "Processo terminato (exit code 0)", "INFO")
            else:
                self.bus.emit("GW", f"Il Gateway si è chiuso in modo inatteso (exit code {rc})", "ERROR")

    def stop_gateway(self, force_external: bool = False) -> ActionResult:
        with self._lock:
            proc = self._gw_proc
        if proc is not None and proc.poll() is None:
            self.bus.emit("APP", f"Arresto Gateway (PID {proc.pid})…", "INFO")
            self._expected_exit.add(proc.pid)
            try:
                kill_tree(psutil.Process(proc.pid))
            except psutil.Error:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass
            return ActionResult(True, "STOPPED", "Gateway arrestato.")
        if self.ports.is_listening(self.gw_port):
            owners = self.ports.owners(self.gw_port)
            if not force_external:
                return ActionResult(False, "EXTERNAL", "Il Gateway è attivo ma non è stato avviato da Commander.", owners)
            killed = self.ports.kill_owner(self.gw_port)
            return ActionResult(True, "STOPPED", f"Gateway esterno terminato ({len(killed)} processo/i).")
        return ActionResult(True, "NOT_RUNNING", "Il Gateway non è in esecuzione.")

    def restart_gateway(self) -> ActionResult:
        r = self.stop_gateway()
        if not r.ok and r.code == "EXTERNAL":
            return r
        self.ports.wait_free(self.gw_port, 5.0)
        return self.start_gateway()

    # ---- LM Studio ------------------------------------------------------- #
    def find_lm_studio_exe(self) -> str | None:
        cands: list = [self.cfg["paths"].get("lm_studio_exe", "")]
        la, pf = os.environ.get("LOCALAPPDATA"), os.environ.get("PROGRAMFILES")
        if la:
            cands += [Path(la) / "Programs" / "LM Studio" / "LM Studio.exe",
                      Path(la) / "LM-Studio" / "LM Studio.exe"]
        if pf:
            cands.append(Path(pf) / "LM Studio" / "LM Studio.exe")
        for c in cands:
            if c and Path(c).is_file():
                return str(c)
        return None

    def set_lm_exe(self, path: str) -> None:
        self.cfg["paths"]["lm_studio_exe"] = path
        self.c.save()
        self.bus.emit("CFG", f"Percorso LM Studio salvato: {path}", "SUCCESS")

    def _find_lms_cli(self) -> str | None:
        configured = self.cfg["paths"].get("lms_cli") or ""
        if configured and Path(configured).is_file():
            return configured
        found = shutil.which("lms")
        if found:
            return found
        guess = Path.home() / ".lmstudio" / "bin" / ("lms.exe" if IS_WIN else "lms")
        return str(guess) if guess.is_file() else None

    def _run_lms(self, lms: str, *args: str, timeout: float = 60.0) -> None:
        try:
            r = subprocess.run(
                [lms, *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=timeout, creationflags=_win_flags("CREATE_NO_WINDOW"),
            )
            out = (r.stdout or "") + (r.stderr or "")
            if out.strip():
                self.bus.emit("LMS", out, "INFO" if r.returncode == 0 else "WARNING")
        except Exception as e:
            self.bus.emit("LMS", f"lms {' '.join(args)} fallito: {e}", "WARNING")

    def _lms_start_server(self, lms: str, delay: float) -> None:
        time.sleep(delay)
        self._run_lms(lms, "server", "start", "--port", str(self.lm_port))
        if self.ports.is_listening(self.lm_port):
            self.bus.emit("LMS", f"Server LM Studio attivo sulla porta {self.lm_port}", "SUCCESS")
        else:
            self.bus.emit("LMS", "Server non ancora attivo: avvialo dalla scheda Developer di LM Studio.", "WARNING")

    def start_lm_studio(self) -> ActionResult:
        if self.ports.is_listening(self.lm_port):
            owners = self.ports.owners(self.lm_port)
            if owners and not any(is_lm_name(n) for _, n in owners):  # porta presa da altro
                who = ", ".join(f"{n} (PID {pid})" for pid, n in owners)
                return ActionResult(False, "PORT_BUSY", f"Porta {self.lm_port} occupata da: {who}", owners)
            return ActionResult(True, "ALREADY_RUNNING", f"LM Studio è già attivo sulla porta {self.lm_port}.")
        lms = self._find_lms_cli()
        app_open = bool(find_lm_processes())
        if not app_open:
            exe = self.find_lm_studio_exe()
            if not exe:
                return ActionResult(False, "NOT_FOUND", "LM Studio.exe non trovato: seleziona il file.")
            try:
                subprocess.Popen(
                    [exe], cwd=str(Path(exe).parent), stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True,
                    creationflags=_win_flags("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP"),
                )
            except OSError as e:
                return ActionResult(False, "SPAWN_FAILED", f"Avvio LM Studio fallito: {e}")
            self.bus.emit("APP", "LM Studio avviato.", "INFO")
        if lms:
            threading.Thread(target=self._lms_start_server, args=(lms, 0.5 if app_open else 6.0),
                             daemon=True).start()
        else:
            self.bus.emit(
                "APP",
                "Se il server non parte da solo, attivalo dalla scheda Developer di LM Studio "
                "(oppure imposta paths.lms_cli per l'avvio automatico).", "INFO")
        return ActionResult(True, "STARTED", "LM Studio in avvio.")

    def stop_lm_studio(self) -> ActionResult:
        lms = self._find_lms_cli()
        if lms and self.ports.is_listening(self.lm_port):
            self._run_lms(lms, "server", "stop", timeout=15.0)
        procs = find_lm_processes()
        if not procs and not self.ports.is_listening(self.lm_port):
            return ActionResult(True, "NOT_RUNNING", "LM Studio non è in esecuzione.")
        for p in procs:
            try:
                kill_tree(p)
            except psutil.Error:
                pass
        if self.ports.is_listening(self.lm_port):
            return ActionResult(False, "STILL_UP", f"La porta {self.lm_port} è ancora in ascolto (servizio esterno?).")
        return ActionResult(True, "STOPPED", "LM Studio terminato.")

    def restart_lm_studio(self) -> ActionResult:
        self.stop_lm_studio()
        self.ports.wait_free(self.lm_port, 5.0)
        return self.start_lm_studio()


# --------------------------------------------------------------------------- #
# HealthChecker
# --------------------------------------------------------------------------- #
class HealthChecker:
    """3 livelli. Distingue GATEWAY DOWN (L2 ko) da BACKEND DOWN (L2 ok ma L3 ko)."""

    def __init__(self, cfg: Config, bus: LogBus, ports: PortMonitor) -> None:
        self.c, self.bus, self.ports = cfg, bus, ports

    def run(self) -> HealthReport:
        t0 = time.time()
        cfg = self.c.data
        h = cfg["health"]
        model, prompt = h.get("model", "bionic"), h.get("prompt", "ping")
        max_lat = float(h.get("max_latency_s", 5))
        timeout_s = float(h.get("timeout_s", 30))
        gw_port, lm_port = int(cfg["ports"]["gateway"]), int(cfg["ports"]["lm_studio"])
        checks: list[Check] = []
        lm_ok = gw_ok = False
        slow = False
        self.bus.emit("HEALTH", "Avvio health check…", "INFO")

        with httpx.Client(timeout=httpx.Timeout(timeout_s, connect=2.0), trust_env=False) as c:
            # L1 - API LM Studio
            name = f"L1 LM Studio API (:{lm_port})"
            try:
                r = c.get(f"http://127.0.0.1:{lm_port}/v1/models", timeout=3.0)
                if r.status_code == 200:
                    try:
                        n = len(r.json().get("data", []))
                    except Exception:
                        n = "?"
                    lm_ok = True
                    checks.append(Check(name, True, f"HTTP 200 · {n} modelli esposti"))
                else:
                    checks.append(Check(name, False, f"HTTP {r.status_code}"))
            except Exception as e:
                checks.append(Check(name, False, _describe_exc(e)))

            # L2 - API Gateway
            name = f"L2 Gateway API (:{gw_port})"
            try:
                r = c.get(cfg["commands"]["check_health_endpoint"], timeout=3.0)
                if r.status_code == 200:
                    gw_ok, warn, detail = True, False, "HTTP 200"
                    try:
                        ids = [m.get("id") for m in r.json().get("data", [])]
                        if ids and model not in ids:
                            warn, detail = True, f"HTTP 200 · ⚠ modello '{model}' non elencato"
                    except Exception:
                        pass
                    checks.append(Check(name, True, detail, warn))
                else:
                    checks.append(Check(name, False, f"HTTP {r.status_code}"))
            except Exception as e:
                checks.append(Check(name, False, _describe_exc(e)))

            # L3 - ping di inferenza (solo se il gateway risponde)
            name = f"L3 Inferenza ('{model}')"
            if gw_ok:
                t = time.perf_counter()
                try:
                    r = c.post(
                        f"http://localhost:{gw_port}/v1/chat/completions",
                        json={"model": model, "messages": [{"role": "user", "content": prompt}],
                              "stream": False, "max_tokens": 16},
                    )
                    dt = time.perf_counter() - t
                    if r.status_code == 200:
                        try:
                            content = (r.json()["choices"][0]["message"]["content"] or "").strip()
                        except Exception:
                            content = ""
                        if not content:
                            checks.append(Check(name, False, "HTTP 200 ma risposta vuota/non valida"))
                        elif dt <= max_lat:
                            checks.append(Check(name, True, f"risposta in {dt:.1f}s"))
                        else:
                            slow = True
                            checks.append(Check(name, False, f"risposta lenta: {dt:.1f}s (soglia {max_lat:g}s)", warn=True))
                    elif r.status_code in (502, 503, 504):
                        checks.append(Check(name, False, f"HTTP {r.status_code} · il gateway non raggiunge il backend"))
                    else:
                        checks.append(Check(name, False, f"HTTP {r.status_code}"))
                except Exception as e:
                    checks.append(Check(name, False, _describe_exc(e) + (f" oltre {timeout_s:g}s" if "timeout" in _describe_exc(e) else "")))
            else:
                checks.append(Check(name, False, "saltato (gateway non raggiungibile)"))

        if all(ch.ok for ch in checks):
            diagnosis = "ALL SYSTEMS GO"
        elif not gw_ok:
            listening = self.ports.is_listening(gw_port)
            diagnosis = "GATEWAY DOWN" + ("" if not listening else " · porta aperta ma risposta non valida")
        elif slow:
            diagnosis = f"BACKEND LENTO · risposta oltre {max_lat:g}s"
        else:
            hint = "LM Studio non risponde" if not lm_ok else "modello non caricato o backend in errore"
            diagnosis = f"BACKEND DOWN · {hint}"

        report = HealthReport(checks, diagnosis, time.time() - t0)
        for ch in checks:
            lvl = "WARNING" if ch.warn else ("SUCCESS" if ch.ok else "ERROR")
            self.bus.emit("HEALTH", f"{'✅' if ch.ok else '❌'} {ch.name}: {ch.detail}", lvl)
        self.bus.emit("HEALTH", f"{report.summary} · {diagnosis} ({report.elapsed:.1f}s)",
                      "SUCCESS" if report.all_ok else "ERROR")
        return report


# --------------------------------------------------------------------------- #
# Facciata
# --------------------------------------------------------------------------- #
class TridentCore:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self.bus = LogBus()
        self.config = Config(config_path, self.bus)
        self.cfg: dict = self.config.data
        self.config_path = self.config.path
        self.bus.set_secrets(self.config.secret_values())
        self.ports = PortMonitor(self.bus)
        self.pm = ProcessManager(self.config, self.bus, self.ports)
        self.health = HealthChecker(self.config, self.bus, self.ports)
        self._lock = threading.RLock()
        self._state = {"gateway": (STOPPED, "spento"), "lm_studio": (STOPPED, "spento")}
        self._stop_evt = threading.Event()
        self._monitor: threading.Thread | None = None
        self._down = False
        atexit.register(self.shutdown)  # rete di sicurezza contro i processi zombie

    # porte
    @property
    def gw_port(self) -> int:
        return self.pm.gw_port

    @property
    def lm_port(self) -> int:
        return self.pm.lm_port

    # config / chiavi
    def validate_config(self) -> list[tuple[str, str]]:
        issues = self.config.validate()
        if not self.pm.find_lm_studio_exe():
            issues.append(("WARNING", "LM Studio.exe non trovato: ti verrà chiesto al primo avvio."))
        return issues

    def env_status(self) -> dict[str, bool]:
        return self.config.env_status()

    def log_env_status(self) -> None:
        st = self.env_status()
        if not st:
            return
        txt = " · ".join(f"{k} {'present' if v else 'MISSING'}" for k, v in st.items())
        self.bus.emit("CFG", f"Chiavi .env: {txt}", "INFO" if all(st.values()) else "WARNING")

    # monitor
    def refresh_state(self) -> dict:
        state = {"gateway": self.pm.gateway_state(), "lm_studio": self.pm.lm_state()}
        with self._lock:
            self._state = state
        return dict(state)

    def get_state(self) -> dict:
        with self._lock:
            return dict(self._state)

    def start_monitor(self) -> None:
        if self._monitor and self._monitor.is_alive():
            return
        self._monitor = threading.Thread(target=self._monitor_loop, daemon=True, name="monitor")
        self._monitor.start()

    def _monitor_loop(self) -> None:
        while not self._stop_evt.is_set():
            try:
                self.refresh_state()
            except Exception:
                pass
            self._stop_evt.wait(float(self.cfg["options"].get("poll_interval_s", 2)))

    # servizi (delegati)
    def gateway_managed_alive(self) -> bool:
        return self.pm.gateway_alive()

    def start_gateway(self) -> ActionResult:
        return self.pm.start_gateway()

    def stop_gateway(self, force_external: bool = False) -> ActionResult:
        return self.pm.stop_gateway(force_external)

    def restart_gateway(self) -> ActionResult:
        return self.pm.restart_gateway()

    def start_lm_studio(self) -> ActionResult:
        return self.pm.start_lm_studio()

    def stop_lm_studio(self) -> ActionResult:
        return self.pm.stop_lm_studio()

    def restart_lm_studio(self) -> ActionResult:
        return self.pm.restart_lm_studio()

    def stop_all(self) -> list[ActionResult]:
        return [self.pm.stop_gateway(force_external=True), self.pm.stop_lm_studio()]

    def set_lm_exe(self, path: str) -> None:
        self.pm.set_lm_exe(path)

    def kill_port_owner(self, port: int) -> list[tuple[int, str]]:
        return self.ports.kill_owner(port)

    def health_check(self) -> HealthReport:
        return self.health.run()

    def shutdown(self) -> None:
        """Idempotente: atexit, segnali, uscita dalla GUI. Chiude l'albero del Gateway figlio."""
        if self._down:
            return
        self._down = True
        self._stop_evt.set()
        try:
            if self.cfg["options"].get("stop_gateway_on_exit", True):
                self.pm.stop_gateway(force_external=False)
            if self.cfg["options"].get("kill_lm_studio_on_exit", False):
                self.pm.stop_lm_studio()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# CLI di test (senza GUI)
# --------------------------------------------------------------------------- #
def _drain_print(core: TridentCore) -> None:
    while True:
        try:
            ts, src, _lvl, line = core.bus.q.get_nowait()
        except queue.Empty:
            return
        print(f"{ts} [{src}] {line}", flush=True)


def cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trident_core", description=f"{APP_NAME} - CLI di test")
    ap.add_argument("command", choices=["status", "health", "run", "start-lm", "stop-lm", "stop-gateway"])
    ap.add_argument("--config", help="percorso di config.json (default: accanto allo script)")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    core = TridentCore(a.config)
    for lvl, msg in core.validate_config():
        core.bus.emit("CFG", msg, lvl)
    code = 0

    if a.command == "status":
        for k, (st, det) in core.refresh_state().items():
            print(f"{k:10s} {st:9s} {det}")
        core.log_env_status()
    elif a.command == "health":
        rep = core.health_check()
        code = 0 if rep.all_ok else 1
    elif a.command == "start-lm":
        r = core.start_lm_studio()
        core.bus.emit("APP", r.message, "SUCCESS" if r.ok else "ERROR")
        _drain_print(core)
        time.sleep(8)  # lascia lavorare 'lms server start' in background
    elif a.command == "stop-lm":
        r = core.stop_lm_studio()
        core.bus.emit("APP", r.message, "SUCCESS" if r.ok else "ERROR")
    elif a.command == "stop-gateway":
        r = core.stop_gateway(force_external=True)
        core.bus.emit("APP", r.message, "SUCCESS" if r.ok else "ERROR")
    elif a.command == "run":
        r = core.start_gateway()
        core.bus.emit("APP", r.message, "SUCCESS" if r.ok else "ERROR")

        def _stop(*_):  # SIGINT/SIGTERM/SIGBREAK -> uscita pulita (il finally chiude il Gateway)
            raise KeyboardInterrupt

        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
            sig = getattr(signal, name, None)
            if sig is not None:
                try:
                    signal.signal(sig, _stop)
                except (ValueError, OSError):
                    pass
        try:
            while r.ok and core.gateway_managed_alive():
                _drain_print(core)
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\nCtrl+C: chiusura…")
        finally:
            core.shutdown()
        code = 0 if r.ok else 1
    _drain_print(core)
    return code


if __name__ == "__main__":
    sys.exit(cli())
