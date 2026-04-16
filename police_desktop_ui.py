import os

from dotenv import load_dotenv

load_dotenv()
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip
from PIL import Image, ImageTk

from ai_engine_manager import get_engine
from analytics_engine import AnalyticsEngine
from api_keys import delete_gemini_api_keys, get_gemini_key_display, save_gemini_api_key
from db_manager import get_recent_files
from desktop_pipeline import (
    process_pdf_hyper_hybrid,
    process_pdf_kaggle_cloud_hybrid,
    process_text_report,
)
from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PoliceDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Police AI — Fast Report Generator")
        self.geometry("1200x800")

        # Layout: 2-column
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===== SIDEBAR =====
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Logo
        ctk.CTkLabel(self.sidebar, text="⚡ Police AI", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#38bdf8").grid(row=0, column=0, padx=20, pady=(25, 5))
        ctk.CTkLabel(self.sidebar, text="Fast Report v2.2 [STABLE]", font=ctk.CTkFont(size=11),
                     text_color="#64748b").grid(row=1, column=0, padx=20, pady=(0, 25))

        # Upload Button (BIG)
        self.upload_btn = ctk.CTkButton(self.sidebar, text="📁  Select PDF", height=50,
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        fg_color="#1e40af", hover_color="#1d4ed8",
                                        command=self.select_pdf)
        self.upload_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Process Button (BIG, GREEN)
        self.process_btn = ctk.CTkButton(self.sidebar, text="⚡  Process Now", height=55,
                                         font=ctk.CTkFont(size=18, weight="bold"),
                                         fg_color="#059669", hover_color="#10b981",
                                         command=self.start_processing)
        self.process_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Pipeline: 1 = Turbo first (fast), 2 = Sinhala General/Security split then translate
        ctk.CTkLabel(self.sidebar, text="Pipeline", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#cbd5e1").grid(row=4, column=0, padx=20, pady=(8, 2), sticky="w")
        # Default Turbo-first — fewer OCR/API failures; pick 2 in menu for Sinhala split-first
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
        self.pipeline_menu.grid(row=5, column=0, padx=20, pady=(0, 6), sticky="ew")

        # Progress
        self.progress = ctk.CTkProgressBar(self.sidebar, height=8)
        self.progress.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.sidebar, text="Ready — Select a PDF",
                                         font=ctk.CTkFont(size=11), text_color="#94a3b8",
                                         wraplength=180)
        self.status_label.grid(row=7, column=0, padx=20, pady=(0, 10))

        # Local Engine Status
        self.ollama_status = ctk.CTkLabel(self.sidebar, text="🤖 Local AI Engine Ready",
                                         font=ctk.CTkFont(size=10), text_color="#64748b",
                                         wraplength=180)
        self.ollama_status.grid(row=8, column=0, padx=20, pady=(5, 10))

        # Update Ollama status on startup
        self.after(1000, self.update_ollama_status)

        # --- RECENT REPORTS SECTION ---
        ctk.CTkLabel(self.sidebar, text="🕒 Recent Reports", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#38bdf8").grid(row=9, column=0, padx=20, pady=(15, 2), sticky="w")

        self.recent_container = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=6)
        self.recent_container.grid(row=10, column=0, padx=15, pady=5, sticky="nsew")
        self.recent_container.grid_columnconfigure(0, weight=1)

        self.recent_scroll = ctk.CTkScrollableFrame(self.recent_container, height=180, fg_color="transparent")
        self.recent_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # Initial population of recent reports
        self.after(1500, self.refresh_recent_reports)

        # API Status Section
        ctk.CTkLabel(self.sidebar, text="🌐 API Health", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#94a3b8").grid(row=11, column=0, padx=20, pady=(15, 2), sticky="w")

        self.api_status_box = ctk.CTkTextbox(self.sidebar, height=100, width=180, font=ctk.CTkFont(size=10),
                                              fg_color="#0f172a", text_color="#64748b", corner_radius=6)
        self.api_status_box.grid(row=12, column=0, padx=20, pady=5)
        self.api_status_box.insert("0.0", "Checking...")
        self.api_status_box.configure(state="disabled")

        self.refresh_api_btn = ctk.CTkButton(self.sidebar, text="🔄 Refresh API", height=24,
                                             font=ctk.CTkFont(size=10), fg_color="#334155",
                                             command=self.refresh_api_status)
        self.refresh_api_btn.grid(row=13, column=0, padx=20, pady=(0, 10), sticky="ew")

        # --- SPEED SETTINGS ---
        self.speed_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.speed_frame.grid(row=14, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.turbo_switch = ctk.CTkSwitch(self.speed_frame, text="⚡ Turbo Speed (Race)",
                                          font=ctk.CTkFont(size=11),
                                          progress_color="#10b981",
                                          command=self.toggle_turbo_mode)
        self.turbo_switch.pack(side="left")
        if os.environ.get("AI_DISPATCH_MODE") == "race":
            self.turbo_switch.select()

        # --- KAGGLE AI TOGGLE ---
        self.kaggle_switch = ctk.CTkSwitch(self.sidebar, text="🌐 Disconnect Local (Kaggle)",
                                           font=ctk.CTkFont(size=11),
                                           progress_color="#38bdf8",
                                           command=self.toggle_kaggle_mode)
        self.kaggle_switch.grid(row=15, column=0, padx=20, pady=(5, 5), sticky="w")

        # Load default from config
        try:
            from ai_engine_manager import get_engine
            if get_engine().prefer_kaggle_ollama:
                self.kaggle_switch.select()
        except Exception:
            pass

        # Spacer
        self.sidebar.grid_rowconfigure(15, weight=1)

        # Appearance toggle
        self.appearance = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light"],
                                            width=100, command=ctk.set_appearance_mode)
        self.appearance.grid(row=16, column=0, padx=20, pady=(0, 15))
        self.appearance.set("Dark")

        # Start initial API check in background
        self.after(2000, self.refresh_api_status)

        # ===== MAIN AREA =====
        self.main = ctk.CTkFrame(self, corner_radius=12)
        self.main.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        # Header bar
        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(self.header, text="No PDF selected",
                                       font=ctk.CTkFont(size=16, weight="bold"), text_color="#94a3b8")
        self.file_label.grid(row=0, column=0, sticky="w")

        self.copy_btn = ctk.CTkButton(self.header, text="📋 Copy", width=90, height=32,
                                      fg_color="#334155", hover_color="#475569",
                                      command=self.copy_result)
        self.copy_btn.grid(row=0, column=1, padx=5)

        # Tabview: Dashboard + Preview
        self.tabs = ctk.CTkTabview(self.main, height=500)
        self.tabs.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.tabs.add("📊 Dashboard")
        self.tabs.add("📝 Translation Preview")
        self.tabs.add("📈 Analytics")
        self.tabs.add("📋 Paste text")
        self.tabs.add("🔑 API Keys")

        # --- Dashboard Tab ---
        self.dash_frame = ctk.CTkScrollableFrame(self.tabs.tab("📊 Dashboard"))
        self.dash_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.cat_widgets = {}
        self._build_summary_table()   # ← prominent 29-row table at TOP
        self._build_dashboard()       # ← per-category cards below

        # --- Analytics Tab ---
        self._build_analytics_tab()

        # --- Preview Tab ---
        self.preview_text = ctk.CTkTextbox(self.tabs.tab("📝 Translation Preview"),
                                           font=ctk.CTkFont(family="Consolas", size=13))
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Paste text tab (copy-paste full Sinhala report, no PDF) ---
        paste_tab = self.tabs.tab("📋 Paste text")
        paste_wrap = ctk.CTkFrame(paste_tab, fg_color="transparent")
        paste_wrap.pack(fill="both", expand=True, padx=12, pady=10)
        ctk.CTkLabel(
            paste_wrap,
            text=(
                "වාර්තාවේ සම්පූර්ණ සිංහල පෙළ මෙතන paste කරන්න (Ctrl+V). "
                "PDF එකක් නැතිව වැඩ කරන්න මෙම මාර්ගය භාවිතා කරන්න.\n"
                "Paste the full Sinhala police report below, then click Process. Shortcut: Ctrl+Enter."
            ),
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8",
            wraplength=880,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))
        self.paste_input = ctk.CTkTextbox(
            paste_wrap,
            height=400,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.paste_input.pack(fill="both", expand=True, pady=4)
        self.paste_input.bind("<Control-Return>", lambda e: self.start_processing_paste())
        self.paste_process_btn = ctk.CTkButton(
            paste_wrap,
            text="⚡ Process pasted text",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=self.start_processing_paste,
        )
        self.paste_process_btn.pack(pady=(10, 4))

        # --- API Keys tab (Gemini) ---
        keys_tab = self.tabs.tab("🔑 API Keys")
        keys_wrap = ctk.CTkFrame(keys_tab, fg_color="transparent")
        keys_wrap.pack(fill="both", expand=True, padx=16, pady=12)
        ctk.CTkLabel(
            keys_wrap,
            text="Google Gemini (Generative Language API)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e2e8f0",
        ).pack(anchor="w", pady=(0, 6))
        self.gemini_status_label = ctk.CTkLabel(
            keys_wrap,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            wraplength=900,
            justify="left",
        )
        self.gemini_status_label.pack(anchor="w", pady=(0, 12))
        ctk.CTkLabel(keys_wrap, text="Paste new key (hidden):", font=ctk.CTkFont(size=12), text_color="#cbd5e1").pack(
            anchor="w"
        )
        self.gemini_entry = ctk.CTkEntry(
            keys_wrap,
            placeholder_text="AIza…",
            width=720,
            height=36,
            font=ctk.CTkFont(size=12),
            show="*",
        )
        self.gemini_entry.pack(anchor="w", pady=(6, 12))
        key_btn_row = ctk.CTkFrame(keys_wrap, fg_color="transparent")
        key_btn_row.pack(anchor="w", pady=4)
        ctk.CTkButton(
            key_btn_row,
            text="💾 Save Gemini key",
            width=180,
            height=36,
            fg_color="#059669",
            hover_color="#10b981",
            command=self._save_gemini_key_from_ui,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            key_btn_row,
            text="🗑 Remove saved keys",
            width=180,
            height=36,
            fg_color="#b91c1c",
            hover_color="#dc2626",
            command=self._delete_gemini_key_from_ui,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            key_btn_row,
            text="↻ Refresh status",
            width=140,
            height=36,
            fg_color="#334155",
            command=self._refresh_gemini_key_ui,
        ).pack(side="left")
        ctk.CTkLabel(
            keys_wrap,
            text=(
                "Saves to gemini_keys.json (Gemini_1) and GEMINI_API_KEY in .env. "
                "Remove clears all Gemini_* slots in that JSON and removes GEMINI_API_KEY from .env. "
                "Other keys in the JSON file are left unchanged."
            ),
            font=ctk.CTkFont(size=11),
            text_color="#64748b",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(16, 0))
        self._refresh_gemini_key_ui()

        # Report buttons row
        self.report_row = ctk.CTkFrame(self.main, fg_color="transparent")
        self.report_row.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.report_row.grid_columnconfigure((0, 1), weight=1)

        # State
        self.current_pdf = None
        self.generated_pdfs = []
        self.last_results = {}

        # Analytics Engine
        self.analytics_engine = AnalyticsEngine()
        self.chart_refs = {} # To prevent GC

    # =========================================================================
    # SUMMARY TABLE  (prominent 29-row table at top of Dashboard)
    # =========================================================================
    # English labels matching the 29-row official table on the last PDF page
    _TABLE_LABELS = [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
        "21", "22", "23", "24", "25", "26", "27", "28", "29",
    ]

    def _build_summary_table(self):
        """Build the 5-column summary table (No | Incident | Reported | Solved | Unsolved) at the top of the dashboard."""
        from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES

        # ── outer card ──
        card = ctk.CTkFrame(self.dash_frame, fg_color="#0f172a", corner_radius=10)
        card.pack(fill="x", padx=8, pady=(8, 2))

        # ── title row ──
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

        # ── column headers ──
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

        # ── data rows ──
        self._sum_row_widgets = {}   # cat_num -> {rep, sol, uns, row_frame}
        for idx, num in enumerate(self._TABLE_LABELS):
            # Find matching label
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

            rep_lbl = ctk.CTkLabel(row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
                                   text_color="#4b5563", anchor="center")
            rep_lbl.grid(row=0, column=2, padx=2, pady=2)

            sol_lbl = ctk.CTkLabel(row, text="—", width=72, font=ctk.CTkFont(size=11),
                                   text_color="#4b5563", anchor="center")
            sol_lbl.grid(row=0, column=3, padx=2, pady=2)

            uns_lbl = ctk.CTkLabel(row, text="—", width=72, font=ctk.CTkFont(size=11),
                                   text_color="#4b5563", anchor="center")
            uns_lbl.grid(row=0, column=4, padx=2, pady=2)

            self._sum_row_widgets[num] = {
                "rep": rep_lbl, "sol": sol_lbl, "uns": uns_lbl, "row": row
            }

        # ── totals row ──
        tot_row = ctk.CTkFrame(card, fg_color="#1e3a5f", corner_radius=0)
        tot_row.pack(fill="x", padx=8, pady=(0, 8))
        tot_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tot_row, text="TOTAL", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#93c5fd", anchor="w").grid(row=0, column=0, columnspan=2, padx=8, pady=3, sticky="w")
        self._tot_rep = ctk.CTkLabel(tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#38bdf8", anchor="center")
        self._tot_rep.grid(row=0, column=2, padx=2, pady=3)
        self._tot_sol = ctk.CTkLabel(tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#22c55e", anchor="center")
        self._tot_sol.grid(row=0, column=3, padx=2, pady=3)
        self._tot_uns = ctk.CTkLabel(tot_row, text="—", width=72, font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#f87171", anchor="center")
        self._tot_uns.grid(row=0, column=4, padx=2, pady=3)

        # ── separator ──
        ctk.CTkFrame(self.dash_frame, fg_color="#1e293b", height=2).pack(fill="x", padx=8, pady=(4, 8))

    def _update_summary_table(self, summary_table: dict, date_range: str = ""):
        """Populate the summary table cells from pipeline result."""
        if date_range:
            self.table_date_label.configure(text=date_range)
        tot_rep = tot_sol = tot_uns = 0
        for num, widgets in self._sum_row_widgets.items():
            row_data = summary_table.get(num, {"reported": 0, "solved": 0, "unsolved": 0})
            rep = row_data.get("reported", 0)
            sol = row_data.get("solved", 0)
            uns = row_data.get("unsolved", 0)
            tot_rep += rep; tot_sol += sol; tot_uns += uns

            def _fmt(n):
                return str(n).zfill(2) if n else "—"

            widgets["rep"].configure(
                text=_fmt(rep),
                text_color="#38bdf8" if rep > 0 else "#4b5563",
            )
            widgets["sol"].configure(
                text=_fmt(sol),
                text_color="#22c55e" if sol > 0 else "#4b5563",
            )
            widgets["uns"].configure(
                text=_fmt(uns),
                text_color="#f87171" if uns > 0 else "#4b5563",
            )
            # Highlight rows with any activity
            widgets["row"].configure(
                fg_color="#052e16" if rep > 0 else widgets["row"].cget("fg_color")
            )
        self._tot_rep.configure(text=str(tot_rep) if tot_rep else "—")
        self._tot_sol.configure(text=str(tot_sol) if tot_sol else "—")
        self._tot_uns.configure(text=str(tot_uns) if tot_uns else "—")

    # =========================================================================
    # DASHBOARD (per-category cards)
    # =========================================================================
    def _build_dashboard(self):
        """Build compact 29-category dashboard cards."""
        for cat_name in OFFICIAL_CASE_TABLE_CATEGORIES:
            cat_num = cat_name.split(".")[0].strip()

            row = ctk.CTkFrame(self.dash_frame, height=36)
            row.pack(fill="x", padx=8, pady=1)

            dot = ctk.CTkLabel(row, text="●", text_color="#4b5563", font=ctk.CTkFont(size=14), width=20)
            dot.pack(side="left", padx=(10, 5))

            lbl = ctk.CTkLabel(row, text=cat_name, font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(side="left", fill="x", expand=True, padx=5)

            count_lbl = ctk.CTkLabel(row, text="—", text_color="#6b7280",
                                     font=ctk.CTkFont(size=11, weight="bold"), width=80)
            count_lbl.pack(side="right", padx=10)

            # Click to view details
            for w in (row, lbl, dot):
                w.bind("<Button-1>", lambda e, n=cat_num: self._show_detail(n))

            self.cat_widgets[cat_num] = {"row": row, "dot": dot, "count": count_lbl}

    def _update_cat(self, cat_num, data):
        """Update a single category card (thread-safe)."""
        if cat_num not in self.cat_widgets:
            return
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

    def _show_detail(self, cat_num):
        """Pop-up with incidents for a specific category."""
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

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def select_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.current_pdf = path
            self.file_label.configure(text=f"📄 {os.path.basename(path)}", text_color="white")
            self.status_label.configure(text=f"✅ Ready — {os.path.basename(path)}")

    def start_processing(self):
        if not self.current_pdf:
            messagebox.showwarning("No PDF", "Please select a PDF file first!")
            return

        # Disable button, start progress
        self.process_btn.configure(state="disabled", text="⏳ Processing...")
        if hasattr(self, "paste_process_btn"):
            self.paste_process_btn.configure(state="disabled")
        self.progress.set(0)
        self.progress.start()
        self.preview_text.delete("1.0", "end")
        # Reset dashboard
        for i in range(1, 29):
            self._update_cat(str(i).zfill(2), {"count": 0})

        # Clear report buttons
        for w in self.report_row.winfo_children():
            w.destroy()

        def progress_cb(cat_num, data):
            """Real-time category progress from pipeline."""
            self.after(0, lambda: self._on_category_done(cat_num, data))

        def worker():
            try:
                mode = self.pipeline_mode_var.get()
                sinhala_first = mode.startswith("2")

                if self.kaggle_switch.get() == 1:
                    print("  [UI] Switching to Kaggle + Cloud Hybrid Pipeline...")
                    result = process_pdf_kaggle_cloud_hybrid(
                        self.current_pdf,
                        progress_callback=progress_cb
                    )
                else:
                    result = process_pdf_hyper_hybrid(
                        self.current_pdf,
                        progress_callback=progress_cb,
                        fast_complete=True,
                        sinhala_first=sinhala_first,
                    )

                if result and isinstance(result, dict):
                    self.after(0, lambda r=result: self._on_complete(r))
                else:
                    self.after(0, lambda: self._on_error("Invalid result from processing pipeline"))
            except Exception as e:
                import traceback
                error_msg = f"{e!s}\n{traceback.format_exc()}"
                print(f"[ERROR] Worker thread error: {error_msg}")
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def start_processing_paste(self):
        """Process Sinhala report from clipboard / typed text (no PDF)."""
        raw = self.paste_input.get("1.0", "end-1c").strip()
        if len(raw) < 30:
            messagebox.showwarning(
                "Paste text",
                "Please paste at least a few lines of the report (Sinhala).\n"
                "සිංහල වාර්තාවේ පෙළ මෙතන ඇතුළත් කරන්න.",
            )
            return

        self.process_btn.configure(state="disabled")
        self.paste_process_btn.configure(state="disabled", text="⏳ Processing…")
        self.progress.set(0)
        self.progress.start()
        self.preview_text.delete("1.0", "end")
        for i in range(1, 30):
            self._update_cat(str(i).zfill(2), {"count": 0})
        for w in self.report_row.winfo_children():
            w.destroy()

        def progress_cb(cat_num, data):
            self.after(0, lambda: self._on_category_done(cat_num, data))

        def worker():
            try:
                result = process_text_report(raw, progress_callback=progress_cb)
                self.after(0, lambda r=result: self._on_complete(r))
            except Exception as e:
                import traceback

                print(f"❌ Paste worker error: {e}\n{traceback.format_exc()}")
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def update_ollama_status(self):
        """Standard Local Model Status."""
        self.ollama_status.configure(text="🤖 Local Master Engine Ready", text_color="#22c55e")

    def _first_existing_report_path(self, pdf_path: str):
        """Prefer PDF; if missing (e.g. wkhtmltopdf not installed), open sibling HTML."""
        if not pdf_path:
            return None
        pdf_path = os.path.normpath(os.path.abspath(pdf_path))
        if os.path.isfile(pdf_path):
            return pdf_path
        html_path = os.path.splitext(pdf_path)[0] + ".html"
        html_path = os.path.normpath(os.path.abspath(html_path))
        return html_path if os.path.isfile(html_path) else None

    def _open_report_path(self, pdf_path: str):
        p = self._first_existing_report_path(pdf_path)
        if p:
            os.startfile(p)
            return
        messagebox.showwarning(
            "Report file not found",
            f"No PDF or HTML found for:\n{pdf_path}\n\n"
            "Install wkhtmltopdf to build PDFs, or open the HTML in outputs/ if it exists.",
        )

    def _on_category_done(self, cat_num, data):
        """Called per-category as pipeline processes."""
        if cat_num == "OCR_UPDATE":
            msg = data.get("msg", "Scanning...")
            self.status_label.configure(text=f"🌐 Kaggle + Cloud AI: {msg}")
            # Ensure progress bar moves a bit or simulates activity
            curr = self.progress.get()
            self.progress.set(min(0.9, curr + 0.05))
            return

        self._update_cat(cat_num, data)
        self.last_results[cat_num] = data

        count = data.get("count", 0)
        if count > 0:
            self.preview_text.insert("end", f"\n[CAT {cat_num}] — {count} incidents\n")
            for inc in data.get("incidents", []):
                self.preview_text.insert("end", f"  {inc}\n")
            self.preview_text.insert("end", "─" * 60 + "\n")
            self.preview_text.see("end")

            # Auto switch to dashboard on first data
            if self.tabs.get() != "📊 Dashboard":
                self.tabs.set("📊 Dashboard")

        processed = sum(1 for cn in self.cat_widgets if self.last_results.get(cn, {}).get("count", -1) >= 0)
        self.status_label.configure(text=f"⚡ Processing... ({processed}/28 categories)")

    def _on_complete(self, result):
        """Called when pipeline finishes."""
        self.progress.stop()
        self.progress.set(1.0)
        self.process_btn.configure(state="normal", text="⚡  Process Now")
        if hasattr(self, "paste_process_btn"):
            self.paste_process_btn.configure(state="normal", text="⚡ Process pasted text")

        if not result.get("success"):
            self._on_error(result.get("error", "Unknown error"))
            return

        self.status_label.configure(
            text="✅ Complete! — සිංහලෙන් සාමාන්‍ය/ආරක්ෂක වෙන් කර පරිවර්තනය කර institutional PDF දෙක ජනනය විය. "
            "(එක දින වාර්තා PDF එකක දෙ කොටසම තිබේ නම් හොඳින්ම පිරෙයි.)"
        )

        # Update all categories
        cat_results = result.get("category_results", {})
        for cn, data in cat_results.items():
            if cn in ["table_counts", "date_range"]:
                continue
            self._update_cat(cn, data)
            self.last_results[cn] = data

        # ── Update the prominent summary table ──
        summary_table = result.get("summary_table", {})
        date_range = cat_results.get("date_range", "")
        if summary_table:
            self._update_summary_table(summary_table, date_range)
        else:
            # Fallback: derive from category counts alone
            derived = {
                cn: {"reported": (data.get("count", 0) if isinstance(data, dict) else 0), "solved": 0, "unsolved": 0}
                for cn, data in cat_results.items() if cn not in ["table_counts", "date_range"]
            }
            self._update_summary_table(derived, date_range)

        # Refresh history
        self.after(500, self.refresh_recent_reports)

        # Show translation in preview
        translation = result.get("full_translation", "")
        if translation:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", translation)

        # Add report buttons (pair General + Security when both paths exist)
        self.generated_pdfs = result.get("generated_pdfs", [])
        self.generated_words = result.get("generated_words", [])

        all_generated = self.generated_pdfs + self.generated_words

        # Filter by type for strategic button placement
        general_files = [p for p in all_generated if "General" in os.path.basename(p)]
        security_files = [p for p in all_generated if "Security" in os.path.basename(p)]

        col = 0
        for f_path in general_files:
            ext = os.path.splitext(f_path)[1].lower()
            if ext == ".pdf":
                icon, label, color = "📋", "View General PDF", "#059669"
            elif ext in [".docx", ".dotx"]:
                icon, label, color = "📝", "Edit General Word", "#1e40af"
            else:
                icon, label, color = "🌐", "View General HTML", "#334155"

            ctk.CTkButton(
                self.report_row, text=f"{icon} {label}",
                height=45, font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=color, hover_color="#334155",
                command=lambda p=f_path: self._open_report_path(p),
            ).grid(row=0, column=col, padx=4, pady=8, sticky="ew")
            col += 1

        for f_path in security_files:
            ext = os.path.splitext(f_path)[1].lower()
            if ext == ".pdf":
                icon, label, color = "🔒", "View Security PDF", "#4f46e5"
            elif ext in [".docx", ".dotx"]:
                icon, label, color = "📝", "Edit Security Word", "#1e40af"
            else:
                icon, label, color = "🌐", "View Security HTML", "#334155"

            ctk.CTkButton(
                self.report_row, text=f"{icon} {label}",
                height=45, font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=color, hover_color="#334155",
                command=lambda p=f_path: self._open_report_path(p),
            ).grid(row=0, column=col, padx=4, pady=8, sticky="ew")
            col += 1

    def _on_error(self, msg):
        try:
            self.progress.stop()
            self.progress.set(0)
            self.process_btn.configure(state="normal", text="⚡  Process Now")
            if hasattr(self, "paste_process_btn"):
                self.paste_process_btn.configure(state="normal", text="⚡ Process pasted text")
            error_display = str(msg)[:80] if msg else "Unknown error"
            self.status_label.configure(text=f"❌ {error_display}")
            messagebox.showerror("Error", str(msg)[:500] if msg else "Processing failed")
        except Exception as e:
            print(f"Error in error handler: {e}")

    def copy_result(self):
        text = self.preview_text.get("1.0", "end-1c").strip()
        if text:
            pyperclip.copy(text)
            self.status_label.configure(text="📋 Copied!")
            self.after(2000, lambda: self.status_label.configure(text="✅ Complete!"))
        else:
            messagebox.showinfo("Empty", "No text to copy yet.")

    def refresh_recent_reports(self):
        """Fetch and display the last 10 generated reports."""
        for widget in self.recent_scroll.winfo_children():
            widget.destroy()

        try:
            recent_files = get_recent_files(limit=10)
            if not recent_files:
                ctk.CTkLabel(self.recent_scroll, text="No history yet", font=ctk.CTkFont(size=10), text_color="#475569").pack(pady=10)
                return

            for finfo in recent_files:
                fname = finfo["filename"]
                fpath = finfo["filepath"]
                ftype = finfo["file_type"]
                finfo["category"] or "Report"

                # Truncate long filenames
                display_name = (fname[:22] + "...") if len(fname) > 25 else fname

                # Determine icon
                icon = "📄" if ftype == "PDF" else ("📝" if ftype == "Word" else "🌐")

                f_row = ctk.CTkFrame(self.recent_scroll, fg_color="#0f172a", height=32, corner_radius=4)
                f_row.pack(fill="x", pady=1, padx=2)

                lbl = ctk.CTkLabel(f_row, text=f"{icon} {display_name}", font=ctk.CTkFont(size=10), text_color="#cbd5e1", anchor="w")
                lbl.pack(side="left", padx=5, fill="x", expand=True)

                # Bind click to open
                for w in (f_row, lbl):
                    w.bind("<Button-1>", lambda e, p=fpath: self._open_report_path(p))

        except Exception as e:
            print(f"  [UI] Error refreshing history: {e}")

    # =========================================================================
    # API HEALTH MONITORING
    # =========================================================================
    def refresh_api_status(self):
        """Check all API keys in background thread."""
        self.refresh_api_btn.configure(state="disabled", text="⌛ Checking...")
        self.api_status_box.configure(state="normal")
        self.api_status_box.delete("0.0", "end")
        self.api_status_box.insert("0.0", "🔄 Testing all keys...")
        self.api_status_box.configure(state="disabled")

        threading.Thread(target=self._run_api_check, daemon=True).start()

    def _run_api_check(self):
        """The actual background work for API check."""
        from machine_translator import MachineTranslator
        try:
            health = MachineTranslator.get_api_health()

            # Formulate display text
            lines = []
            lines.append("--- Gemini ---")
            for k, v in sorted(health["Gemini"].items()):
                lines.append(f"{k}: {v}")

            lines.append("\n--- GitHub ---")
            for k, v in sorted(health["GitHub"].items()):
                lines.append(f"{k}: {v}")

            display_text = "\n".join(lines)

            # Update UI from thread
            self.after(0, lambda: self._update_api_ui(display_text))
        except Exception:
            self.after(0, lambda: self._update_api_ui("❌ Check Failed"))

    def _update_api_ui(self, text):
        """Update the text box and button state."""
        self.api_status_box.configure(state="normal")
        self.api_status_box.delete("0.0", "end")
        self.api_status_box.insert("0.0", text)
        self.api_status_box.configure(state="disabled")
        self.refresh_api_btn.configure(state="normal", text="🔄 Refresh API Status")

    def _refresh_gemini_key_ui(self):
        ok, desc = get_gemini_key_display()
        prefix = "✅ " if ok else "⚪ "
        self.gemini_status_label.configure(text=prefix + desc)

    def _save_gemini_key_from_ui(self):
        raw = self.gemini_entry.get().strip()
        ok, msg = save_gemini_api_key(raw)
        self.gemini_entry.delete(0, "end")
        if ok:
            messagebox.showinfo("Gemini key", msg)
            self._refresh_gemini_key_ui()
            self.after(500, self.refresh_api_status)
        else:
            messagebox.showerror("Gemini key", msg)

    def _delete_gemini_key_from_ui(self):
        if not messagebox.askyesno(
            "Remove Gemini keys",
            "Remove all Gemini_* keys from gemini_keys.json and GEMINI_API_KEY from .env?\n\n"
            "Other entries in gemini_keys.json (e.g. OpenAI) are kept.",
        ):
            return
        ok, msg = delete_gemini_api_keys()
        if ok:
            messagebox.showinfo("Gemini key", msg)
            self._refresh_gemini_key_ui()
            self.after(500, self.refresh_api_status)
        else:
            messagebox.showerror("Gemini key", msg)


    # =========================================================================
    # ANALYTICS DASHBOARD
    # =========================================================================
    def _build_analytics_tab(self):
        tab = self.tabs.tab("📈 Analytics")

        # Main scrollable area
        self.analytics_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.analytics_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Header / Stats Bar
        self.stats_bar = ctk.CTkFrame(self.analytics_scroll, fg_color="#1e293b", height=80, corner_radius=10)
        self.stats_bar.pack(fill="x", padx=10, pady=10)

        self.stat_labels = {}
        fields = [("total_reports", "Total Reports"), ("total_incidents", "Total Incidents"),
                  ("security_incidents", "Security Cases"), ("general_incidents", "General Cases")]

        for i, (key, label) in enumerate(fields):
            f = ctk.CTkFrame(self.stats_bar, fg_color="transparent")
            f.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack()
            self.stat_labels[key] = ctk.CTkLabel(f, text="0", font=ctk.CTkFont(size=22, weight="bold"), text_color="#38bdf8")
            self.stat_labels[key].pack()

        # Charts Container
        self.charts_frame = ctk.CTkFrame(self.analytics_scroll, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True)

        # Refresh Button
        ctk.CTkButton(self.analytics_scroll, text="🔄 Refresh Analytics", command=self._refresh_analytics,
                      fg_color="#334155", hover_color="#1e293b").pack(pady=10)

        # Initial Load
        self.after(2000, self._refresh_analytics)

    def _refresh_analytics(self):
        """Generates new charts and updates the UI."""
        def _job():
            try:
                # 1. Update stats
                stats = self.analytics_engine.get_summary_stats()
                self.after(0, lambda s=stats: self._update_stat_labels(s))

                # 2. Generate and load charts
                c1_path = self.analytics_engine.generate_crime_distribution_by_province()
                c2_path = self.analytics_engine.generate_incident_trend()

                self.after(0, lambda p1=c1_path, p2=c2_path: self._display_charts(p1, p2))
            except Exception as e:
                print(f"[Analytics UI] Error: {e}")

        threading.Thread(target=_job, daemon=True).start()

    def _update_stat_labels(self, stats):
        for k, v in stats.items():
            if k in self.stat_labels:
                self.stat_labels[k].configure(text=str(v))

    def _display_charts(self, p1, p2):
        # Clear old charts if any
        for w in self.charts_frame.winfo_children():
            w.destroy()

        # Display Province Chart
        if p1 and os.path.exists(p1):
            img1 = Image.open(p1)
            # Resize logic for dashboard fit
            img1 = img1.resize((500, 300), Image.LANCZOS)
            photo1 = ImageTk.PhotoImage(img1)
            self.chart_refs['c1'] = photo1

            c1_label = ctk.CTkLabel(self.charts_frame, image=photo1, text="")
            c1_label.grid(row=0, column=0, padx=10, pady=10)

        # Display Trend Chart
        if p2 and os.path.exists(p2):
            img2 = Image.open(p2)
            img2 = img2.resize((500, 300), Image.LANCZOS)
            photo2 = ImageTk.PhotoImage(img2)
            self.chart_refs['c2'] = photo2

            c2_label = ctk.CTkLabel(self.charts_frame, image=photo2, text="")
            c2_label.grid(row=0, column=1, padx=10, pady=10)

    def toggle_turbo_mode(self):
        """Toggle between Race (Parallel) and Sequential AI dispatch."""
        mode = "race" if self.turbo_switch.get() else "sequential"
        try:
            get_engine().set_dispatch_mode(mode)
            status = "Turbo (Parallel Race) Enabled" if mode == "race" else "Standard (Sequential) Enabled"
            print(f"[UI] {status}")
        except Exception as e:
            print(f"  [UI] Error toggling turbo: {e}")

    def toggle_kaggle_mode(self):
        """Toggle between Local and Remote (Kaggle) Ollama."""
        prefer_kaggle = bool(self.kaggle_switch.get())
        try:
            get_engine().set_ollama_preference(prefer_kaggle)
            status = "Kaggle (Remote) AI Enabled" if prefer_kaggle else "Local Master AI Enabled"
            self.status_label.configure(text=f"[OK] {status}")
            print(f"[UI] {status}")
        except Exception as e:
            print(f"  [UI] Error toggling kaggle: {e}")
            messagebox.showerror("Toggle Error", f"Could not switch engine: {e}")

if __name__ == "__main__":
    app = PoliceDesktopApp()
    app.mainloop()
