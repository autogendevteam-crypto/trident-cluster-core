"""
TRIDENT COMMANDER - dashboard di controllo (CustomTkinter + pystray)

Avvio:  python main_app.py     (o avvia.bat)
La logica vera sta in trident_core.py; qui c'è solo l'interfaccia.

Regola thread: tutto ciò che tocca i widget gira nel thread principale.
I worker e le callback della tray mettono funzioni in `ui_q`, che il loop `_poll` esegue.
"""
from __future__ import annotations

import os
import queue
import signal
import socket
import sys
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

try:
    import pystray
except Exception:  # tray non disponibile: l'app funziona comunque
    pystray = None

from trident_core import (
    APP_NAME, APP_VERSION, RUNNING, STARTING, STOPPED,
    ActionResult, HealthReport, TridentCore, app_dir,
)

# --------------------------------------------------------------------------- #
# Stile
# --------------------------------------------------------------------------- #
BG, PANEL, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, DIM = "#c9d1d9", "#8b949e"
NEON, GREEN, RED, ORANGE, BLUE = "#00ff41", "#2ea043", "#f85149", "#d29922", "#58a6ff"
CONSOLE_BG = "#010409"

LEVEL_COLORS = {"INFO": TEXT, "WARNING": "#e3b341", "ERROR": "#ff4444", "SUCCESS": NEON}
STATUS_COLOR = {RUNNING: NEON, STARTING: ORANGE, STOPPED: RED}
STATUS_LABEL = {RUNNING: "ONLINE", STARTING: "IN AVVIO", STOPPED: "OFFLINE"}
MONO = "Consolas"

LOCK_PORT = 47831  # blocco istanza singola (solo localhost)


