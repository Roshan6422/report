"""
desktop_app.py
==============
CustomTkinter-based desktop GUI for Sri Lanka Police AI Report Generator.
Features: PDF upload, Turbo processing, Dashboard with 29-category table,
          OCR → Translate → PDF workflow, API key management, Recent reports history.

Usage:
    python desktop_app.py
"""

from __future__ import annotations  # Python 3.9+ compatibility for str | None syntax

import os
import sys
import threading
import traceback
from typing import Any, Dict, List, Optional
from datetime import datetime

import customtkinter as ctk
import pyperclip
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

# Local project imports
from ai_engine_manager import get_engine
from api_keys import delete_gemini_api_keys, get_gemini_key_display, save_gemini_api_key
from db_manager import get_recent_files
from desktop_pipeline import (
    process_pdf_hyper_hybrid,
    process_pdf_kaggle_cloud_hybrid,
    process_pdf_kaggle_only,
    process_text_report,
    parse_incidents_from_text,
)
from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES

# ── UTF-8 Enforcer (Windows compatibility) ───────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

try:
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NotoSansSinhala-Regular.ttf")
    if os.path.exists(font_path):
        ctk.FontManager.load_font(font_path)
except Exception as e:
    print(f"Notice: Custom font loading skipped: {e}")


class PoliceDesktopApp(ctk.CTk):
    """
    Main desktop application for Sri Lanka Police AI Report Generator.
    Provides GUI for PDF processing, dashboard viewing, and OCR/Translate workflow.
    """

    # English labels matching the 29-row official table on the last PDF page
    _TABLE_LABELS = [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
        "21", "22", "23", "24", "25", "26", "27", "28", "29",
    ]

    def __init__(self) -> None:
        super().__init__()

        self.title("Police AI — Fast Report Generator")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Layout: 2-column
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State variables
        self.current_pdf: Optional[str] = None
        self.generated_pdfs: List[str] = []
        self.generated_words: List[str] = []
        self.last_results: Dict[str, Any] = {}
        self.chart_refs: Dict[str, Any] = {}  # To prevent PIL Image GC

        # Build UI
        self._build_sidebar()
        self._build_main_area()

        # Start background tasks
        self.after(1000, self.update_ollama_status)
        self.after(1500, self.refresh_recent_reports)
        self.after(2000, self.refresh_api_status)

    # ═════════════════════════════════════════════════════════════════════════
    # SIDEBAR BUILD
    # ═════════════════════════════════════════════════════════════════════════

    def _build_sidebar(self) -> None:
        """Build the left sidebar with controls and status."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Logo
        ctk.CTkLabel(
            self.sidebar, text="⚡ Police AI",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, padx=20, pady=(25, 5))
        
        ctk.CTkLabel(
            self.sidebar, text="Fast Report v2.2 [STABLE]",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        ).grid(row=1, column=0, padx=20, pady=(0, 25))

        # Upload Button (BIG)
        self.upload_btn = ctk.CTkButton(
            self.sidebar, text="📁  Select PDF", height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1e40af", hover_color="#1d4ed8",
            command=self.select_pdf
        )
        self.upload_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Process Button (BIG, GREEN)
        self.process_btn = ctk.CTkButton(
            self.sidebar, text="⚡  Process Now", height=55,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#059669", hover_color="#10b981",
            command=self.start_processing
        )
        self.process_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Kaggle Fast Button (ORANGE — skips cloud validation)
        self.kaggle_fast_btn = ctk.CTkButton(
            self.sidebar, text="🚀  Kaggle Fast", height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#d97706", hover_color="#f59e0b",
            command=self.start_kaggle_fast
        )
        self.kaggle_fast_btn.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Pipeline mode selector
        ctk.CTkLabel(
            self.sidebar, text="Pipeline",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cbd5e1"
        ).grid(row=5, column=0, padx=20, pady=(8, 2), sticky="w")
        
        self.pipeline_mode_var = ctk.StringVar(value="1 — Fast (Turbo first)")
        self.pipeline_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=[
                "1 — Fast (Turbo first)",
                "2 — Sinhala split first",
            ],
            variable=self.pipeline_mode_var,
            width=180,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="#1e3a5f",
            button_color="#2563eb",
            button_hover_color="#1d4ed8",
        )
        self.pipeline_menu.grid(row=6, column=0, padx=20, pady=(0, 6), sticky="ew")

        # Progress bar
        self.progress = ctk.CTkProgressBar(self.sidebar, height=8)
        self.progress.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.progress.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Ready — Select a PDF",
            font=ctk.CTkFont(size=11), text_color="#94a3b8",
            wraplength=180
        )
        self.status_label.grid(row=8, column=0, padx=20, pady=(0, 10))

        # Local Engine Status
        self.ollama_status = ctk.CTkLabel(
            self.sidebar, text="🤖 Local AI Engine Ready",
            font=ctk.CTkFont(size=10), text_color="#64748b",
            wraplength=180
        )
        self.ollama_status.grid(row=9, column=0, padx=20, pady=(5, 5))

        # ── Toggle Switches (always visible) ──────────────────────
        self.toggle_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        self.toggle_frame.grid(row=10, column=0, padx=15, pady=(5, 5), sticky="ew")

        self.turbo_switch = ctk.CTkSwitch(
            self.toggle_frame, text="⚡ Turbo Speed",
            font=ctk.CTkFont(size=11),
            progress_color="#10b981",
            command=self.toggle_turbo_mode
        )
        self.turbo_switch.pack(anchor="w", padx=10, pady=(8, 4))
        if os.environ.get("AI_DISPATCH_MODE") == "race":
            self.turbo_switch.select()

        self.kaggle_switch = ctk.CTkSwitch(
            self.toggle_frame, text="🌐 Kaggle AI (Remote)",
            font=ctk.CTkFont(size=11),
            progress_color="#38bdf8",
            command=self.toggle_kaggle_mode
        )
        self.kaggle_switch.pack(anchor="w", padx=10, pady=(4, 8))

        # Load default from config
        try:
            if get_engine().prefer_kaggle_ollama:
                self.kaggle_switch.select()
        except Exception:
            pass

        # Recent Reports Section
        ctk.CTkLabel(
            self.sidebar, text="🕒 Recent Reports",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=11, column=0, padx=20, pady=(10, 2), sticky="w")

        self.recent_container = ctk.CTkFrame(
            self.sidebar, fg_color="#1e293b", corner_radius=6
        )
        self.recent_container.grid(row=12, column=0, padx=15, pady=5, sticky="nsew")
        self.recent_container.grid_columnconfigure(0, weight=1)

        self.recent_scroll = ctk.CTkScrollableFrame(
            self.recent_container, height=140, fg_color="transparent"
        )
        self.recent_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # API Status Section
        ctk.CTkLabel(
            self.sidebar, text="🌐 API Health",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        ).grid(row=13, column=0, padx=20, pady=(10, 2), sticky="w")

        self.api_status_box = ctk.CTkTextbox(
            self.sidebar, height=80, width=180, font=ctk.CTkFont(size=10),
            fg_color="#0f172a", text_color="#64748b", corner_radius=6
        )
        self.api_status_box.grid(row=14, column=0, padx=20, pady=5)
        self.api_status_box.insert("0.0", "Checking...")
        self.api_status_box.configure(state="disabled")

        self.refresh_api_btn = ctk.CTkButton(
            self.sidebar, text="🔄 Refresh API", height=24,
            font=ctk.CTkFont(size=10), fg_color="#334155",
            command=self.refresh_api_status
        )
        self.refresh_api_btn.grid(row=15, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Spacer
        self.sidebar.grid_rowconfigure(15, weight=1)

        # Appearance toggle
        self.appearance = ctk.CTkOptionMenu(
            self.sidebar, values=["Dark", "Light"],
            width=100, command=ctk.set_appearance_mode
        )
        self.appearance.grid(row=16, column=0, padx=20, pady=(0, 15))
        self.appearance.set("Dark")

    # ═════════════════════════════════════════════════════════════════════════
    # MAIN AREA BUILD
    # ═════════════════════════════════════════════════════════════════════════

    def _build_main_area(self) -> None:
        """Build the main content area with tabs."""
        self.main = ctk.CTkFrame(self, corner_radius=12)
        self.main.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        # Header bar
        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(
            self.header, text="No PDF selected",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#94a3b8"
        )
        self.file_label.grid(row=0, column=0, sticky="w")

        self.copy_btn = ctk.CTkButton(
            self.header, text="📋 Copy", width=90, height=32,
            fg_color="#334155", hover_color="#475569",
            command=self.copy_result
        )
        self.copy_btn.grid(row=0, column=1, padx=5)

        # Tabview: Dashboard + Preview + OCR/Translate + Paste + API Keys
        self.tabs = ctk.CTkTabview(self.main, height=500)
        self.tabs.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.tabs.add("📊 Dashboard")
        self.tabs.add("📝 Translation Preview")
        self.tabs.add("🔤 OCR & Translate")  # REPLACED Analytics
        self.tabs.add("📋 Paste text")
        self.tabs.add("🔑 API Keys")

        # Build each tab
        self._build_dashboard_tab()
        self._build_preview_tab()
        self._build_ocr_translate_tab()  # REPLACED Analytics builder
        self._build_paste_tab()
        self._build_api_keys_tab()

        # Report buttons row (bottom)
        self.report_row = ctk.CTkFrame(self.main, fg_color="transparent")
        self.report_row.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.report_row.grid_columnconfigure((0, 1), weight=1)

    def _build_dashboard_tab(self) -> None:
        """Build the Dashboard tab with summary table and category cards."""
        self.dash_frame = ctk.CTkScrollableFrame(
            self.tabs.tab("📊 Dashboard"), fg_color="transparent"
        )
        self.dash_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.cat_widgets: Dict[str, Dict[str, Any]] = {}
        self._build_summary_table()
        self._build_category_cards()

    def _build_summary_table(self) -> None:
        """Build the 5-column summary table (No | Incident | Reported | Solved | Unsolved)."""
        card = ctk.CTkFrame(self.dash_frame, fg_color="#0f172a", corner_radius=10)
        card.pack(fill="x", padx=8, pady=(8, 2))

        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            title_row,
            text="📊  Daily Incident Summary Table",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#38bdf8",
        ).pack(side="left")
        
        self.table_date_label = ctk.CTkLabel(
            title_row, text="", font=ctk.CTkFont(size=11), text_color="#64748b"
        )
        self.table_date_label.pack(side="right")

        HDR_BG = "#1e3a5f"
        hdr = ctk.CTkFrame(card, fg_color=HDR_BG, corner_radius=6)
        hdr.pack(fill="x", padx=8, pady=(2, 0))
        hdr.grid_columnconfigure(1, weight=1)
        
        for col, (txt, w) in enumerate([
            ("No.", 38), ("Incident Category", 0), ("Reported", 72), ("Solved", 72), ("Unsolved", 72)
        ]):
            anchor = "w" if col == 1 else "center"
            ctk.CTkLabel(
                hdr, text=txt, width=w, font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#93c5fd", anchor=anchor,
            ).grid(row=0, column=col, padx=(6 if col == 0 else 2), pady=4, sticky="ew" if col == 1 else "")

        self._sum_row_widgets: Dict[str, Dict[str, Any]] = {}
        
        for idx, num in enumerate(self._TABLE_LABELS):
            label = next(
                (c for c in OFFICIAL_CASE_TABLE_CATEGORIES if c.split(".")[0].strip().zfill(2) == num),
                f"{num}. —"
            )
            incident_name = label.split(".", 1)[1].strip() if "." in label else label

            row_bg = "#0d1b2a" if idx % 2 == 0 else "#0f172a"
            row = ctk.CTkFrame(card, fg_color=row_bg, height=28, corner_radius=0)
            row.pack(fill="x", padx=8, pady=0)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=num, width=38, font=ctk.CTkFont(size=11),
                text_color="#64748b", anchor="center",
            ).grid(row=0, column=0, padx=6, pady=2)

            ctk.CTkLabel(
                row, text=incident_name, font=ctk.CTkFont(size=11),
                text_color="#cbd5e1", anchor="w",
            ).grid(row=0, column=1, padx=4, pady=2, sticky="ew")

            rep_lbl = ctk.CTkLabel(
                row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#4b5563", anchor="center"
            )
            rep_lbl.grid(row=0, column=2, padx=2, pady=2)

            sol_lbl = ctk.CTkLabel(
                row, text="—", width=72, font=ctk.CTkFont(size=11),
                text_color="#4b5563", anchor="center"
            )
            sol_lbl.grid(row=0, column=3, padx=2, pady=2)

            uns_lbl = ctk.CTkLabel(
                row, text="—", width=72, font=ctk.CTkFont(size=11),
                text_color="#4b5563", anchor="center"
            )
            uns_lbl.grid(row=0, column=4, padx=2, pady=2)

            self._sum_row_widgets[num] = {
                "rep": rep_lbl, "sol": sol_lbl, "uns": uns_lbl, "row": row
            }

        tot_row = ctk.CTkFrame(card, fg_color="#1e3a5f", corner_radius=0)
        tot_row.pack(fill="x", padx=8, pady=(0, 8))
        tot_row.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            tot_row, text="TOTAL", font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#93c5fd", anchor="w"
        ).grid(row=0, column=0, columnspan=2, padx=8, pady=3, sticky="w")
        
        self._tot_rep = ctk.CTkLabel(
            tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#38bdf8", anchor="center"
        )
        self._tot_rep.grid(row=0, column=2, padx=2, pady=3)
        
        self._tot_sol = ctk.CTkLabel(
            tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#22c55e", anchor="center"
        )
        self._tot_sol.grid(row=0, column=3, padx=2, pady=3)
        
        self._tot_uns = ctk.CTkLabel(
            tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#f87171", anchor="center"
        )
        self._tot_uns.grid(row=0, column=4, padx=2, pady=3)

        ctk.CTkFrame(self.dash_frame, fg_color="#1e293b", height=2).pack(fill="x", padx=8, pady=(4, 8))

    def _build_category_cards(self) -> None:
        """Build compact 29-category dashboard cards below the summary table."""
        for cat_name in OFFICIAL_CASE_TABLE_CATEGORIES:
            cat_num = cat_name.split(".")[0].strip()

            row = ctk.CTkFrame(self.dash_frame, height=36)
            row.pack(fill="x", padx=8, pady=1)

            dot = ctk.CTkLabel(
                row, text="●", text_color="#4b5563",
                font=ctk.CTkFont(size=14), width=20
            )
            dot.pack(side="left", padx=(10, 5))

            lbl = ctk.CTkLabel(
                row, text=cat_name, font=ctk.CTkFont(size=12), anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True, padx=5)

            count_lbl = ctk.CTkLabel(
                row, text="—", text_color="#6b7280",
                font=ctk.CTkFont(size=11, weight="bold"), width=80
            )
            count_lbl.pack(side="right", padx=10)

            for w in (row, lbl, dot):
                w.bind("<Button-1>", lambda e, n=cat_num: self._show_detail(n))

            self.cat_widgets[cat_num] = {"row": row, "dot": dot, "count": count_lbl}

    def _build_preview_tab(self) -> None:
        """Build the Translation Preview tab."""
        self.preview_text = ctk.CTkTextbox(
            self.tabs.tab("📝 Translation Preview"),
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)

    # ═════════════════════════════════════════════════════════════════════════
    # 🆕 OCR & TRANSLATE TAB (REPLACES ANALYTICS)
    # ═════════════════════════════════════════════════════════════════════════

    def _build_ocr_translate_tab(self) -> None:
        """OCR Sinhala Text → Translate → PDF Generator tab."""
        tab = self.tabs.tab("🔤 OCR & Translate")

        self.ocr_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.ocr_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            self.ocr_scroll,
            text="📋 Paste Sinhala Text from OCR / Manual Entry",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            self.ocr_scroll,
            text="OCR කරපු හෝ manual input කළ සිංහල වාර්තාව මෙතනට paste කරන්න. \nපසුව category select කරලා translate කරන්න.",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            justify="left"
        ).pack(pady=(0, 10))

        # Sinhala Text Input Area
        self.ocr_text_input = ctk.CTkTextbox(
            self.ocr_scroll,
            height=300,
            font=ctk.CTkFont(family="Noto Sans Sinhala", size=14),
            border_width=2,
            border_color="#334155"
        )
        self.ocr_text_input.pack(fill="both", expand=True, pady=10)
        self.ocr_text_input.insert("1.0", "මෙතනට සිංහල පෙළ paste කරන්න...")

        # Category Selection
        cat_frame = ctk.CTkFrame(self.ocr_scroll, fg_color="#1e293b")
        cat_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            cat_frame,
            text="Category තෝරන්න:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cbd5e1"
        ).pack(side="left", padx=10)

        self.category_var = ctk.StringVar(value="01")
        self.category_menu = ctk.CTkOptionMenu(
            cat_frame,
            values=self._TABLE_LABELS,
            variable=self.category_var,
            width=200,
            height=32,
            font=ctk.CTkFont(size=11)
        )
        self.category_menu.pack(side="left", padx=10)

        # Translate Button
        self.translate_btn = ctk.CTkButton(
            self.ocr_scroll,
            text="🔄 Translate to English",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#10b981",
            command=self.start_translation
        )
        self.translate_btn.pack(pady=10, fill="x", padx=20)

        # Progress indicator
        self.translate_progress = ctk.CTkProgressBar(self.ocr_scroll, height=6)
        self.translate_progress.pack(fill="x", padx=20, pady=5)
        self.translate_progress.set(0)

        # Translation Result Area (initially hidden)
        self.translation_result_frame = ctk.CTkFrame(
            self.ocr_scroll, 
            fg_color="#0f172a",
            corner_radius=10
        )
        # Don't pack yet - show after translation

        ctk.CTkLabel(
            self.translation_result_frame,
            text="✅ Translation Complete",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#22c55e"
        ).pack(pady=(10, 5))

        self.translation_output = ctk.CTkTextbox(
            self.translation_result_frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled"
        )
        self.translation_output.pack(fill="both", expand=True, padx=10, pady=5)

        # Generate PDFs Button
        self.generate_pdfs_btn = ctk.CTkButton(
            self.translation_result_frame,
            text="📄 Generate PDF Report",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#4f46e5",
            hover_color="#6366f1",
            command=self.generate_both_pdfs_from_translation
        )
        self.generate_pdfs_btn.pack(pady=10, fill="x", padx=20)

        # Store translation results
        self.current_translation_data = None

    def start_translation(self) -> None:
        """Start translation process for pasted Sinhala text."""
        sinhala_text = self.ocr_text_input.get("1.0", "end-1c").strip()
        
        if len(sinhala_text) < 20:
            messagebox.showwarning(
                "Text Too Short",
                "Please paste more Sinhala text (at least 20 characters).\nවැඩිපුර සිංහල පෙළක් paste කරන්න."
            )
            return

        selected_cat = self.category_var.get()
        
        self.translate_btn.configure(state="disabled", text="⏳ Translating...")
        self.translate_progress.set(0)
        self.translate_progress.start()

        def worker():
            try:
                from machine_translator import MachineTranslator
                translator = MachineTranslator()
                
                english_text = translator.translate_sinhala_to_english(sinhala_text)
                incidents = parse_incidents_from_text(sinhala_text, selected_cat)
                
                self.current_translation_data = {
                    "category": selected_cat,
                    "sinhala_text": sinhala_text,
                    "english_translation": english_text,
                    "incidents": incidents
                }
                
                self.after(0, lambda: self._on_translation_complete(english_text, incidents))
            except Exception as e:
                print(f"[Translation Error] {e}")
                self.after(0, lambda m=str(e): self._on_translation_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def _on_translation_complete(self, english_text: str, incidents: list) -> None:
        """Called when translation is complete."""
        self.translate_progress.stop()
        self.translate_progress.set(1.0)
        self.translate_btn.configure(state="normal", text="🔄 Translate to English")

        self.translation_result_frame.pack(fill="x", pady=10, padx=5)

        self.translation_output.configure(state="normal")
        self.translation_output.delete("1.0", "end")
        self.translation_output.insert("1.0", english_text)
        self.translation_output.insert("end", f"\n\n--- Incidents Found: {len(incidents)} ---\n")
        for i, inc in enumerate(incidents, 1):
            self.translation_output.insert("end", f"\n{i}. {inc.get('station', 'Unknown')}: {inc.get('summary', '')}\n")
        self.translation_output.configure(state="disabled")

        self.status_label.configure(
            text=f"✅ Translation complete - Category {self.category_var.get()}: {len(incidents)} incidents"
        )

    def _on_translation_error(self, msg: str) -> None:
        """Handle translation errors."""
        self.translate_progress.stop()
        self.translate_progress.set(0)
        self.translate_btn.configure(state="normal", text="🔄 Translate to English")
        messagebox.showerror("Translation Error", f"Failed to translate:\n{msg}")
        self.status_label.configure(text="❌ Translation failed")

    def generate_both_pdfs_from_translation(self) -> None:
        """Generate PDF report from translation data."""
        if not self.current_translation_data:
            messagebox.showwarning("No Data", "Please translate text first.")
            return

        self.generate_pdfs_btn.configure(state="disabled", text="⏳ Generating...")

        def worker():
            try:
                from web_report_engine_v2 import generate_security_report, generate_general_report
                
                category = self.current_translation_data["category"]
                incidents = self.current_translation_data["incidents"]
                
                cat_num = int(category)
                is_security = cat_num in [1, 2, 3]
                
                sections_data = {
                    "date_range": "From 0400 hrs. on " + datetime.now().strftime("%d %B %Y"),
                    "sections": [
                        {
                            "title": f"{category}. TRANSLATED INCIDENTS:",
                            "provinces": [
                                {
                                    "name": "WESTERN",
                                    "incidents": incidents,
                                    "nil": len(incidents) == 0
                                }
                            ]
                        }
                    ]
                }

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                generated_files = []

                if is_security:
                    sec_pdf_path = f"outputs/Security_Translated_{timestamp}.html"
                    os.makedirs("outputs", exist_ok=True)
                    generate_security_report(sections_data, sec_pdf_path)
                    generated_files.append(sec_pdf_path)
                    print(f"[PDF] Security report generated: {sec_pdf_path}")
                else:
                    gen_pdf_path = f"outputs/General_Translated_{timestamp}.html"
                    os.makedirs("outputs", exist_ok=True)
                    generate_general_report(sections_data, gen_pdf_path)
                    generated_files.append(gen_pdf_path)
                    print(f"[PDF] General report generated: {gen_pdf_path}")

                self.after(0, lambda files=generated_files: self._on_pdfs_generated(files))

            except Exception as e:
                print(f"[PDF Generation Error] {e}")
                import traceback
                traceback.print_exc()
                self.after(0, lambda m=str(e): self._on_pdf_generation_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def _on_pdfs_generated(self, files: list) -> None:
        """Called when PDFs are generated."""
        self.generate_pdfs_btn.configure(state="normal", text="📄 Generate PDF Report")
        
        if files:
            self.status_label.configure(text=f"✅ PDFs generated successfully! ({len(files)} files)")
            for f_path in files:
                self._open_report_path(f_path)
            messagebox.showinfo("Success", f"PDF reports generated successfully!\n\nFiles:\n" + "\n".join(files))
        else:
            messagebox.showwarning("Warning", "No PDFs were generated.")

    def _on_pdf_generation_error(self, msg: str) -> None:
        """Handle PDF generation errors."""
        self.generate_pdfs_btn.configure(state="normal", text="📄 Generate PDF Report")
        messagebox.showerror("PDF Generation Error", f"Failed to generate PDFs:\n{msg}")
        self.status_label.configure(text="❌ PDF generation failed")

    # ═════════════════════════════════════════════════════════════════════════
    # PASTE & API TABS
    # ═════════════════════════════════════════════════════════════════════════

    def _build_paste_tab(self) -> None:
        paste_tab = self.tabs.tab("📋 Paste text")
        paste_wrap = ctk.CTkFrame(paste_tab, fg_color="transparent")
        paste_wrap.pack(fill="both", expand=True, padx=12, pady=10)
        
        ctk.CTkLabel(
            paste_wrap,
            text="වාර්තාවේ සම්පූර්ණ සිංහල පෙළ මෙතන paste කරන්න (Ctrl+V). PDF එකක් නැතිව වැඩ කරන්න මෙම මාර්ගය භාවිතා කරන්න.",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8",
            wraplength=880,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))
        
        self.paste_input = ctk.CTkTextbox(paste_wrap, height=400, font=ctk.CTkFont(family="Consolas", size=12))
        self.paste_input.pack(fill="both", expand=True, pady=4)
        self.paste_input.bind("<Control-Return>", lambda e: self.start_processing_paste())
        
        self.paste_process_btn = ctk.CTkButton(
            paste_wrap, text="⚡ Process pasted text", height=44,
            font=ctk.CTkFont(size=15, weight="bold"), fg_color="#7c3aed", hover_color="#6d28d9",
            command=self.start_processing_paste,
        )
        self.paste_process_btn.pack(pady=(10, 4))

    def _build_api_keys_tab(self) -> None:
        keys_tab = self.tabs.tab("🔑 API Keys")
        keys_wrap = ctk.CTkFrame(keys_tab, fg_color="transparent")
        keys_wrap.pack(fill="both", expand=True, padx=16, pady=12)
        
        ctk.CTkLabel(keys_wrap, text="Google Gemini (Generative Language API)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e2e8f0").pack(anchor="w", pady=(0, 6))
        self.gemini_status_label = ctk.CTkLabel(keys_wrap, text="", font=ctk.CTkFont(size=12), text_color="#94a3b8", wraplength=900, justify="left")
        self.gemini_status_label.pack(anchor="w", pady=(0, 12))
        
        ctk.CTkLabel(keys_wrap, text="Paste new key (hidden):", font=ctk.CTkFont(size=12), text_color="#cbd5e1").pack(anchor="w")
        self.gemini_entry = ctk.CTkEntry(keys_wrap, placeholder_text="AIza…", width=720, height=36, font=ctk.CTkFont(size=12), show="*")
        self.gemini_entry.pack(anchor="w", pady=(6, 12))
        
        key_btn_row = ctk.CTkFrame(keys_wrap, fg_color="transparent")
        key_btn_row.pack(anchor="w", pady=4)
        
        ctk.CTkButton(key_btn_row, text="💾 Save Gemini key", width=180, height=36, fg_color="#059669", hover_color="#10b981", command=self._save_gemini_key_from_ui).pack(side="left", padx=(0, 10))
        ctk.CTkButton(key_btn_row, text="🗑 Remove saved keys", width=180, height=36, fg_color="#b91c1c", hover_color="#dc2626", command=self._delete_gemini_key_from_ui).pack(side="left", padx=(0, 10))
        ctk.CTkButton(key_btn_row, text="↻ Refresh status", width=140, height=36, fg_color="#334155", command=self._refresh_gemini_key_ui).pack(side="left")
        
        ctk.CTkLabel(keys_wrap, text="Saves to gemini_keys.json and GEMINI_API_KEY in .env.", font=ctk.CTkFont(size=11), text_color="#64748b", wraplength=900, justify="left").pack(anchor="w", pady=(16, 0))
        self._refresh_gemini_key_ui()

    # ═════════════════════════════════════════════════════════════════════════
    # UI UPDATE METHODS
    # ═════════════════════════════════════════════════════════════════════════

    def _update_summary_table(self, summary_table: Dict[str, Any], date_range: str = "") -> None:
        if date_range: self.table_date_label.configure(text=date_range)
        tot_rep = tot_sol = tot_uns = 0
        
        for num, widgets in self._sum_row_widgets.items():
            row_data = summary_table.get(num, {"reported": 0, "solved": 0, "unsolved": 0})
            rep, sol, uns = row_data.get("reported", 0), row_data.get("solved", 0), row_data.get("unsolved", 0)
            tot_rep, tot_sol, tot_uns = tot_rep + rep, tot_sol + sol, tot_uns + uns

            def _fmt(n: int) -> str: return str(n).zfill(2) if n else "—"

            widgets["rep"].configure(text=_fmt(rep), text_color="#38bdf8" if rep > 0 else "#4b5563")
            widgets["sol"].configure(text=_fmt(sol), text_color="#22c55e" if sol > 0 else "#4b5563")
            widgets["uns"].configure(text=_fmt(uns), text_color="#f87171" if uns > 0 else "#4b5563")
            widgets["row"].configure(fg_color="#052e16" if rep > 0 else widgets["row"].cget("fg_color"))
        
        self._tot_rep.configure(text=str(tot_rep) if tot_rep else "—")
        self._tot_sol.configure(text=str(tot_sol) if tot_sol else "—")
        self._tot_uns.configure(text=str(tot_uns) if tot_uns else "—")

    def _update_cat(self, cat_num: str, data: Dict[str, Any]) -> None:
        if cat_num not in self.cat_widgets: return
        w = self.cat_widgets[cat_num]
        count = data.get("count", 0)
        if count > 0:
            w["dot"].configure(text_color="#22c55e")
            w["count"].configure(text=f"{count:02d} cases", text_color="#22c55e")
            w["row"].configure(fg_color="#052e16")
        else:
            w["dot"].configure(text_color="#4b5563")
            w["count"].configure(text="NIL", text_color="#4b5563")
            w["row"].configure(fg_color="transparent")

    def _show_detail(self, cat_num: str) -> None:
        data = self.last_results.get(cat_num, {})
        incidents = data.get("incidents", [])
        if not incidents:
            messagebox.showinfo(f"Category {cat_num}", "No incidents (NIL)")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Category {cat_num} — {len(incidents)} incidents")
        win.geometry("650x450")
        txt = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=12))
        txt.pack(fill="both", expand=True, padx=15, pady=15)
        txt.insert("1.0", "\n\n".join(f"--- Incident {i+1} ---\n{inc}" for i, inc in enumerate(incidents)))
        txt.configure(state="disabled")

    # ═════════════════════════════════════════════════════════════════════════
    # ACTIONS & EVENT HANDLERS
    # ═════════════════════════════════════════════════════════════════════════

    def select_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.current_pdf = path
            self.file_label.configure(text=f"📄 {os.path.basename(path)}", text_color="white")
            self.status_label.configure(text=f"✅ Ready — {os.path.basename(path)}")

    def start_processing(self) -> None:
        if not self.current_pdf:
            messagebox.showwarning("No PDF", "Please select a PDF file first!")
            return

        self.process_btn.configure(state="disabled", text="⏳ Processing...")
        if hasattr(self, "paste_process_btn"): self.paste_process_btn.configure(state="disabled")
        self.progress.set(0)
        self.progress.start()
        self.preview_text.delete("1.0", "end")
        for i in range(1, 30): self._update_cat(str(i).zfill(2), {"count": 0})
        for w in self.report_row.winfo_children(): w.destroy()

        def progress_cb(cat_num: str, data: Dict[str, Any]) -> None:
            self.after(0, lambda: self._on_category_done(cat_num, data))

        def worker() -> None:
            try:
                mode = self.pipeline_mode_var.get()
                sinhala_first = mode.startswith("2")
                if self.kaggle_switch.get() == 1:
                    result = process_pdf_kaggle_cloud_hybrid(self.current_pdf, progress_callback=progress_cb)
                else:
                    result = process_pdf_hyper_hybrid(self.current_pdf, progress_callback=progress_cb, fast_complete=True, sinhala_first=sinhala_first)

                if result and isinstance(result, dict):
                    self.after(0, lambda r=result: self._on_complete(r))
                else:
                    self.after(0, lambda: self._on_error("Invalid result from processing pipeline"))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def start_kaggle_fast(self) -> None:
        """Kaggle-Only Fast processing — skips Cloud AI consensus for 2-3x speed."""
        if not self.current_pdf:
            messagebox.showwarning("No PDF", "Please select a PDF file first!")
            return

        self.process_btn.configure(state="disabled")
        self.kaggle_fast_btn.configure(state="disabled", text="⏳ Kaggle Processing...")
        if hasattr(self, "paste_process_btn"): self.paste_process_btn.configure(state="disabled")
        self.progress.set(0)
        self.progress.start()
        self.preview_text.delete("1.0", "end")
        for i in range(1, 30): self._update_cat(str(i).zfill(2), {"count": 0})
        for w in self.report_row.winfo_children(): w.destroy()

        def progress_cb(cat_num: str, data: Dict[str, Any]) -> None:
            self.after(0, lambda: self._on_category_done(cat_num, data))

        def worker() -> None:
            try:
                result = process_pdf_kaggle_only(self.current_pdf, progress_callback=progress_cb)
                if result and isinstance(result, dict):
                    self.after(0, lambda r=result: self._on_complete(r))
                else:
                    self.after(0, lambda: self._on_error("Invalid result from Kaggle pipeline"))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def start_processing_paste(self) -> None:
        raw = self.paste_input.get("1.0", "end-1c").strip()
        if len(raw) < 30:
            messagebox.showwarning("Paste text", "Please paste at least a few lines of the report (Sinhala).")
            return

        self.process_btn.configure(state="disabled")
        self.paste_process_btn.configure(state="disabled", text="⏳ Processing…")
        self.progress.set(0)
        self.progress.start()
        self.preview_text.delete("1.0", "end")
        for i in range(1, 30): self._update_cat(str(i).zfill(2), {"count": 0})
        for w in self.report_row.winfo_children(): w.destroy()

        def progress_cb(cat_num: str, data: Dict[str, Any]) -> None:
            self.after(0, lambda: self._on_category_done(cat_num, data))

        def worker() -> None:
            try:
                result = process_text_report(raw, progress_callback=progress_cb)
                self.after(0, lambda r=result: self._on_complete(r))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def update_ollama_status(self) -> None:
        self.ollama_status.configure(text="🤖 Local Master Engine Ready", text_color="#22c55e")

    def _first_existing_report_path(self, pdf_path: str) -> Optional[str]:
        if not pdf_path: return None
        pdf_path = os.path.normpath(os.path.abspath(pdf_path))
        if os.path.isfile(pdf_path): return pdf_path
        html_path = os.path.splitext(pdf_path)[0] + ".html"
        html_path = os.path.normpath(os.path.abspath(html_path))
        return html_path if os.path.isfile(html_path) else None

    def _open_report_path(self, pdf_path: str) -> None:
        import subprocess, platform
        p = self._first_existing_report_path(pdf_path)
        if not p:
            messagebox.showwarning("Report file not found", f"No PDF or HTML found for:\n{pdf_path}")
            return
        try:
            if platform.system() == "Windows": os.startfile(p)
            elif platform.system() == "Darwin": subprocess.run(["open", p], check=True)
            else: subprocess.run(["xdg-open", p], check=True)
        except Exception as e:
            messagebox.showerror("Open Error", f"Could not open file:\n{e}")

    def _on_category_done(self, cat_num: str, data: Dict[str, Any]) -> None:
        if cat_num == "OCR_UPDATE":
            self.status_label.configure(text=f"🌐 Kaggle + Cloud AI: {data.get('msg', 'Scanning...')}")
            curr = self.progress.get()
            self.progress.set(min(0.9, curr + 0.05))
            return

        self._update_cat(cat_num, data)
        self.last_results[cat_num] = data
        count = data.get("count", 0)
        if count > 0:
            self.preview_text.insert("end", f"\n[CAT {cat_num}] — {count} incidents\n")
            for inc in data.get("incidents", []): self.preview_text.insert("end", f"  {inc}\n")
            self.preview_text.insert("end", "─" * 60 + "\n")
            self.preview_text.see("end")
            if self.tabs.get() != "📊 Dashboard": self.tabs.set("📊 Dashboard")

        processed = sum(1 for cn in self.cat_widgets if self.last_results.get(cn, {}).get("count", -1) >= 0)
        self.status_label.configure(text=f"⚡ Processing... ({processed}/29 categories)")

    def _on_complete(self, result: Dict[str, Any]) -> None:
        self.progress.stop()
        self.progress.set(1.0)
        self.process_btn.configure(state="normal", text="⚡  Process Now")
        self.kaggle_fast_btn.configure(state="normal", text="🚀  Kaggle Fast")
        if hasattr(self, "paste_process_btn"): self.paste_process_btn.configure(state="normal", text="⚡ Process pasted text")

        if not result.get("success"):
            self._on_error(result.get("error", "Unknown error"))
            return

        self.status_label.configure(text="✅ Complete! — සිංහලෙන් සාමාන්‍ය/ආරක්ෂක වෙන් කර පරිවර්තනය කර institutional PDF දෙක ජනනය විය.")

        cat_results = result.get("category_results", {})
        for cn, data in cat_results.items():
            if cn in ["table_counts", "date_range"]: continue
            self._update_cat(cn, data)
            self.last_results[cn] = data

        summary_table = result.get("summary_table", {})
        date_range = cat_results.get("date_range", "")
        if summary_table: self._update_summary_table(summary_table, date_range)

        self.after(500, self.refresh_recent_reports)
        translation = result.get("full_translation", "")
        if translation:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", translation)

        self.generated_pdfs = result.get("generated_pdfs", [])
        self.generated_words = result.get("generated_words", [])
        all_generated = self.generated_pdfs + self.generated_words

        general_files = [p for p in all_generated if "General" in os.path.basename(p)]
        security_files = [p for p in all_generated if "Security" in os.path.basename(p)]

        col = 0
        for f_path in general_files:
            ext = os.path.splitext(f_path)[1].lower()
            icon, label, color = ("📋", "View General PDF", "#059669") if ext == ".pdf" else ("📝", "Edit General Word", "#1e40af") if ext in [".docx", ".dotx"] else ("🌐", "View General HTML", "#334155")
            ctk.CTkButton(self.report_row, text=f"{icon} {label}", height=45, font=ctk.CTkFont(size=13, weight="bold"), fg_color=color, hover_color="#334155", command=lambda p=f_path: self._open_report_path(p)).grid(row=0, column=col, padx=4, pady=8, sticky="ew")
            col += 1

        for f_path in security_files:
            ext = os.path.splitext(f_path)[1].lower()
            icon, label, color = ("🔒", "View Security PDF", "#4f46e5") if ext == ".pdf" else ("📝", "Edit Security Word", "#1e40af") if ext in [".docx", ".dotx"] else ("🌐", "View Security HTML", "#334155")
            ctk.CTkButton(self.report_row, text=f"{icon} {label}", height=45, font=ctk.CTkFont(size=13, weight="bold"), fg_color=color, hover_color="#334155", command=lambda p=f_path: self._open_report_path(p)).grid(row=0, column=col, padx=4, pady=8, sticky="ew")
            col += 1

    def _on_error(self, msg: str) -> None:
        try:
            self.progress.stop()
            self.progress.set(0)
            self.process_btn.configure(state="normal", text="⚡  Process Now")
            self.kaggle_fast_btn.configure(state="normal", text="🚀  Kaggle Fast")
            if hasattr(self, "paste_process_btn"): self.paste_process_btn.configure(state="normal", text="⚡ Process pasted text")
            self.status_label.configure(text=f"❌ {str(msg)[:80]}")
            messagebox.showerror("Error", str(msg)[:500] if msg else "Processing failed")
        except Exception as e:
            print(f"Error in error handler: {e}")

    def copy_result(self) -> None:
        text = self.preview_text.get("1.0", "end-1c").strip()
        if text:
            pyperclip.copy(text)
            self.status_label.configure(text="📋 Copied!")
            self.after(2000, lambda: self.status_label.configure(text="✅ Complete!"))
        else:
            messagebox.showinfo("Empty", "No text to copy yet.")

    def refresh_recent_reports(self) -> None:
        for widget in self.recent_scroll.winfo_children(): widget.destroy()
        try:
            recent_files = get_recent_files(limit=10)
            if not recent_files:
                ctk.CTkLabel(self.recent_scroll, text="No history yet", font=ctk.CTkFont(size=10), text_color="#475569").pack(pady=10)
                return
            for finfo in recent_files:
                fname, fpath, ftype = finfo["filename"], finfo["filepath"], finfo["file_type"]
                display_name = (fname[:22] + "...") if len(fname) > 25 else fname
                icon = "📄" if ftype == "PDF" else ("📝" if ftype == "Word" else "🌐")
                f_row = ctk.CTkFrame(self.recent_scroll, fg_color="#0f172a", height=32, corner_radius=4)
                f_row.pack(fill="x", pady=1, padx=2)
                lbl = ctk.CTkLabel(f_row, text=f"{icon} {display_name}", font=ctk.CTkFont(size=10), text_color="#cbd5e1", anchor="w")
                lbl.pack(side="left", padx=5, fill="x", expand=True)
                for w in (f_row, lbl): w.bind("<Button-1>", lambda e, p=fpath: self._open_report_path(p))
        except Exception as e:
            print(f"  [UI] Error refreshing history: {e}")

    # ═════════════════════════════════════════════════════════════════════════
    # API HEALTH & KEY MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════════

    def refresh_api_status(self) -> None:
        self.refresh_api_btn.configure(state="disabled", text="⌛ Checking...")
        self.api_status_box.configure(state="normal")
        self.api_status_box.delete("0.0", "end")
        self.api_status_box.insert("0.0", "🔄 Testing all keys...")
        self.api_status_box.configure(state="disabled")
        threading.Thread(target=self._run_api_check, daemon=True).start()

    def _run_api_check(self) -> None:
        from machine_translator import MachineTranslator
        try:
            health = MachineTranslator.get_api_health()
            lines = ["--- Gemini ---"] + [f"{k}: {v}" for k, v in sorted(health["Gemini"].items())] + ["\n--- GitHub ---"] + [f"{k}: {v}" for k, v in sorted(health["GitHub"].items())]
            self.after(0, lambda: self._update_api_ui("\n".join(lines)))
        except Exception:
            self.after(0, lambda: self._update_api_ui("❌ Check Failed"))

    def _update_api_ui(self, text: str) -> None:
        self.api_status_box.configure(state="normal")
        self.api_status_box.delete("0.0", "end")
        self.api_status_box.insert("0.0", text)
        self.api_status_box.configure(state="disabled")
        self.refresh_api_btn.configure(state="normal", text="🔄 Refresh API Status")

    def _refresh_gemini_key_ui(self) -> None:
        ok, desc = get_gemini_key_display()
        self.gemini_status_label.configure(text=("✅ " if ok else "⚪ ") + desc)

    def _save_gemini_key_from_ui(self) -> None:
        raw = self.gemini_entry.get().strip()
        ok, msg = save_gemini_api_key(raw)
        self.gemini_entry.delete(0, "end")
        if ok:
            messagebox.showinfo("Gemini key", msg)
            self._refresh_gemini_key_ui()
            self.after(500, self.refresh_api_status)
        else:
            messagebox.showerror("Gemini key", msg)

    def _delete_gemini_key_from_ui(self) -> None:
        if not messagebox.askyesno("Remove Gemini keys", "Remove all Gemini_* keys from gemini_keys.json and GEMINI_API_KEY from .env?"):
            return
        ok, msg = delete_gemini_api_keys()
        if ok:
            messagebox.showinfo("Gemini key", msg)
            self._refresh_gemini_key_ui()
            self.after(500, self.refresh_api_status)
        else:
            messagebox.showerror("Gemini key", msg)

    # ═════════════════════════════════════════════════════════════════════════
    # SETTINGS TOGGLES
    # ═════════════════════════════════════════════════════════════════════════

    def toggle_turbo_mode(self) -> None:
        mode = "race" if self.turbo_switch.get() else "sequential"
        try:
            get_engine().set_dispatch_mode(mode)
            print(f"[UI] {'Turbo (Parallel Race) Enabled' if mode == 'race' else 'Standard (Sequential) Enabled'}")
        except Exception as e:
            print(f"  [UI] Error toggling turbo: {e}")

    def toggle_kaggle_mode(self) -> None:
        prefer_kaggle = bool(self.kaggle_switch.get())
        try:
            get_engine().set_ollama_preference(prefer_kaggle)
            self.status_label.configure(text=f"[OK] {'Kaggle (Remote) AI Enabled' if prefer_kaggle else 'Local Master AI Enabled'}")
        except Exception as e:
            print(f"  [UI] Error toggling kaggle: {e}")
            messagebox.showerror("Toggle Error", f"Could not switch engine: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = PoliceDesktopApp()
    app.mainloop()