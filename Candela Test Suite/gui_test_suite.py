#!/usr/bin/env python3
"""
CANDELA Test Suite — GUI Wizard  (v3)
======================================

Compact wizard-style interface inspired by Raspberry Pi Imager.
Designed for non-technical users, tech-savvy reviewers, and developers alike.

Window: ~700×500, wizard steps with sidebar navigation.
Dynamically discovers locally available models and compatible HuggingFace models.
Full workflow: Welcome → Depth → Model → Rules → Review → Download → Launch → Interact → Results

Usage:
  python3.11 gui_test_suite.py

Requires: Python 3.11+ with tkinter
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SANDBOX = SCRIPT_DIR.parent
HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"
OLLAMA_DIR = Path.home() / ".ollama" / "models"
CANDELA_MODELS = SANDBOX / "models"
RESULTS_DIR = SCRIPT_DIR  # Reports written here

# ── Colours (clean, professional, compact) ─────────────────────────────
WHITE      = "#ffffff"
BG         = "#f5f5f5"
SIDEBAR_BG = "#2b3e50"
SIDEBAR_FG = "#c8d6e5"
SIDEBAR_ACTIVE_BG = "#1a2c3d"
SIDEBAR_ACTIVE_FG = "#ffffff"
TEXT       = "#1a1a1a"
TEXT_LIGHT = "#666666"
TEXT_MUTED = "#999999"
ACCENT     = "#c0392b"          # CANDELA red (Raspberry Pi style)
ACCENT_HOVER = "#a93226"
GREEN      = "#27ae60"
AMBER      = "#e67e22"
RED        = "#e74c3c"
CARD_BORDER = "#dcdcdc"
SELECTED_BG = "#dae8fc"
HOVER_BG   = "#f0f0f0"
PROGRESS_TRACK = "#e0e0e0"
LINK_BLUE  = "#2980b9"


# ══════════════════════════════════════════════════════════════════════
#  System Scan
# ══════════════════════════════════════════════════════════════════════
def scan_system() -> dict:
    ram_gb = 8.0
    try:
        if sys.platform == "darwin":
            out = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"], text=True
            ).strip()
            ram_gb = int(out) / (1024 ** 3)
        elif sys.platform.startswith("linux"):
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_gb = int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass

    gpu = "cpu"
    gpu_label = "CPU only"
    try:
        import torch
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            gpu, gpu_label = "mps", "Apple GPU"
        elif torch.cuda.is_available():
            gpu, gpu_label = "cuda", "NVIDIA GPU"
    except ImportError:
        # torch not available in this Python — that's fine, cpu fallback
        if sys.platform == "darwin" and platform.machine() == "arm64":
            gpu, gpu_label = "mps", "Apple GPU (inferred)"

    return {
        "ram_gb": round(ram_gb, 1),
        "cores": os.cpu_count() or 1,
        "gpu": gpu,
        "gpu_label": gpu_label,
        "disk_gb": round(shutil.disk_usage(str(SANDBOX)).free / (1024**3), 1),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "os": f"{platform.system()} {platform.mac_ver()[0]}" if sys.platform == "darwin" else platform.system(),
    }


# ══════════════════════════════════════════════════════════════════════
#  Model Discovery — runs in background thread
# ══════════════════════════════════════════════════════════════════════
# Well-known small text-generation models suitable for testing on consumer hardware
WELL_KNOWN_SMALL_MODELS = [
    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "name": "TinyLlama 1.1B Chat", "size_gb": 2.2,
     "desc": "Fast, compact chat model. Great for testing."},
    {"id": "distilbert/distilgpt2", "name": "DistilGPT-2", "size_gb": 0.4,
     "desc": "Very small and fast. Limited but usable for basic tests."},
    {"id": "microsoft/phi-2", "name": "Microsoft Phi-2", "size_gb": 5.5,
     "desc": "Strong reasoning for its size. Needs more memory."},
    {"id": "Qwen/Qwen2.5-1.5B-Instruct", "name": "Qwen 2.5 1.5B", "size_gb": 3.0,
     "desc": "Capable instruction-following model. Good balance."},
    {"id": "stabilityai/stablelm-zephyr-3b", "name": "StableLM Zephyr 3B", "size_gb": 5.6,
     "desc": "Larger but more capable. Needs 8+ GB memory."},
    {"id": "bigscience/bloom-560m", "name": "BLOOM 560M", "size_gb": 1.1,
     "desc": "Multilingual. Very small footprint."},
]

# Models to skip (not text-generation, too specialised, or encoder-only)
SKIP_PATTERNS = [
    "sentence-transformers", "embed", "reranker", "clip",
    "whisper", "wav2vec", "hubert", "vit", "dino",
    "bert", "roberta", "distilbert", "albert", "electra",
    "encoder", "segformer", "detr", "yolo",
]


def discover_models(sys_info: dict) -> list[dict]:
    """
    Discover locally available models and rate their suitability.
    Sources: CANDELA models/, HuggingFace cache, well-known downloadable models.
    Runs in a background thread — must not touch tkinter.
    """
    ram = sys_info["ram_gb"]
    gpu = sys_info["gpu"]
    found = []
    seen_ids = set()

    def _should_skip(model_id: str) -> bool:
        low = model_id.lower()
        return any(pat in low for pat in SKIP_PATTERNS)

    # 1) CANDELA's own models directory
    if CANDELA_MODELS.exists():
        for d in CANDELA_MODELS.iterdir():
            if d.is_dir() and (d / "config.json").exists():
                model_id = d.name
                if model_id not in seen_ids and not _should_skip(model_id):
                    # Efficient size calculation — only look at large files
                    disk_bytes = 0
                    for f in d.iterdir():
                        if f.is_file():
                            disk_bytes += f.stat().st_size
                    # Check subdirs (shallow)
                    for sub in d.iterdir():
                        if sub.is_dir():
                            for f in sub.iterdir():
                                if f.is_file():
                                    disk_bytes += f.stat().st_size
                    disk_gb = disk_bytes / (1024**3)
                    mem_gb = disk_gb / 2 if gpu != "cpu" else disk_gb
                    friendly = _friendly_name(model_id)
                    found.append(_rate_model(
                        friendly, model_id, str(d),
                        "Ready to use (already downloaded)",
                        mem_gb, ram, gpu, local=True
                    ))
                    seen_ids.add(model_id)

    # 2) HuggingFace cache (text-generation models only)
    if HF_CACHE.exists():
        for d in HF_CACHE.iterdir():
            if d.name.startswith("models--"):
                parts = d.name.split("--")
                if len(parts) >= 3:
                    model_id = "/".join(parts[1:])
                    short_name = parts[-1]
                    if _should_skip(model_id):
                        continue
                    if short_name in seen_ids or model_id in seen_ids:
                        continue
                    snapshots = d / "snapshots"
                    if snapshots.exists():
                        latest = max(
                            snapshots.iterdir(),
                            key=lambda p: p.stat().st_mtime,
                            default=None,
                        )
                        if latest and (latest / "config.json").exists():
                            try:
                                cfg = json.loads(
                                    (latest / "config.json").read_text()
                                )
                                model_type = cfg.get("model_type", "").lower()
                                if model_type in (
                                    "bert", "roberta", "distilbert",
                                    "albert", "electra",
                                ):
                                    continue
                            except Exception:
                                pass

                            # Efficient size: sum top-level files only
                            disk_bytes = sum(
                                f.stat().st_size
                                for f in latest.iterdir()
                                if f.is_file()
                            )
                            disk_gb = disk_bytes / (1024**3)
                            mem_gb = disk_gb / 2 if gpu != "cpu" else disk_gb
                            friendly = _friendly_name(short_name)
                            found.append(_rate_model(
                                friendly, model_id, str(latest),
                                "Found in your cache",
                                mem_gb, ram, gpu, local=True,
                            ))
                            seen_ids.add(short_name)
                            seen_ids.add(model_id)

    # 3) Ollama models
    manifests = OLLAMA_DIR / "manifests" / "registry.ollama.ai" / "library"
    if manifests.exists():
        for model_dir in manifests.iterdir():
            if model_dir.is_dir():
                name = model_dir.name
                if name not in seen_ids and not _should_skip(name):
                    est = _estimate_size_from_name(name)
                    mem_gb = est / 2 if gpu != "cpu" else est
                    friendly = f"{name.title()} (Ollama)"
                    found.append(_rate_model(
                        friendly, f"ollama:{name}", str(model_dir),
                        "Installed via Ollama",
                        mem_gb, ram, gpu, local=True,
                    ))
                    seen_ids.add(name)

    # 4) Well-known downloadable models (always show these as options)
    for wk in WELL_KNOWN_SMALL_MODELS:
        short = wk["id"].split("/")[-1]
        if short not in seen_ids and wk["id"] not in seen_ids:
            mem_gb = wk["size_gb"] / 2 if gpu != "cpu" else wk["size_gb"]
            found.append(_rate_model(
                wk["name"], wk["id"], wk["id"],
                f"Download from HuggingFace (~{wk['size_gb']} GB)",
                mem_gb, ram, gpu, local=False,
                description=wk["desc"],
            ))
            seen_ids.add(short)
            seen_ids.add(wk["id"])

    # 5) Try HuggingFace Hub API for trending models (fast, non-blocking)
    try:
        from huggingface_hub import list_models
        hub_hits = list_models(
            task="text-generation", sort="downloads",
            direction=-1, limit=15,
        )
        for m in hub_hits:
            short = m.id.split("/")[-1] if "/" in m.id else m.id
            if short in seen_ids or m.id in seen_ids:
                continue
            if _should_skip(m.id):
                continue
            est = _estimate_size_from_name(m.id)
            if est > 10:
                continue  # skip huge models
            mem_gb = est / 2 if gpu != "cpu" else est
            friendly = _friendly_name(short)
            found.append(_rate_model(
                friendly, m.id, m.id,
                f"Download from HuggingFace (~{est:.1f} GB)",
                mem_gb, ram, gpu, local=False,
            ))
            seen_ids.add(short)
            seen_ids.add(m.id)
            if len(found) >= 15:
                break
    except Exception:
        pass  # offline or library not installed — no problem

    # Sort: suitable locals first, then risky locals, then downloadable
    order = {"suitable": 0, "risky": 1, "unsuitable": 2}
    found.sort(key=lambda m: (
        0 if m["local"] else 1,
        order.get(m["status"], 3),
        m["size_gb"],
    ))
    return found


def _rate_model(
    name: str, model_id: str, path: str, source: str,
    mem_gb: float, ram: float, gpu: str, local: bool,
    description: str = "",
) -> dict:
    available = ram - 3.0  # OS + browser overhead
    if mem_gb <= available * 0.5:
        status = "suitable"
        reason = "Fits comfortably in memory"
    elif mem_gb <= available:
        status = "risky"
        reason = "Will use most of your memory"
    else:
        status = "unsuitable"
        reason = "Not enough memory"

    # Memory mode
    if gpu != "cpu":
        dtype_label = "Efficient memory mode"
    elif ram >= 12:
        dtype_label = "Standard memory mode"
    else:
        dtype_label = "Efficient memory mode"

    return {
        "name": name,
        "model_id": model_id,
        "path": path,
        "source": source,
        "size_gb": round(mem_gb, 1),
        "status": status,
        "reason": reason,
        "dtype_label": dtype_label,
        "local": local,
        "description": description,
    }


def _friendly_name(raw: str) -> str:
    """Turn model directory names into human-readable names."""
    name = raw.replace("-", " ").replace("_", " ")
    # Capitalise known tokens
    replacements = {
        "tinyllama": "TinyLlama",
        "1.1b": "1.1B",
        "1.5b": "1.5B",
        "3b": "3B",
        "7b": "7B",
        "chat": "Chat",
        "instruct": "Instruct",
        "v1.0": "v1.0",
        "gpt2": "GPT-2",
        "phi": "Phi",
        "qwen": "Qwen",
        "bloom": "BLOOM",
        "stablelm": "StableLM",
        "zephyr": "Zephyr",
    }
    for token, rep in replacements.items():
        name = re.sub(re.escape(token), rep, name, flags=re.IGNORECASE)
    return name.strip()


def _estimate_size_from_name(model_id: str) -> float:
    mid = model_id.lower()
    if "70b" in mid: return 40
    if "34b" in mid: return 20
    if "13b" in mid: return 8
    if "8b" in mid:  return 5
    if "7b" in mid:  return 4.5
    if "3b" in mid:  return 2
    if "1.5b" in mid: return 3
    if "1b" in mid or "1.1b" in mid: return 2.2
    if "560m" in mid: return 1.1
    if "distilgpt2" in mid or "gpt2" in mid: return 0.5
    return 4  # conservative default


# ── Profiles & Rulesets ────────────────────────────────────────────────
PROFILES = [
    (
        "quick",
        "Quick check",
        "Tests the core rules and detection modes.\n"
        "No AI model needed — fast and lightweight.",
        "~2 minutes",
    ),
    (
        "full",
        "Full test",
        "Everything: rules, modes, AI model interaction,\n"
        "and stress tests. The recommended choice.",
        "15–30 minutes",
    ),
    (
        "anchor",
        "Full + blockchain record",
        "Full test plus a permanent, tamper-proof record\n"
        "of the results on the blockchain.",
        "20–35 minutes",
    ),
]

RULESETS = [
    ("baseline",             "Standard enterprise rules",  "12 safety rules covering the most common AI risks."),
    ("security_hardening",   "Security hardening",         "Extra checks focused on preventing security leaks."),
    ("privacy_strict",       "Strict privacy",             "Stricter rules around personal data protection."),
    ("health_privacy_micro", "Health data privacy",        "Specialised rules for health and medical data."),
]

PHASE_NAMES = {
    2: "Checking validation rules",
    3: "Testing operating modes",
    4: "Verifying rule sets",
    5: "Testing with AI model",
    6: "Verifying audit trail",
    7: "Running stress tests",
    8: "Generating report",
}

# Friendly explanations shown during each phase
PHASE_DETAIL = {
    2: "Making sure CANDELA correctly validates inputs and catches "
       "malformed or dangerous content before it reaches the model.",
    3: "Testing each operating mode — from lightweight regex scanning "
       "to full AI-powered semantic analysis — to confirm they all work.",
    4: "Checking every safety rule in the selected ruleset. CANDELA should "
       "catch violations like leaked passwords, credit cards, and private data.",
    5: "Loading the AI model into memory and sending real prompts with CANDELA "
       "active. Each response is checked in real time for safety rule violations. "
       "This may take a moment the first time.",
    6: "Verifying that every check CANDELA performed was properly logged "
       "in the audit trail — creating a tamper-proof compliance record.",
    7: "Pushing the system hard with rapid-fire requests and edge cases "
       "to make sure CANDELA stays reliable under pressure.",
    8: "Compiling all results into a detailed report you can share with "
       "reviewers, auditors, or compliance officers.",
}


# ══════════════════════════════════════════════════════════════════════
#  GUI Application
# ══════════════════════════════════════════════════════════════════════
class CandelaWizard(tk.Tk):

    STEPS = [
        {"name": "Welcome",     "icon": "1",  "nav": True},
        {"name": "Test Depth",  "icon": "2",  "nav": True},
        {"name": "AI Model",    "icon": "3",  "nav": True},
        {"name": "Rules",       "icon": "4",  "nav": True},
        {"name": "Review",      "icon": "5",  "nav": True},
        {"name": "Preparing",   "icon": "▸",  "nav": False},
        {"name": "Running",     "icon": "▶",  "nav": False},
        {"name": "Interact",    "icon": "💬", "nav": False},
        {"name": "Results",     "icon": "✓",  "nav": False},
    ]

    def __init__(self):
        super().__init__()
        self.title("CANDELA Test Suite")
        self.configure(bg=BG)
        self.geometry("700x500+300+150")
        self.minsize(680, 450)
        self.resizable(True, True)

        # ── State ──
        self.sys_info = scan_system()
        self.models: list[dict] = []
        self.models_loading = False
        self.selected_model: dict | None = None
        self.selected_profile = "full"
        self.selected_ruleset = "baseline"
        self.current_step = 0
        self.run_cancelled = False
        self.run_results: dict = {}
        self.model_process: subprocess.Popen | None = None

        # ── Fonts ──
        self.f_title   = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.f_heading = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.f_body    = tkfont.Font(family="Helvetica", size=12)
        self.f_body_it = tkfont.Font(family="Helvetica", size=12, slant="italic")
        self.f_small   = tkfont.Font(family="Helvetica", size=10)
        self.f_badge   = tkfont.Font(family="Helvetica", size=9, weight="bold")
        self.f_sidebar = tkfont.Font(family="Helvetica", size=11)
        self.f_sidebar_active = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.f_big     = tkfont.Font(family="Helvetica", size=40, weight="bold")
        self.f_mono    = tkfont.Font(family="Courier", size=11)

        # ── ttk button styles (trackpad-friendly, consistent) ──
        style = ttk.Style()
        # Use 'clam' theme — native trackpad response on macOS
        style.theme_use("clam")
        style.configure("Nav.TButton",
            font=("Helvetica", 12),
            padding=(14, 6),
        )
        # NavAccent is visually identical to Nav — same size, same font
        style.configure("NavAccent.TButton",
            font=("Helvetica", 12),
            padding=(14, 6),
        )

        # ── Layout: sidebar + content ──
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=170)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=WHITE)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._build_all_steps()
        self._show_step(0)

        # Start model discovery immediately (background thread)
        self._begin_model_discovery()

        # Clean exit on window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Cleanup ────────────────────────────────────────────────────────
    def _on_close(self):
        self.run_cancelled = True
        if self.model_process:
            try:
                self.model_process.terminate()
            except Exception:
                pass
        self.destroy()

    # ══════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        # Logo area
        title_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        title_frame.pack(fill="x", padx=12, pady=(14, 16))
        tk.Label(
            title_frame, text="CANDELA",
            font=self.f_heading, bg=SIDEBAR_BG, fg=WHITE,
        ).pack(anchor="w")
        tk.Label(
            title_frame, text="Test Suite",
            font=self.f_small, bg=SIDEBAR_BG, fg=SIDEBAR_FG,
        ).pack(anchor="w")

        # Divider
        tk.Frame(self.sidebar, bg="#3d5166", height=1).pack(fill="x", padx=12)

        # Step labels
        self.sidebar_labels = []
        for i, step in enumerate(self.STEPS):
            frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
            frame.pack(fill="x")

            cursor = "hand2" if step["nav"] else ""
            row = tk.Frame(frame, bg=SIDEBAR_BG, padx=12, pady=5, cursor=cursor)
            row.pack(fill="x")

            num = tk.Label(
                row, text=step["icon"],
                font=self.f_small, bg=SIDEBAR_BG, fg=SIDEBAR_FG, width=2,
            )
            num.pack(side="left")
            lbl = tk.Label(
                row, text=step["name"],
                font=self.f_sidebar, bg=SIDEBAR_BG, fg=SIDEBAR_FG, anchor="w",
            )
            lbl.pack(side="left", padx=(4, 0))

            self.sidebar_labels.append(
                {"frame": frame, "row": row, "num": num, "lbl": lbl}
            )

            if step["nav"]:
                for widget in (frame, row, num, lbl):
                    widget.bind(
                        "<Button-1>",
                        lambda e, idx=i: self._jump_to(idx),
                    )

        # Spacer + system info at bottom
        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)

        # Help
        help_lbl = tk.Label(
            self.sidebar, text="?  Help",
            font=self.f_small, bg=SIDEBAR_BG, fg=SIDEBAR_FG, cursor="hand2",
        )
        help_lbl.pack(padx=12, pady=(0, 4), anchor="w")
        help_lbl.bind("<Button-1>", self._show_help)

        # Compact system line
        sys_text = f"{self.sys_info['ram_gb']}GB · {self.sys_info['gpu_label']}"
        tk.Label(
            self.sidebar, text=sys_text,
            font=tkfont.Font(family="Helvetica", size=9),
            bg=SIDEBAR_BG, fg="#7f9bba",
        ).pack(padx=12, pady=(0, 10), anchor="w")

    def _update_sidebar(self):
        for i, s in enumerate(self.sidebar_labels):
            if i == self.current_step:
                s["row"].configure(bg=SIDEBAR_ACTIVE_BG)
                s["num"].configure(bg=SIDEBAR_ACTIVE_BG, fg=SIDEBAR_ACTIVE_FG)
                s["lbl"].configure(
                    bg=SIDEBAR_ACTIVE_BG, fg=SIDEBAR_ACTIVE_FG,
                    font=self.f_sidebar_active,
                )
            elif i < self.current_step:
                s["row"].configure(bg=SIDEBAR_BG)
                s["num"].configure(bg=SIDEBAR_BG, fg=GREEN)
                s["lbl"].configure(
                    bg=SIDEBAR_BG, fg=SIDEBAR_FG, font=self.f_sidebar,
                )
            else:
                s["row"].configure(bg=SIDEBAR_BG)
                s["num"].configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
                s["lbl"].configure(
                    bg=SIDEBAR_BG, fg=SIDEBAR_FG, font=self.f_sidebar,
                )

    # ══════════════════════════════════════════════════════════════════
    #  STEP MANAGEMENT
    # ══════════════════════════════════════════════════════════════════
    def _build_all_steps(self):
        self.step_frames = []
        builders = [
            self._build_welcome,      # 0
            self._build_profile,      # 1
            self._build_model,        # 2
            self._build_ruleset,      # 3
            self._build_review,       # 4
            self._build_preparing,    # 5 — download / configure
            self._build_running,      # 6 — test execution
            self._build_interact,     # 7 — interactive model session
            self._build_results,      # 8 — final results
        ]
        for builder in builders:
            frame = tk.Frame(self.content, bg=WHITE)
            builder(frame)
            self.step_frames.append(frame)

    def _show_step(self, idx: int):
        self.current_step = idx
        for i, f in enumerate(self.step_frames):
            if i == idx:
                f.pack(fill="both", expand=True)
            else:
                f.pack_forget()
        self._update_sidebar()

        # Hook per-step refresh
        if idx == 2:
            self._refresh_model_list()
        elif idx == 4:
            self._refresh_review()
        elif idx == 5:
            self._start_preparation()
        elif idx == 6:
            self._start_run()
        elif idx == 7:
            # Give keyboard focus to chat input so typing works immediately
            self.after(100, lambda: self.chat_input.focus_set())
        elif idx == 8:
            pass  # results shown by caller

    def _next(self):
        nxt = self.current_step + 1
        # Skip model step if profile is "quick"
        if nxt == 2 and self.selected_profile == "quick":
            nxt = 3
        if nxt < len(self.step_frames):
            self._show_step(nxt)

    def _back(self):
        prev = self.current_step - 1
        if prev == 2 and self.selected_profile == "quick":
            prev = 1
        if prev >= 0:
            self._show_step(prev)

    def _jump_to(self, idx: int):
        # Can jump to any completed or current navigable step
        if idx <= self.current_step or idx <= 4:
            self._show_step(idx)

    # ── Reusable nav bar ──────────────────────────────────────────────
    def _nav_bar(self, parent, back=True, next_text="Next", next_cmd=None):
        bar = tk.Frame(parent, bg=WHITE)
        bar.pack(fill="x", side="bottom", padx=24, pady=(0, 14))

        if back:
            back_btn = ttk.Button(
                bar, text="Back", style="Nav.TButton",
                command=self._back, cursor="hand2",
            )
            back_btn.pack(side="left")

        next_btn = ttk.Button(
            bar, text=next_text, style="NavAccent.TButton",
            command=next_cmd or self._next, cursor="hand2",
        )
        next_btn.pack(side="right")
        return bar

    # ══════════════════════════════════════════════════════════════════
    #  STEP 0: Welcome
    # ══════════════════════════════════════════════════════════════════
    def _build_welcome(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Welcome to CANDELA",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 10))

        welcome_text = (
            "CANDELA is an AI safety and compliance system. It sits alongside "
            "an AI model and checks everything the model says against a set of "
            "rules — catching things like leaked passwords, credit card numbers, "
            "medical records, or anything else that shouldn't appear in AI responses."
            "\n\n"
            "Every check is logged, and those logs can be permanently recorded "
            "on a blockchain, creating a tamper-proof audit trail. This means "
            "organisations can prove their AI was compliant — not just claim it."
            "\n\n"
            "This test suite runs CANDELA through its paces and produces "
            "a report you can share with reviewers, auditors, or anyone who "
            "needs evidence that the system works as promised."
        )
        tk.Label(
            body, text=welcome_text,
            font=tkfont.Font(family="Helvetica", size=16), bg=WHITE, fg=TEXT,
            wraplength=450, justify="left",
        ).pack(anchor="w", pady=(0, 14))

        # What happens next
        tk.Label(
            body, text="You'll choose how thorough a test to run, "
            "pick an AI model, and the system handles the rest.",
            font=tkfont.Font(family="Helvetica", size=16, slant="italic"),
            bg=WHITE, fg=TEXT_LIGHT,
            wraplength=450, justify="left",
        ).pack(anchor="w")

        self._nav_bar(parent, back=False, next_text="Get started")

    # ══════════════════════════════════════════════════════════════════
    #  STEP 1: Test Depth (Profile)
    # ══════════════════════════════════════════════════════════════════
    def _build_profile(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="How thorough?",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 2))
        tk.Label(
            body, text="Choose how much to test.",
            font=self.f_body, bg=WHITE, fg=TEXT_LIGHT,
        ).pack(anchor="w", pady=(0, 12))

        self.profile_var = tk.StringVar(value=self.selected_profile)
        self.profile_rows = []

        for key, name, desc, time_est in PROFILES:
            row = tk.Frame(
                body, bg=WHITE, cursor="hand2",
                relief="solid", bd=1,
                highlightbackground=CARD_BORDER, highlightthickness=1,
            )
            row.pack(fill="x", pady=3)

            inner = tk.Frame(row, bg=WHITE, padx=12, pady=8)
            inner.pack(fill="x")

            top_row = tk.Frame(inner, bg=WHITE)
            top_row.pack(fill="x")

            radio = tk.Radiobutton(
                top_row, text=name, variable=self.profile_var, value=key,
                font=self.f_heading, bg=WHITE, fg=TEXT, selectcolor=WHITE,
                activebackground=WHITE, command=self._on_profile_change,
            )
            radio.pack(side="left")
            tk.Label(
                top_row, text=time_est,
                font=self.f_badge, bg=WHITE, fg=TEXT_MUTED,
            ).pack(side="right", padx=4)

            tk.Label(
                inner, text=desc,
                font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
                wraplength=380, justify="left",
            ).pack(anchor="w", padx=24)

            self.profile_rows.append((key, row))
            for w in (row, inner, top_row):
                w.bind("<Button-1>", lambda e, k=key: self._select_profile(k))

        self._on_profile_change()
        self._nav_bar(parent)

    def _select_profile(self, key):
        self.profile_var.set(key)
        self._on_profile_change()

    def _on_profile_change(self):
        self.selected_profile = self.profile_var.get()
        for key, row in self.profile_rows:
            if key == self.selected_profile:
                row.configure(highlightbackground=ACCENT, highlightthickness=2)
            else:
                row.configure(highlightbackground=CARD_BORDER, highlightthickness=1)

    # ══════════════════════════════════════════════════════════════════
    #  STEP 2: AI Model
    # ══════════════════════════════════════════════════════════════════
    def _build_model(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Choose an AI model",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 2))
        tk.Label(
            body,
            text="CANDELA needs a model to test against. Only models your "
                 f"computer can run ({self.sys_info['ram_gb']} GB memory, "
                 f"{self.sys_info['gpu_label']}) are shown.",
            font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        # Scrollable model list container
        list_frame = tk.Frame(
            body, bg=WHITE, relief="solid", bd=1,
            highlightbackground=CARD_BORDER, highlightthickness=1,
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 6))

        canvas = tk.Canvas(list_frame, bg=WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=canvas.yview,
        )
        self.model_list_inner = tk.Frame(canvas, bg=WHITE)

        self.model_list_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window(
            (0, 0), window=self.model_list_inner, anchor="nw", tags="inner",
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig("inner", width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120 or 1), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._nav_bar(parent)

    def _begin_model_discovery(self):
        """Start model scan in background — called once at startup."""
        if self.models_loading:
            return
        self.models_loading = True

        def _scan():
            result = discover_models(self.sys_info)
            self.models = result
            self.models_loading = False
            # Auto-select best model — prefer local + suitable + smallest
            runnable = [m for m in self.models if m["status"] == "suitable"]
            if runnable and not self.selected_model:
                # First choice: local models, sorted by size (smallest first)
                local_ok = [m for m in runnable if m["local"]]
                if local_ok:
                    local_ok.sort(key=lambda m: m["size_gb"])
                    self.selected_model = local_ok[0]
                else:
                    # Fall back to smallest downloadable
                    runnable.sort(key=lambda m: m["size_gb"])
                    self.selected_model = runnable[0]
            # Refresh UI if model step is visible
            if self.current_step == 2:
                self.after(0, self._populate_model_rows)

        threading.Thread(target=_scan, daemon=True).start()

    def _refresh_model_list(self):
        for w in self.model_list_inner.winfo_children():
            w.destroy()

        if self.models_loading or not self.models:
            # Show spinner
            spin_frame = tk.Frame(self.model_list_inner, bg=WHITE)
            spin_frame.pack(padx=12, pady=30)
            tk.Label(
                spin_frame, text="Scanning for compatible models…",
                font=self.f_body, bg=WHITE, fg=TEXT_LIGHT,
            ).pack()
            tk.Label(
                spin_frame,
                text="Checking your computer and online sources",
                font=self.f_small, bg=WHITE, fg=TEXT_MUTED,
            ).pack(pady=(4, 0))
            # Poll until done
            if self.models_loading:
                self.after(300, self._check_model_scan)
            return

        self._populate_model_rows()

    def _check_model_scan(self):
        if self.models_loading:
            self.after(300, self._check_model_scan)
        else:
            if self.current_step == 2:
                self._refresh_model_list()

    def _populate_model_rows(self):
        for w in self.model_list_inner.winfo_children():
            w.destroy()

        # Only show models this hardware can comfortably run
        runnable = [m for m in self.models if m["status"] == "suitable"]

        if not runnable:
            tk.Label(
                self.model_list_inner,
                text="No models found that fit your hardware.\n"
                     f"Your computer has {self.sys_info['ram_gb']} GB of memory.\n\n"
                     "Try closing other applications to free up memory,\n"
                     "or the test will download a small model automatically.",
                font=self.f_small, bg=WHITE, fg=TEXT_LIGHT, justify="center",
            ).pack(padx=12, pady=20)
            return

        # Section headers
        locals_shown = False
        downloads_shown = False

        for i, model in enumerate(runnable):
            # Section divider
            if model["local"] and not locals_shown:
                tk.Label(
                    self.model_list_inner,
                    text="  On your computer",
                    font=self.f_badge, bg=WHITE, fg=TEXT_MUTED, anchor="w",
                ).pack(fill="x", padx=6, pady=(6, 2))
                locals_shown = True
            elif not model["local"] and not downloads_shown:
                if locals_shown:
                    tk.Frame(
                        self.model_list_inner, bg=CARD_BORDER, height=1,
                    ).pack(fill="x", padx=8, pady=4)
                tk.Label(
                    self.model_list_inner,
                    text="  Available to download",
                    font=self.f_badge, bg=WHITE, fg=TEXT_MUTED, anchor="w",
                ).pack(fill="x", padx=6, pady=(4, 2))
                downloads_shown = True

            is_sel = (model is self.selected_model)
            bg = SELECTED_BG if is_sel else WHITE

            row = tk.Frame(
                self.model_list_inner, bg=bg, cursor="hand2",
            )
            row.pack(fill="x", padx=4, pady=1)

            inner = tk.Frame(row, bg=bg, padx=10, pady=6)
            inner.pack(fill="x")

            # Left: name + info
            left = tk.Frame(inner, bg=bg)
            left.pack(side="left", fill="x", expand=True)

            name_row = tk.Frame(left, bg=bg)
            name_row.pack(anchor="w")
            tk.Label(
                name_row, text=model["name"],
                font=self.f_body, bg=bg, fg=TEXT,
            ).pack(side="left")
            if model["local"]:
                tk.Label(
                    name_row, text=" ✓",
                    font=self.f_badge, bg=bg, fg=GREEN,
                ).pack(side="left", padx=(4, 0))

            # Description or source line
            desc_text = model.get("description") or model["source"]
            detail = f"{desc_text}  ·  ~{model['size_gb']} GB"
            tk.Label(
                left, text=detail,
                font=self.f_small, bg=bg, fg=TEXT_LIGHT,
                wraplength=300, justify="left",
            ).pack(anchor="w")

            # Right: badge — show "Recommended" for first local suitable model
            is_recommended = (
                model["local"]
                and model == runnable[0]  # first in sorted list
            )
            if is_recommended:
                tk.Label(
                    inner, text=" Recommended ",
                    font=self.f_badge, bg=GREEN, fg=WHITE,
                ).pack(side="right", padx=4)
            elif model["local"]:
                tk.Label(
                    inner, text=" Ready ",
                    font=self.f_badge, bg=GREEN, fg=WHITE,
                ).pack(side="right", padx=4)
            else:
                tk.Label(
                    inner, text=" Download ",
                    font=self.f_badge, bg=LINK_BLUE, fg=WHITE,
                ).pack(side="right", padx=4)

            # Click handler
            for w in (row, inner, left, name_row):
                w.bind(
                    "<Button-1>",
                    lambda e, m=model: self._select_model(m),
                )

    def _select_model(self, model):
        self.selected_model = model
        self._populate_model_rows()

    # ══════════════════════════════════════════════════════════════════
    #  STEP 3: Rules
    # ══════════════════════════════════════════════════════════════════
    def _build_ruleset(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Which rules to check?",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 2))
        tk.Label(
            body,
            text="CANDELA enforces rules about what AI models can and "
                 "cannot say. Choose which set of rules to test.",
            font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        ).pack(anchor="w", pady=(0, 12))

        self.ruleset_var = tk.StringVar(value=self.selected_ruleset)
        self.ruleset_rows = []

        for key, name, desc in RULESETS:
            row = tk.Frame(
                body, bg=WHITE, cursor="hand2",
                relief="solid", bd=1,
                highlightbackground=CARD_BORDER, highlightthickness=1,
            )
            row.pack(fill="x", pady=3)

            inner = tk.Frame(row, bg=WHITE, padx=12, pady=8)
            inner.pack(fill="x")

            radio = tk.Radiobutton(
                inner, text=name, variable=self.ruleset_var, value=key,
                font=self.f_heading, bg=WHITE, fg=TEXT, selectcolor=WHITE,
                activebackground=WHITE, command=self._on_ruleset_change,
            )
            radio.pack(anchor="w")

            tk.Label(
                inner, text=desc,
                font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
                wraplength=380, justify="left",
            ).pack(anchor="w", padx=24)

            self.ruleset_rows.append((key, row))
            for w in (row, inner):
                w.bind(
                    "<Button-1>",
                    lambda e, k=key: self._select_ruleset(k),
                )

        self._on_ruleset_change()
        self._nav_bar(parent)

    def _select_ruleset(self, key):
        self.ruleset_var.set(key)
        self._on_ruleset_change()

    def _on_ruleset_change(self):
        self.selected_ruleset = self.ruleset_var.get()
        for key, row in self.ruleset_rows:
            if key == self.selected_ruleset:
                row.configure(highlightbackground=ACCENT, highlightthickness=2)
            else:
                row.configure(highlightbackground=CARD_BORDER, highlightthickness=1)

    # ══════════════════════════════════════════════════════════════════
    #  STEP 4: Review
    # ══════════════════════════════════════════════════════════════════
    def _build_review(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Ready to run",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 2))
        tk.Label(
            body, text="Check your choices below, then press Run.",
            font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
        ).pack(anchor="w", pady=(0, 12))

        self.review_frame = tk.Frame(
            body, bg=BG, relief="solid", bd=1,
            highlightbackground=CARD_BORDER, highlightthickness=1,
        )
        self.review_frame.pack(fill="x", pady=(0, 10))

        self.review_warning = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=AMBER,
            wraplength=430, justify="left",
        )
        self.review_warning.pack(anchor="w")

        # What happens next
        self.review_next_steps = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        )
        self.review_next_steps.pack(anchor="w", pady=(8, 0))

        self._nav_bar(parent, next_text="Run tests", next_cmd=self._begin_tests)

    def _refresh_review(self):
        for w in self.review_frame.winfo_children():
            w.destroy()

        profile = next(
            (p for p in PROFILES if p[0] == self.selected_profile),
            PROFILES[1],
        )
        ruleset = next(
            (r for r in RULESETS if r[0] == self.selected_ruleset),
            RULESETS[0],
        )
        model_name = (
            self.selected_model["name"] if self.selected_model else "None"
        )
        model_local = (
            self.selected_model["local"] if self.selected_model else True
        )

        items = [
            ("Test depth", profile[1]),
            ("Time estimate", profile[3]),
            ("Rules", ruleset[1]),
        ]
        if self.selected_profile != "quick":
            items.append(("AI model", model_name))
            if not model_local:
                items.append(("Download", f"~{self.selected_model['size_gb']} GB"))

        for label, value in items:
            row = tk.Frame(self.review_frame, bg=BG)
            row.pack(fill="x", padx=12, pady=3)
            tk.Label(
                row, text=f"{label}:",
                font=self.f_small, bg=BG, fg=TEXT_MUTED,
                width=14, anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=value,
                font=self.f_body, bg=BG, fg=TEXT, anchor="w",
            ).pack(side="left")
        tk.Frame(self.review_frame, bg=BG, height=6).pack()

        # Warning (only shown if somehow no model is selected)
        if (not self.selected_model
                and self.selected_profile != "quick"):
            self.review_warning.config(
                text="No model selected. Go back to select one.",
                fg=AMBER,
            )
        else:
            self.review_warning.config(text="")

        # Next steps
        if self.selected_profile == "quick":
            self.review_next_steps.config(
                text="The quick check will run the core rule tests and produce "
                     "a report. No AI model is needed.",
            )
        else:
            steps = []
            if not model_local:
                steps.append("download the AI model")
            steps.append("configure and launch the model")
            steps.append("run CANDELA's checks against it")
            steps.append("produce a detailed report")
            self.review_next_steps.config(
                text="When you press Run, the system will "
                     + ", ".join(steps) + "."
            )

    def _begin_tests(self):
        """Transition from Review to the appropriate next step."""
        if self.selected_profile == "quick":
            ok = messagebox.askyesno(
                "Ready to run",
                "This will run CANDELA's core rule checks.\n\n"
                "No AI model is needed for the quick check.\n\n"
                "Start the tests now?",
            )
            if not ok:
                return
            self._show_step(6)
        else:
            model_name = (
                self.selected_model["name"] if self.selected_model else "the selected model"
            )
            ok = messagebox.askyesno(
                "Ready to launch",
                f"This will launch {model_name} with CANDELA's safety "
                f"layer active, then run the full test suite against it.\n\n"
                f"CANDELA will check every response the model produces "
                f"and log the results.\n\n"
                f"Start now?",
            )
            if not ok:
                return
            self._show_step(5)

    # ══════════════════════════════════════════════════════════════════
    #  STEP 5: Preparing (Download & Configure)
    # ══════════════════════════════════════════════════════════════════
    def _build_preparing(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Preparing",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.prep_status = tk.Label(
            body, text="Getting ready…",
            font=self.f_body, bg=WHITE, fg=TEXT_LIGHT,
        )
        self.prep_status.pack(anchor="w", pady=(0, 12))

        # Progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Prep.Horizontal.TProgressbar",
            troughcolor=PROGRESS_TRACK, background=ACCENT, thickness=18,
        )
        self.prep_progress = tk.DoubleVar(value=0)
        self.prep_bar = ttk.Progressbar(
            body, variable=self.prep_progress, maximum=100,
            style="Prep.Horizontal.TProgressbar",
        )
        self.prep_bar.pack(fill="x", pady=(0, 4))

        self.prep_pct = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=TEXT_MUTED,
        )
        self.prep_pct.pack(anchor="e", pady=(0, 12))

        # Detail steps
        self.prep_detail = tk.Label(
            body, text="",
            font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        )
        self.prep_detail.pack(anchor="w")

        # Cancel
        tk.Frame(parent, bg=WHITE).pack(fill="both", expand=True)
        cancel_bar = tk.Frame(parent, bg=WHITE)
        cancel_bar.pack(fill="x", side="bottom", padx=24, pady=(0, 14))
        self.prep_cancel_btn = ttk.Button(
            cancel_bar, text="Cancel", style="Nav.TButton",
            cursor="hand2", command=self._cancel_prep,
        )
        self.prep_cancel_btn.pack(side="right")

    def _start_preparation(self):
        self.run_cancelled = False
        self.prep_progress.set(0)
        self.prep_pct.config(text="")
        self.prep_status.config(text="Getting ready…")
        self.prep_detail.config(text="")

        threading.Thread(
            target=self._do_preparation, daemon=True,
        ).start()

    def _do_preparation(self):
        """
        Smart preparation: silently checks what's already installed,
        only downloads/installs what's missing, with friendly progress.
        """
        model = self.selected_model
        if not model:
            self.after(0, lambda: self._show_step(6))
            return

        # ── Phase A: Check what we already have ──────────────────────
        self.after(0, lambda: self._prep_ui(
            2, "Checking what's already set up…",
            "Looking at what's on your computer.",
        ))

        # Check which Python packages are present
        def _has_pkg(name):
            r = subprocess.run(
                [sys.executable, "-c", f"import {name}"],
                capture_output=True, timeout=10,
            )
            return r.returncode == 0

        has_pytest = _has_pkg("pytest")
        has_torch = _has_pkg("torch")
        has_transformers = _has_pkg("transformers")
        has_hf_hub = _has_pkg("huggingface_hub")
        has_dotenv = _has_pkg("dotenv")
        has_web3 = _has_pkg("web3")
        has_st = _has_pkg("sentence_transformers")
        model_is_local = model["local"]

        # Build a list of things we need to do
        tasks = []
        if not has_pytest:
            tasks.append(("pytest", "pip", "pytest"))
        if not has_torch:
            tasks.append(("torch", "pip", "torch"))
        if not has_transformers:
            tasks.append(("transformers", "pip", "transformers"))
        if not has_st:
            tasks.append(("sentence_transformers", "pip", "sentence-transformers"))
        if not has_dotenv:
            tasks.append(("dotenv", "pip", "python-dotenv"))
        if not has_web3:
            tasks.append(("web3", "pip", "web3"))
        if not has_hf_hub and not model_is_local:
            tasks.append(("huggingface_hub", "pip", "huggingface-hub"))
        if not model_is_local:
            tasks.append(("model", "download", model["name"]))

        if self.run_cancelled:
            return

        # ── Phase B: Nothing to do? Skip silently ─────────────────────
        if not tasks:
            pass  # everything present — go straight to configure
        else:
            # ── Phase C: Tell the user what's happening ──────────────
            pkg_tasks = [t for t in tasks if t[1] == "pip"]
            dl_task = [t for t in tasks if t[1] == "download"]

            parts = []
            if dl_task:
                parts.append(f"download {model['name']}")
            if pkg_tasks:
                parts.append("install a few supporting tools")

            summary = " and ".join(parts)
            self.after(0, lambda: self._prep_ui(
                5,
                f"Setting things up…",
                f"We need to {summary}.\n"
                "This only needs to happen once — next time it will be instant.",
            ))
            time.sleep(0.5)

            # Work out progress steps
            total_steps = len(tasks) + 1  # +1 for configure
            done_steps = 0

            # ── Phase D: Install missing Python packages ─────────────
            for pkg_name, task_type, pip_name in tasks:
                if self.run_cancelled:
                    return
                if task_type != "pip":
                    continue

                done_steps += 1
                pct = int((done_steps / total_steps) * 80)

                self.after(0, lambda p=pct, n=pip_name: self._prep_ui(
                    p, f"Installing {n}…",
                    "This only needs to happen once.",
                ))

                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", pip_name],
                    capture_output=True, text=True, timeout=600,
                )
                if result.returncode != 0:
                    # Try --user fallback
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--quiet",
                         "--user", pip_name],
                        capture_output=True, text=True, timeout=600,
                    )
                if result.returncode != 0:
                    self.after(0, lambda n=pip_name, e=result.stderr: self._prep_ui(
                        0,
                        f"Could not install {n}",
                        f"Something went wrong. You may need to install it "
                        f"manually by typing this in Terminal:\n"
                        f"  pip install {n}\n\n"
                        f"Then try running the test suite again.",
                    ))
                    return

            if self.run_cancelled:
                return

            # ── Phase E: Download model if needed ────────────────────
            if dl_task:
                done_steps += 1
                self.after(0, lambda: self._prep_ui(
                    int((done_steps / total_steps) * 80),
                    f"Downloading {model['name']}…",
                    f"This may take a few minutes (~{model['size_gb']} GB).\n"
                    "The model will be saved on your computer for future use.",
                ))

                try:
                    from huggingface_hub import snapshot_download
                    target_dir = CANDELA_MODELS / model["model_id"].split("/")[-1]

                    download_done = threading.Event()
                    download_error = [None]

                    def _download():
                        try:
                            snapshot_download(
                                model["model_id"],
                                local_dir=str(target_dir),
                                local_dir_use_symlinks=False,
                            )
                        except Exception as ex:
                            download_error[0] = str(ex)
                        download_done.set()

                    dl_thread = threading.Thread(target=_download, daemon=True)
                    dl_thread.start()

                    base_pct = int((done_steps / total_steps) * 80)
                    dl_pct = base_pct
                    while not download_done.is_set():
                        if self.run_cancelled:
                            return
                        time.sleep(1)
                        dl_pct = min(dl_pct + 1, base_pct + 15)
                        self.after(0, lambda p=dl_pct: self._prep_ui(
                            p, f"Downloading {model['name']}…", None,
                        ))

                    if download_error[0]:
                        self.after(0, lambda: self._prep_ui(
                            0,
                            "Download failed",
                            f"Could not download the model.\n\n"
                            "Check your internet connection and try again.\n"
                            "If the problem persists, try selecting a different "
                            "model on the previous screen.",
                        ))
                        return

                    model["path"] = str(target_dir)
                    model["local"] = True
                    model["source"] = "Ready to use (just downloaded)"

                except ImportError:
                    self.after(0, lambda: self._prep_ui(
                        0,
                        "Setup incomplete",
                        "A download tool could not be installed.\n"
                        "Please check your internet connection and try again.",
                    ))
                    return

        if self.run_cancelled:
            return

        # ── Phase F: Configure model for CANDELA ─────────────────────
        self.after(0, lambda: self._prep_ui(
            85, "Configuring for the test…",
            "Connecting the model to CANDELA. Your existing files won't be changed.",
        ))

        model_name = (
            model["model_id"].split("/")[-1]
            if "/" in model["model_id"]
            else model["model_id"]
        )
        candela_model_path = CANDELA_MODELS / model_name
        if not candela_model_path.exists() and model["local"]:
            src = Path(model["path"])
            if src.exists() and src != candela_model_path:
                try:
                    candela_model_path.symlink_to(src)
                except Exception:
                    pass

        time.sleep(0.3)

        # ── Done ─────────────────────────────────────────────────────
        self.after(0, lambda: self._prep_ui(
            100, "Ready!",
            f"Everything is set up. Starting tests…",
        ))
        time.sleep(0.8)

        if not self.run_cancelled:
            self.after(0, lambda: self._show_step(6))

    def _prep_ui(self, pct, status, detail):
        self.prep_progress.set(pct)
        self.prep_pct.config(text=f"{pct}%" if pct > 0 else "")
        if status:
            self.prep_status.config(text=status)
        if detail is not None:
            self.prep_detail.config(text=detail)

    def _cancel_prep(self):
        self.run_cancelled = True
        self.after(500, lambda: self._show_step(4))

    # ══════════════════════════════════════════════════════════════════
    #  STEP 6: Running Tests
    # ══════════════════════════════════════════════════════════════════
    def _build_running(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Running tests",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.run_phase_label = tk.Label(
            body, text="Starting…",
            font=self.f_body, bg=WHITE, fg=TEXT_LIGHT,
        )
        self.run_phase_label.pack(anchor="w", pady=(0, 2))

        # Live description of what's happening right now
        self.run_detail_label = tk.Label(
            body, text="",
            font=self.f_small, bg=WHITE, fg=TEXT_MUTED,
            wraplength=430, justify="left",
        )
        self.run_detail_label.pack(anchor="w", pady=(0, 10))

        # Progress bar
        style = ttk.Style()
        style.configure(
            "Run.Horizontal.TProgressbar",
            troughcolor=PROGRESS_TRACK, background=ACCENT, thickness=18,
        )
        self.run_progress = tk.DoubleVar(value=0)
        self.run_bar = ttk.Progressbar(
            body, variable=self.run_progress, maximum=100,
            style="Run.Horizontal.TProgressbar",
        )
        self.run_bar.pack(fill="x", pady=(0, 4))

        self.run_pct = tk.Label(
            body, text="0%", font=self.f_small, bg=WHITE, fg=TEXT_MUTED,
        )
        self.run_pct.pack(anchor="e", pady=(0, 10))

        # Phase checklist
        self.phase_list = tk.Frame(body, bg=WHITE)
        self.phase_list.pack(fill="x")
        self.phase_widgets = {}

        # Time
        self.run_time_label = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=TEXT_MUTED,
        )
        self.run_time_label.pack(anchor="w", pady=(10, 0))

        # Stop button
        tk.Frame(parent, bg=WHITE).pack(fill="both", expand=True)
        stop_bar = tk.Frame(parent, bg=WHITE)
        stop_bar.pack(fill="x", side="bottom", padx=24, pady=(0, 14))
        self.stop_btn = ttk.Button(
            stop_bar, text="Stop", style="Nav.TButton",
            cursor="hand2", command=self._stop_run,
        )
        self.stop_btn.pack(side="right")

    def _populate_phases(self, phases):
        for w in self.phase_list.winfo_children():
            w.destroy()
        self.phase_widgets.clear()
        for ph in phases:
            row = tk.Frame(self.phase_list, bg=WHITE)
            row.pack(fill="x", pady=1)
            icon = tk.Label(
                row, text="○", font=self.f_small,
                bg=WHITE, fg=TEXT_MUTED, width=3,
            )
            icon.pack(side="left")
            lbl = tk.Label(
                row, text=PHASE_NAMES.get(ph, f"Phase {ph}"),
                font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            )
            lbl.pack(side="left")
            self.phase_widgets[ph] = {"icon": icon, "lbl": lbl}

    def _set_phase_status(self, ph, status):
        if ph not in self.phase_widgets:
            return
        w = self.phase_widgets[ph]
        if status == "running":
            w["icon"].config(text="▶", fg=ACCENT)
            w["lbl"].config(fg=TEXT, font=self.f_heading)
        elif status == "done":
            w["icon"].config(text="✓", fg=GREEN)
            w["lbl"].config(fg=GREEN, font=self.f_small)
        elif status == "fail":
            w["icon"].config(text="✗", fg=RED)
            w["lbl"].config(fg=RED, font=self.f_small)

    def _start_run(self):
        phases = [2, 3, 4]
        if self.selected_profile != "quick":
            phases = [2, 3, 4, 5, 6, 7]

        self.run_cancelled = False
        self.run_started_at = time.time()  # used to reject stale results
        self.run_progress.set(0)
        self.run_pct.config(text="0%")
        self.run_phase_label.config(text="Starting…")
        self.run_time_label.config(text="")
        self._populate_phases(phases)

        threading.Thread(
            target=self._execute_run, args=(phases,), daemon=True,
        ).start()

    def _execute_run(self, phases):
        t0 = time.time()

        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "run_test_suite.py"),
            "--profile", self.selected_profile,
            "--json",
        ]
        if self.selected_profile == "quick":
            cmd.append("--skip-model")
        if self.selected_profile != "anchor":
            cmd.append("--skip-anchor")

        total = len(phases)
        for i, ph in enumerate(phases):
            if self.run_cancelled:
                return
            pct = int((i / total) * 100)
            self.after(0, lambda p=pct, ph=ph: self._update_run_ui(p, ph))
            self.after(0, lambda ph=ph: self._set_phase_status(ph, "running"))

            if i == 0:
                # Run the actual test suite orchestrator
                try:
                    proc = subprocess.run(
                        cmd, capture_output=True, text=True,
                        cwd=str(SANDBOX), timeout=600,
                    )
                    self.run_returncode = proc.returncode

                    # Parse results and update phase statuses
                    # Only read results written AFTER this run started (avoid stale data)
                    json_path = RESULTS_DIR / "Candela Test Suite Results.json"
                    if (json_path.exists()
                            and json_path.stat().st_mtime >= self.run_started_at):
                        try:
                            data = json.loads(json_path.read_text())
                            for pr in data.get("phases", []):
                                p = pr.get("phase")
                                ok = pr.get(
                                    "all_passed",
                                    pr.get(
                                        "passed",
                                        not pr.get("skipped", False),
                                    ),
                                )
                                if p in self.phase_widgets:
                                    self.after(0, lambda p=p, s="done" if ok else "fail":
                                        self._set_phase_status(p, s))
                        except Exception:
                            pass
                except subprocess.TimeoutExpired:
                    self.run_returncode = 1
                except Exception:
                    self.run_returncode = 1

                self.after(0, lambda: self._update_run_ui(100, None))
                break

        elapsed = time.time() - t0
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        self.after(0, lambda: self.run_time_label.config(
            text=f"Completed in {mins}m {secs}s",
        ))

        report = str(RESULTS_DIR / "Candela Test Suite Results.md")

        # If full/anchor profile, always offer interactive session
        # (the model loaded even if some non-model phases had issues)
        if self.selected_profile != "quick":
            self.after(800, lambda: self._show_step(7))
        else:
            self.after(800, lambda: self._show_final_results(
                self.run_returncode == 0, report,
            ))

    def _update_run_ui(self, pct, phase):
        self.run_progress.set(pct)
        self.run_pct.config(text=f"{pct}%")
        if phase:
            self.run_phase_label.config(
                text=PHASE_NAMES.get(phase, f"Phase {phase}") + "…",
            )
            self.run_detail_label.config(
                text=PHASE_DETAIL.get(phase, ""),
            )

    def _stop_run(self):
        self.run_cancelled = True
        self.run_phase_label.config(text="Stopping…")
        self.after(1000, lambda: self._show_step(4))

    # ══════════════════════════════════════════════════════════════════
    #  STEP 7: Interactive Session
    # ══════════════════════════════════════════════════════════════════
    def _build_interact(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            body, text="Try it yourself",
            font=self.f_title, bg=WHITE, fg=TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.interact_status = tk.Label(
            body,
            text="The automated tests are done — now you can try it yourself.\n\n"
                 "The AI model is running with CANDELA watching every response. "
                 "Type anything below and see CANDELA check it in real time. "
                 "Try asking for something sensitive — like a password or credit "
                 "card number — and watch CANDELA catch it.",
            font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        )
        self.interact_status.pack(anchor="w", pady=(0, 10))

        # Chat-style display
        chat_frame = tk.Frame(
            body, bg=BG, relief="solid", bd=1,
            highlightbackground=CARD_BORDER, highlightthickness=1,
        )
        chat_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.chat_display = tk.Text(
            chat_frame, font=self.f_body, bg=BG, fg=TEXT,
            wrap="word", state="disabled", relief="flat",
            padx=10, pady=8,
        )
        chat_scroll = ttk.Scrollbar(
            chat_frame, orient="vertical",
            command=self.chat_display.yview,
        )
        self.chat_display.configure(yscrollcommand=chat_scroll.set)
        self.chat_display.pack(side="left", fill="both", expand=True)
        chat_scroll.pack(side="right", fill="y")

        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground=ACCENT, font=self.f_heading)
        self.chat_display.tag_configure("ai", foreground=TEXT)
        self.chat_display.tag_configure("system", foreground=GREEN, font=self.f_small)
        self.chat_display.tag_configure("warning", foreground=RED, font=self.f_small)

        # Input area
        input_frame = tk.Frame(body, bg=WHITE)
        input_frame.pack(fill="x", pady=(0, 4))

        self.chat_input = tk.Entry(
            input_frame, font=self.f_body,
            bg=BG, fg=TEXT, relief="solid", bd=1,
        )
        self.chat_input.pack(side="left", fill="x", expand=True, ipady=4)
        self.chat_input.bind("<Return>", self._on_chat_send)

        self.chat_send_btn = ttk.Button(
            input_frame, text="Send", style="NavAccent.TButton",
            cursor="hand2", command=self._on_chat_send,
        )
        self.chat_send_btn.pack(side="right", padx=(6, 0))

        # Bottom nav
        bottom = tk.Frame(parent, bg=WHITE)
        bottom.pack(fill="x", side="bottom", padx=24, pady=(0, 14))

        ttk.Button(
            bottom, text="Back", style="Nav.TButton",
            cursor="hand2",
            command=lambda: self._show_step(6),
        ).pack(side="left")

        self.interact_candela_status = tk.Label(
            bottom, text="CANDELA: Active ✓",
            font=self.f_badge, bg=WHITE, fg=GREEN,
        )
        self.interact_candela_status.pack(side="left", padx=(12, 0))

        ttk.Button(
            bottom, text="Finish & see results",
            style="NavAccent.TButton", cursor="hand2",
            command=self._finish_interact,
        ).pack(side="right")

    def _append_chat(self, text, tag="ai"):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text + "\n", tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _on_chat_send(self, event=None):
        msg = self.chat_input.get().strip()
        if not msg:
            return
        self.chat_input.delete(0, "end")

        self._append_chat(f"You: {msg}", "user")
        self._append_chat("Thinking…", "system")

        # Send to model in background
        threading.Thread(
            target=self._send_to_model, args=(msg,), daemon=True,
        ).start()

    def _send_to_model(self, user_msg):
        """
        Send a prompt to the CANDELA-wrapped model and show the response.
        This is a simplified demo — in production, this would use the full
        demo_model_guardian pipeline.
        """
        try:
            cmd = [
                sys.executable,
                str(SANDBOX / "demo_model_guardian.py"),
                "--prompt", user_msg,
                "--mode", "strict",
                "--max-tokens", "150",
            ]
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(SANDBOX), timeout=120,
            )

            # Remove the "Thinking…" line
            self.after(0, lambda: self._remove_last_chat_line())

            if proc.returncode == 0:
                # Parse output for model response and CANDELA verdict
                output = proc.stdout.strip()
                # Show model response
                self.after(0, lambda: self._append_chat(
                    f"AI: {output}", "ai",
                ))
                # Check for CANDELA flags in stderr or output
                if "VIOLATION" in proc.stderr.upper() or "BLOCKED" in proc.stderr.upper():
                    self.after(0, lambda: self._append_chat(
                        "⚠ CANDELA detected a rule violation in this response",
                        "warning",
                    ))
                else:
                    self.after(0, lambda: self._append_chat(
                        "✓ CANDELA: Response checked — no violations found",
                        "system",
                    ))
            else:
                self.after(0, lambda: self._append_chat(
                    f"(Model returned an error. This is normal during testing.)",
                    "system",
                ))

        except subprocess.TimeoutExpired:
            self.after(0, lambda: self._remove_last_chat_line())
            self.after(0, lambda: self._append_chat(
                "(Response timed out — the model may need more time.)",
                "system",
            ))
        except Exception as ex:
            self.after(0, lambda: self._remove_last_chat_line())
            self.after(0, lambda: self._append_chat(
                f"(Could not reach the model: {ex})",
                "system",
            ))

    def _remove_last_chat_line(self):
        self.chat_display.configure(state="normal")
        # Remove last line (the "Thinking…" message)
        content = self.chat_display.get("1.0", "end-1c")
        lines = content.split("\n")
        if lines and "Thinking" in lines[-1]:
            self.chat_display.delete(f"end-{len(lines[-1])+1}c", "end")
        self.chat_display.configure(state="disabled")

    def _finish_interact(self):
        report = str(RESULTS_DIR / "Candela Test Suite Results.md")
        passed = getattr(self, "run_returncode", 1) == 0
        self._show_final_results(passed, report)

    # ══════════════════════════════════════════════════════════════════
    #  STEP 8: Results
    # ══════════════════════════════════════════════════════════════════
    def _build_results(self, parent):
        body = tk.Frame(parent, bg=WHITE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        self.result_icon_lbl = tk.Label(
            body, text="", font=self.f_big, bg=WHITE,
        )
        self.result_icon_lbl.pack(pady=(8, 2))

        self.result_text_lbl = tk.Label(
            body, text="", font=self.f_title, bg=WHITE, fg=TEXT,
        )
        self.result_text_lbl.pack(pady=(0, 6))

        self.result_detail = tk.Frame(
            body, bg=BG, relief="solid", bd=1,
            highlightbackground=CARD_BORDER, highlightthickness=1,
        )
        self.result_detail.pack(fill="x", pady=(0, 6))

        # Explanation of what the results mean
        self.result_explain = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=TEXT,
            wraplength=430, justify="left",
        )
        self.result_explain.pack(anchor="w", pady=(2, 4))

        self.result_report = tk.Label(
            body, text="", font=self.f_small, bg=WHITE, fg=TEXT_LIGHT,
            wraplength=430, justify="left",
        )
        self.result_report.pack(anchor="w", pady=(0, 6))

        # Action buttons — consistent style
        btn_frame = tk.Frame(body, bg=WHITE)
        btn_frame.pack(pady=4)

        ttk.Button(
            btn_frame, text="Run again", style="Nav.TButton",
            cursor="hand2",
            command=lambda: self._show_step(0),
        ).pack(side="left", padx=6)

        ttk.Button(
            btn_frame, text="Exit", style="NavAccent.TButton",
            cursor="hand2",
            command=self.quit,
        ).pack(side="left", padx=6)

    def _show_final_results(self, passed: bool, report_path: str):
        if passed:
            self.result_icon_lbl.config(text="✓", fg=GREEN)
            self.result_text_lbl.config(text="All tests passed", fg=GREEN)
        else:
            self.result_icon_lbl.config(text="✗", fg=RED)
            self.result_text_lbl.config(
                text="Some tests did not pass", fg=RED,
            )

        for w in self.result_detail.winfo_children():
            w.destroy()

        # Parse JSON results if available — only from THIS run (reject stale files)
        json_path = RESULTS_DIR / "Candela Test Suite Results.json"
        total, ok = 0, 0
        run_start = getattr(self, "run_started_at", 0)
        if (json_path.exists()
                and json_path.stat().st_mtime >= run_start):
            try:
                data = json.loads(json_path.read_text())
                for pr in data.get("phases", []):
                    for t in pr.get("tests", []):
                        total += 1
                        if t.get("passed"):
                            ok += 1
            except Exception:
                pass

        failed = total - ok if total else 0
        for label, val, color in [
            ("Tests run", str(total or "—"), TEXT),
            ("Passed", str(ok or "—"), GREEN),
            ("Failed", str(failed or "—"), GREEN if failed == 0 else RED),
        ]:
            row = tk.Frame(self.result_detail, bg=BG)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(
                row, text=f"{label}:",
                font=self.f_small, bg=BG, fg=TEXT_MUTED,
                width=12, anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=val,
                font=self.f_heading, bg=BG, fg=color,
            ).pack(side="left")
        tk.Frame(self.result_detail, bg=BG, height=6).pack()

        # What this means — give the user context
        if passed:
            meaning = (
                "CANDELA checked every AI response against your chosen safety "
                "rules and correctly caught all the violations it was supposed to. "
                "This means the system is working as designed — it can detect "
                "leaked passwords, credit card numbers, personal data, and other "
                "sensitive content before it reaches end users.\n\n"
                "This is the evidence organisations need to demonstrate AI "
                "compliance to regulators, auditors, and stakeholders."
            )
        else:
            meaning = (
                "Some checks did not behave as expected. This could mean "
                "certain safety rules need attention, or the AI model "
                "produced unexpected responses. Review the detailed report "
                "below for specifics on what failed and why.\n\n"
                "Even partial results demonstrate that CANDELA is actively "
                "monitoring AI output — the report shows exactly what was "
                "tested and where issues were found."
            )
        self.result_explain.config(text=meaning)

        # Report location
        if Path(report_path).exists():
            self.result_report.config(
                text=f"Your report has been saved to:\n{report_path}\n\n"
                     "Share this with reviewers, auditors, or compliance officers "
                     "as evidence that CANDELA is working. The report will remain "
                     "on your computer until you delete it.",
            )
        else:
            self.result_report.config(
                text="The report will be available once the test completes.",
            )

        self._show_step(8)

    # ── Help ───────────────────────────────────────────────────────────
    def _show_help(self, event=None):
        messagebox.showinfo(
            "About CANDELA Test Suite",
            "CANDELA stands for Compliant Auditable Natural-language "
            "Directive Enforcement & Ledger Anchoring.\n\n"
            "It is a system that checks whether AI-generated text follows "
            "safety and compliance rules. Every check is logged, and the "
            "logs can be permanently recorded on a blockchain.\n\n"
            "This test suite verifies that CANDELA itself is working "
            "correctly. It produces a detailed report that can be shared "
            "with reviewers, auditors, or anyone who needs proof that "
            "the system works.\n\n"
            "Steps:\n"
            "1. Choose how thorough a test to run\n"
            "2. Pick an AI model to test against\n"
            "3. Choose which safety rules to check\n"
            "4. Review and run\n"
            "5. See results and share the report\n\n"
            "For technical details, see the project documentation.",
        )


# ══════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = CandelaWizard()
    app.mainloop()