def make_icon(color: str, size: int = 64) -> Image.Image:
    """Scudo con tridente, colorato in base allo stato."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64
    shield = [(32, 3), (58, 12), (58, 34), (32, 61), (6, 34), (6, 12)]
    pts = [(x * s, y * s) for x, y in shield]
    w = max(2, int(4 * s))
    d.polygon(pts, fill="#0d1117")
    d.line(pts + [pts[0]], fill=color, width=w, joint="curve")
    for x in (22, 32, 42):  # tre punte
        d.line([(x * s, 16 * s), (x * s, 34 * s)], fill=color, width=w)
    d.line([(22 * s, 34 * s), (42 * s, 34 * s)], fill=color, width=w)  # base
    d.line([(32 * s, 34 * s), (32 * s, 52 * s)], fill=color, width=w)  # manico
    return img


# --------------------------------------------------------------------------- #
# Card di servizio
# --------------------------------------------------------------------------- #
class ServiceCard(ctk.CTkFrame):
    def __init__(self, master, title, port_text, fonts, on_start, on_stop, on_restart):
        super().__init__(master, fg_color=PANEL, border_color=BORDER, border_width=1, corner_radius=8)
        self._last = None
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        top.grid_columnconfigure(1, weight=1)
        self.led = ctk.CTkLabel(top, text="●", font=ctk.CTkFont(size=24), text_color=RED, width=26)
        self.led.grid(row=0, column=0)
        ctk.CTkLabel(top, text=title, font=fonts["h2"], text_color=TEXT).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.status = ctk.CTkLabel(top, text="OFFLINE", font=fonts["mono_b"], text_color=RED)
        self.status.grid(row=0, column=2)

        self.detail = ctk.CTkLabel(self, text="", font=fonts["mono_s"], text_color=DIM,
                                   anchor="w", justify="left", wraplength=270)
        self.detail.grid(row=1, column=0, sticky="ew", padx=14, pady=(4, 0))
        ctk.CTkLabel(self, text=port_text, font=fonts["mono_s"], text_color=BLUE, anchor="w").grid(
            row=2, column=0, sticky="ew", padx=14)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        for i in range(3):
            btns.grid_columnconfigure(i, weight=1, uniform="b")
        self.buttons = [
            ctk.CTkButton(btns, text="▶ Start", width=84, fg_color="#238636", hover_color=GREEN,
                          font=fonts["mono_b"], command=on_start),
            ctk.CTkButton(btns, text="■ Stop", width=84, fg_color="#da3633", hover_color=RED,
                          font=fonts["mono_b"], command=on_stop),
            ctk.CTkButton(btns, text="↻ Restart", width=84, fg_color="#1f6feb", hover_color=BLUE,
                          font=fonts["mono_b"], command=on_restart),
        ]
        for i, b in enumerate(self.buttons):
            b.grid(row=0, column=i, padx=3)

    def set_state(self, status: str, detail: str) -> None:
        if (status, detail) == self._last:
            return
        self._last = (status, detail)
        color = STATUS_COLOR[status]
        self.led.configure(text_color=color)
        self.status.configure(text=STATUS_LABEL[status], text_color=color)
        self.detail.configure(text=detail)

    def set_busy(self, busy: bool) -> None:
        for b in self.buttons:
            b.configure(state="disabled" if busy else "normal")


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME}")
        self.geometry("1120x800")
        self.minsize(940, 660)
        self.configure(fg_color=BG)

        self.core = TridentCore()
        self.ui_q: queue.Queue = queue.Queue()
        self.max_lines = int(self.core.cfg["options"].get("max_log_lines", 1000))
        self._busy: set[str] = set()
        self._quitting = False
        self._tray_notified = False
        self._last_global: str | None = None
        self._last_bar = ""
        self.tray = None

        self.fonts = {
            "title": ctk.CTkFont(family=MONO, size=22, weight="bold"),
            "h2": ctk.CTkFont(family=MONO, size=15, weight="bold"),
            "mono": ctk.CTkFont(family=MONO, size=12),
            "mono_b": ctk.CTkFont(family=MONO, size=12, weight="bold"),
            "mono_s": ctk.CTkFont(family=MONO, size=11),
        }
        self._build_ui()
        self._set_window_icon()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._install_signals()

        bus = self.core.bus
        bus.emit("APP", f"{APP_NAME} v{APP_VERSION} avviato", "SUCCESS")
        bus.emit("APP", f"Config: {self.core.config_path}", "INFO")
        for lvl, msg in self.core.validate_config():
            bus.emit("CFG", msg, lvl)
        self.core.log_env_status()  # solo present/missing, mai i valori
        self._refresh_keys()

        self.core.start_monitor()
        self._setup_tray()
        self.after(100, self._poll)

    # ---- UI -------------------------------------------------------------- #
    def _build_ui(self) -> None:
        f = self.fonts
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="🔱  TRIDENT COMMANDER", font=f["title"], text_color=NEON).grid(
            row=0, column=0, padx=16, pady=12)
        ctk.CTkButton(header, text="⚙ Config", width=86, fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT, hover_color=BORDER, font=f["mono"],
                      command=self.open_config).grid(row=0, column=2, padx=8)
        self.global_lbl = ctk.CTkLabel(header, text="● OFFLINE", font=f["h2"], text_color=RED)
        self.global_lbl.grid(row=0, column=3, padx=16)

        # Corpo
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ns", padx=(12, 6), pady=12)

        self.card_lm = ServiceCard(
            left, "LM STUDIO", f"porta {self.core.lm_port}", f,
            on_start=lambda: self._async("lm", self._work_lm_start),
            on_stop=lambda: self._async("lm", self._work_lm_stop),
            on_restart=lambda: self._async("lm", self._work_lm_restart),
        )
        self.card_lm.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.card_gw = ServiceCard(
            left, "GATEWAY", f"porta {self.core.gw_port}", f,
            on_start=self.act_gw_start, on_stop=self.act_gw_stop, on_restart=self.act_gw_restart,
        )
        self.card_gw.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.health_btn = ctk.CTkButton(
            left, text="▶  RUN HEALTH CHECK", height=56, font=f["h2"],
            fg_color="#1f6feb", hover_color=BLUE, command=self.act_health)
        self.health_btn.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        self.health_summary = ctk.CTkLabel(
            left, text="—", font=ctk.CTkFont(family=MONO, size=28, weight="bold"),
            text_color=DIM, anchor="w")
        self.health_summary.grid(row=3, column=0, sticky="ew", padx=4)
        self.health_result = ctk.CTkLabel(
            left, text="Nessun controllo eseguito.", font=f["mono_s"], text_color=DIM,
            anchor="w", justify="left", wraplength=290)
        self.health_result.grid(row=4, column=0, sticky="ew", padx=4)
        self.keys_lbl = ctk.CTkLabel(
            left, text="", font=f["mono_s"], text_color=DIM, anchor="w", justify="left", wraplength=290)
        self.keys_lbl.grid(row=5, column=0, sticky="ew", padx=4, pady=(10, 0))

        ctk.CTkButton(left, text="■  STOP ALL SERVICES", height=36, font=f["mono_b"],
                      fg_color="transparent", border_width=1, border_color=RED, text_color=RED,
                      hover_color="#3a1618", command=self.act_stop_all).grid(
            row=6, column=0, sticky="ew", pady=(14, 0))

        # Console
        right = ctk.CTkFrame(body, fg_color=PANEL, border_color=BORDER, border_width=1, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(right, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bar, text="CONSOLE", font=f["h2"], text_color=TEXT).grid(row=0, column=0, sticky="w")
        self.autoscroll = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(bar, text="Auto-scroll", variable=self.autoscroll, font=f["mono_s"],
                      progress_color=GREEN).grid(row=0, column=1, padx=10)
        ctk.CTkButton(bar, text="Clear Logs", width=90, font=f["mono"], fg_color="#21262d",
                      hover_color=BORDER, command=self.clear_logs).grid(row=0, column=2)

        self.console = ctk.CTkTextbox(right, font=f["mono"], fg_color=CONSOLE_BG, text_color=TEXT,
                                      wrap="word", border_width=0, corner_radius=6)
        self.console.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        for lvl, col in LEVEL_COLORS.items():
            self.console.tag_config(lvl, foreground=col)
        self.console.tag_config("ts", foreground="#6e7681")
        self.console.tag_config("src", foreground=BLUE)
        self.console.configure(state="disabled")

        self.statusbar = ctk.CTkLabel(right, text="", font=f["mono_s"], text_color=DIM, anchor="w")
        self.statusbar.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 6))

        # Footer
        footer = ctk.CTkLabel(
            self, text=f"{APP_NAME} v{APP_VERSION}   •   config: {self.core.config_path}",
            font=f["mono_s"], text_color=DIM, anchor="w")
        footer.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 6))

    def _set_window_icon(self) -> None:
        try:
            self._icon_ref = ImageTk.PhotoImage(make_icon(NEON, 64))
            # CTk reimposta la propria icona dopo ~200 ms: la sovrascriviamo dopo
            self.after(300, lambda: self.iconphoto(False, self._icon_ref))
        except Exception:
            pass

    def _install_signals(self) -> None:
        def handler(*_):
            self.ui(self._quit)
        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
            sig = getattr(signal, name, None)
            if sig is not None:
                try:
                    signal.signal(sig, handler)
                except (ValueError, OSError):
                    pass

    # ---- thread-safety --------------------------------------------------- #
    def ui(self, fn) -> None:
        """Accoda una funzione da eseguire nel thread della GUI."""
        self.ui_q.put(fn)

    def _poll(self) -> None:
        self.after(100, self._poll)
        if self._quitting:
            return
        for _ in range(50):
            try:
                fn = self.ui_q.get_nowait()
            except queue.Empty:
                break
            try:
                fn()
            except Exception:
                self.core.bus.emit("APP", "Errore UI: " + traceback.format_exc(limit=3), "ERROR")
            if self._quitting:
                return
        self._drain_logs()
        self._refresh_states()

    # ---- console --------------------------------------------------------- #
    def _drain_logs(self) -> None:
        q = self.core.bus.q
        items = []
        while len(items) < 300:
            try:
                items.append(q.get_nowait())
            except queue.Empty:
                break
        if not items:
            return
        c = self.console
        c.configure(state="normal")
        for ts, src, lvl, line in items:
            c.insert("end", f"{ts} ", "ts")
            c.insert("end", f"[{src}] ", "src")
            c.insert("end", line + "\n", lvl)
        end_line = int(c.index("end-1c").split(".")[0])
        if end_line - 1 > self.max_lines:  # buffer circolare
            c.delete("1.0", f"{end_line - self.max_lines}.0")
        c.configure(state="disabled")
        if self.autoscroll.get():
            c.see("end")

    def clear_logs(self) -> None:
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    # ---- stato ----------------------------------------------------------- #
    @staticmethod
    def _global_state(gw: str, lm: str) -> tuple[str, str]:
        if gw == RUNNING and lm == RUNNING:
            return "ALL SYSTEMS GO", NEON
        if gw == STOPPED and lm == STOPPED:
            return "OFFLINE", RED
        return "DEGRADED", ORANGE

    def _refresh_states(self) -> None:
        st = self.core.get_state()
        gw, lm = st["gateway"], st["lm_studio"]
        self.card_gw.set_state(*gw)
        self.card_lm.set_state(*lm)

        text, color = self._global_state(gw[0], lm[0])
        if text != self._last_global:
            prev = self._last_global
            self._last_global = text
            self.global_lbl.configure(text=f"● {text}", text_color=color)
            self._update_tray(text, color)
            if prev == "ALL SYSTEMS GO" and self.tray and not self.winfo_viewable():
                try:
                    self.tray.notify(f"Stato: {text}", APP_NAME)
                except Exception:
                    pass
        bar = f"Gateway: {gw[1]}   |   LM Studio: {lm[1]}"
        if bar != self._last_bar:
            self._last_bar = bar
            self.statusbar.configure(text=bar)

    # ---- worker async ---------------------------------------------------- #
    def _set_busy(self, key: str, busy: bool) -> None:
        if key in ("gw", "all"):
            self.card_gw.set_busy(busy)
        if key in ("lm", "all"):
            self.card_lm.set_busy(busy)
        if key == "health":
            self.health_btn.configure(
                state="disabled" if busy else "normal",
                text="…  CONTROLLO IN CORSO" if busy else "▶  RUN HEALTH CHECK")

    def _async(self, key: str, fn) -> None:
        """Esegue fn in un thread. fn può restituire una funzione da eseguire poi nella GUI."""
        if key in self._busy:
            self.core.bus.emit("APP", "Operazione già in corso…", "WARNING")
            return
        self._busy.add(key)
        self._set_busy(key, True)

        def worker():
            follow = None
            try:
                follow = fn()
            except Exception:
                self.core.bus.emit("APP", "Errore inatteso: " + traceback.format_exc(limit=3), "ERROR")
            self.ui(lambda: self._done(key))
            if follow:
                self.ui(follow)

        threading.Thread(target=worker, daemon=True, name=f"work-{key}").start()

    def _done(self, key: str) -> None:
        self._busy.discard(key)
        self._set_busy(key, False)

    def _report(self, r: ActionResult) -> None:
        if not r.ok:
            lvl = "ERROR"
        elif r.code in ("ALREADY_RUNNING", "NOT_RUNNING"):
            lvl = "WARNING"
        else:
            lvl = "SUCCESS"
        self.core.bus.emit("APP", r.message, lvl)

    def _ask(self, title: str, msg: str) -> bool:
        kw = {"parent": self} if self.winfo_viewable() else {}
        return messagebox.askyesno(title, msg, **kw)

    # ---- azioni Gateway -------------------------------------------------- #
    def act_gw_start(self) -> None:
        self._async("gw", self._work_gw_start)

    def act_gw_stop(self) -> None:
        self._async("gw", self._work_gw_stop)

    def act_gw_restart(self) -> None:
        self._async("gw", self._work_gw_restart)

    def _work_gw_start(self):
        r = self.core.start_gateway()
        self._report(r)
        if r.code == "PORT_BUSY":
            return lambda: self._prompt_force(r, "start")

    def _work_gw_stop(self):
        r = self.core.stop_gateway()
        self._report(r)
        if r.code == "EXTERNAL":
            return lambda: self._prompt_force(r, "stop")

    def _work_gw_restart(self):
        r = self.core.restart_gateway()
        self._report(r)
        if r.code in ("PORT_BUSY", "EXTERNAL"):
            return lambda: self._prompt_force(r, "start")

    def _prompt_force(self, r: ActionResult, mode: str) -> None:
        names = ", ".join(f"{n} (PID {pid})" for pid, n in r.owners) or "processo sconosciuto"
        port = self.core.gw_port
        if mode == "start":
            msg = f"La porta {port} è occupata da:\n{names}\n\nTerminare il processo e avviare il Gateway?"
        else:
            msg = f"Il Gateway sulla porta {port} non è stato avviato da Commander:\n{names}\n\nTerminarlo comunque?"
        if self._ask("Force Kill Port Owner?", msg):
            self._async("gw", lambda: self._work_force(mode))

    def _work_force(self, mode: str):
        killed = self.core.kill_port_owner(self.core.gw_port)
        if not killed:
            self.core.bus.emit("APP", "Nessun processo terminato.", "ERROR")
            return
        if mode == "start":
            self._report(self.core.start_gateway())
        else:
            self.core.bus.emit("APP", "Processo terminato.", "SUCCESS")

    # ---- azioni LM Studio ------------------------------------------------ #
    def _work_lm_start(self):
        r = self.core.start_lm_studio()
        self._report(r)
        if r.code == "NOT_FOUND":
            return self._prompt_lm_exe
        if r.code == "PORT_BUSY":
            return lambda: self._prompt_force_lm(r)

    def _prompt_force_lm(self, r: ActionResult) -> None:
        names = ", ".join(f"{n} (PID {pid})" for pid, n in r.owners) or "processo sconosciuto"
        msg = f"La porta {self.core.lm_port} è occupata da:\n{names}\n\nTerminare il processo e avviare LM Studio?"
        if self._ask("Force Kill Port Owner?", msg):
            self._async("lm", self._work_force_lm)

    def _work_force_lm(self):
        if not self.core.kill_port_owner(self.core.lm_port):
            self.core.bus.emit("APP", "Nessun processo terminato.", "ERROR")
            return
        self._report(self.core.start_lm_studio())

    def _work_lm_stop(self):
        self._report(self.core.stop_lm_studio())

    def _work_lm_restart(self):
        r = self.core.restart_lm_studio()
        self._report(r)
        if r.code == "NOT_FOUND":
            return self._prompt_lm_exe

    def _prompt_lm_exe(self) -> None:
        kw = {"parent": self} if self.winfo_viewable() else {}
        path = filedialog.askopenfilename(
            title="Seleziona LM Studio.exe",
            filetypes=[("Eseguibile", "*.exe"), ("Tutti i file", "*.*")], **kw)
        if path:
            self.core.set_lm_exe(path)
            self._async("lm", self._work_lm_start)

    # ---- altre azioni ---------------------------------------------------- #
    def act_stop_all(self) -> None:
        def work():
            for r in self.core.stop_all():
                self._report(r)
        self._async("all", work)

    def act_health(self) -> None:
        def work():
            report = self.core.health_check()
            return lambda: self._show_health(report)
        self._async("health", work)

    def _show_health(self, rep: HealthReport) -> None:
        color = NEON if rep.all_ok else (RED if rep.passed == 0 else ORANGE)
        lines = [rep.diagnosis, ""]
        for ch in rep.checks:
            lines.append(f"{'✅' if ch.ok else '❌'} {ch.name}")
            lines.append(f"    {ch.detail}")
        self.health_summary.configure(text=rep.summary, text_color=color)
        self.health_result.configure(text="\n".join(lines), text_color=color)
        self._refresh_keys()

    def _refresh_keys(self) -> None:
        """Stato delle chiavi del .env: solo present/missing, mai i valori."""
        st = self.core.env_status()
        if not st:
            self.keys_lbl.configure(text="")
            return
        rows = ["Chiavi .env"] + [f"  {'✔' if ok else '✖'} {k}: {'present' if ok else 'MISSING'}"
                                  for k, ok in st.items()]
        self.keys_lbl.configure(text="\n".join(rows), text_color=DIM if all(st.values()) else ORANGE)

    def open_config(self) -> None:
        try:
            os.startfile(str(self.core.config_path))  # type: ignore[attr-defined]
        except Exception as e:
            self.core.bus.emit("APP", f"Impossibile aprire config.json: {e}", "ERROR")

    # ---- tray ------------------------------------------------------------ #
    def _setup_tray(self) -> None:
        if pystray is None:
            self.core.bus.emit("APP", "pystray non disponibile: niente icona nella tray (la X chiude l'app).", "WARNING")
            return
        try:
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", lambda i, it: self.ui(self.show_window), default=True),
                pystray.MenuItem("Restart Gateway", lambda i, it: self.ui(self.act_gw_restart)),
                pystray.MenuItem("Stop All Services", lambda i, it: self.ui(self.act_stop_all)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit Application", lambda i, it: self.ui(self.request_exit)),
            )
            self.tray = pystray.Icon("trident_commander", make_icon(RED), APP_NAME, menu)
            self.tray.run_detached()
        except Exception as e:
            self.tray = None
            self.core.bus.emit("APP", f"System tray non avviata: {e}", "WARNING")

    def _update_tray(self, text: str, color: str) -> None:
        if not self.tray:
            return
        try:
            self.tray.icon = make_icon(color)
            self.tray.title = f"{APP_NAME} – {text}"
        except Exception:
            pass

    def show_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close(self) -> None:
        """La X nasconde la finestra nella tray (se disponibile)."""
        if self.tray:
            self.withdraw()
            if not self._tray_notified:
                self._tray_notified = True
                try:
                    self.tray.notify("Commander continua a girare nella tray.", APP_NAME)
                except Exception:
                    pass
        else:
            self.request_exit()

    # ---- uscita ---------------------------------------------------------- #
    def request_exit(self) -> None:
        opts = self.core.cfg["options"]
        if opts.get("stop_gateway_on_exit", True) and self.core.gateway_managed_alive():
            if not self._ask(APP_NAME, "Il Gateway avviato da questa app verrà arrestato. Uscire?"):
                return
        self._quit()

    def _quit(self) -> None:
        if self._quitting:
            return
        self._quitting = True
        self.withdraw()
        if self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        self.core.shutdown()  # chiude il gateway figlio (e LM Studio se configurato)
        self.destroy()


# --------------------------------------------------------------------------- #
# Avvio
# --------------------------------------------------------------------------- #
_lock_ref = None  # tiene vivo mutex/socket per tutta la vita del processo


def _acquire_single_instance() -> bool:
    """Windows: named mutex (CreateMutexW via ctypes). Altri OS: bind su localhost."""
    global _lock_ref
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.restype = ctypes.c_void_p
        k32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        handle = k32.CreateMutexW(None, False, "Local\\TRIDENT_COMMANDER_SINGLE_INSTANCE")
        if ctypes.get_last_error() == 183 or not handle:  # ERROR_ALREADY_EXISTS
            return False
        _lock_ref = handle
        return True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", LOCK_PORT))
        s.listen(1)
    except OSError:
        return False
    _lock_ref = s
    return True


def main() -> None:
    if not _acquire_single_instance():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(APP_NAME, "TRIDENT Commander è già in esecuzione (controlla la system tray).")
        return
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    App().mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        (app_dir() / "crash.log").write_text(traceback.format_exc(), encoding="utf-8")
        raise
