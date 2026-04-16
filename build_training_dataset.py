"""
build_training_dataset.py
=========================
Sinhala-English PDF pair → SQLite DB + JSONL training dataset builder
Sri Lanka Police AI — Gold-standard data preparation tool

This script scans for matching Sinhala and English police report PDFs,
extracts text using our robust GPU OCR (local_ocr_tool), 
saves them to a SQLite database to prevent duplicates,
and exports them into a JSONL format ready for LLM fine-tuning.

Usage:
    python build_training_dataset.py
"""

import json
import logging
import os
import re
import sqlite3
import sys
from datetime import datetime

# --- Project Imports ---
try:
    from config_loader import get_config
    from local_ocr_tool import extract_text_from_pdf
except ImportError:
    # Fallback/Error if modules not found in path
    print("Error: Missing local project modules (local_ocr_tool, config_loader).")
    sys.exit(1)

# ==============================================================================
# >  CONFIGURATION
# ==============================================================================
# Attempt to load from config.json, otherwise use defaults
config = get_config()
_data_cfg = config.get("training_dataset", {})

SINHALA_PDF_DIR = _data_cfg.get("sinhala_dir", r"D:\PROJECTS\ha\english\New folder")
ENGLISH_PDF_DIR = _data_cfg.get("english_dir", r"D:\PROJECTS\ha\english\New folder\New folder")
OUTPUT_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH         = os.path.join(OUTPUT_DIR, "training_dataset.db")
JSONL_PATH      = os.path.join(OUTPUT_DIR, "dataset", "training_data.jsonl")
MAIN_DB_PATH    = os.path.join(OUTPUT_DIR, "police_reports.db")

SYSTEM_PROMPT = (
    "You are an expert Sri Lanka Police institutional report translator. "
    "Translate Sinhala police daily reports into formal institutional English, "
    "preserving all station names, dates, incident details, and legal terminology accurately. "
    "Use official Sri Lanka Police terminology. Do not omit any information."
)
# ==============================================================================

logging.basicConfig(level=logging.INFO, format="  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# Reconfigure stdout for Unicode support on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

# -----------------------------------------------------------------------------
# DATABASE — matching db_manager style
# -----------------------------------------------------------------------------

def get_db(path: str = DB_PATH) -> sqlite3.Connection:
    """Open (or create) the SQLite DB and ensure schema exists."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL") # matching project standard
    conn.execute("PRAGMA foreign_keys=ON")
    _create_schema(conn)
    return conn

def _create_schema(conn: sqlite3.Connection):
    conn.executescript("""
        -- Raw PDF text pairs
        CREATE TABLE IF NOT EXISTS pdf_pairs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date     TEXT NOT NULL,          -- YYYY-MM-DD
            report_type     TEXT NOT NULL,          -- General / Security
            sinhala_path    TEXT,
            english_path    TEXT,
            sinhala_text    TEXT,
            english_text    TEXT,
            char_count_sin  INTEGER DEFAULT 0,
            char_count_eng  INTEGER DEFAULT 0,
            status          TEXT DEFAULT 'PAIRED',  -- PAIRED / MISSING_ENG / MISSING_SIN / SKIPPED
            added_at        TEXT DEFAULT (datetime('now')),
            UNIQUE(report_date, report_type)        -- Prevent duplicates
        )
-- Formatted training examples
        CREATE TABLE IF NOT EXISTS training_examples (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pair_id         INTEGER REFERENCES pdf_pairs(id),
            report_date     TEXT NOT NULL,
            report_type     TEXT NOT NULL,
            system_prompt   TEXT NOT NULL,
            user_prompt     TEXT NOT NULL,
            assistant_reply TEXT NOT NULL,
            exported        INTEGER DEFAULT 0,      -- 1 = already in JSONL
            created_at      TEXT DEFAULT (datetime('now'))
        )
-- Export history log
        CREATE TABLE IF NOT EXISTS export_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            exported_at     TEXT DEFAULT (datetime('now')),
            example_count   INTEGER,
            output_path     TEXT
        )
CREATE INDEX IF NOT EXISTS idx_pairs_date ON pdf_pairs(report_date)
CREATE INDEX IF NOT EXISTS idx_examples_exported ON training_examples(exported)
""")
    conn.commit()

# -----------------------------------------------------------------------------
# File Parsing Helpers
# -----------------------------------------------------------------------------

def parse_date(filename: str):
    name = os.path.basename(filename)
    # 2026.03.14 (Common Sinhala format)
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # 14 March 2026 (Common English format)
    months = "|".join(MONTH_MAP)
    m = re.search(rf"(\d{{1,2}})\s+({months})\s+(\d{{4}})", name, re.IGNORECASE)
    if m:
        day = m.group(1).zfill(2)
        month = MONTH_MAP[m.group(2).lower()]
        year = m.group(3)
        return f"{year}-{month}-{day}"
    # 2026-03-14 (Generic)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None

def detect_type(filename: str) -> str:
    low = filename.lower()
    # Security keywords
    if any(w in low for w in ("security", "ආරක්ෂක", "ආරක්‍ෂක")):
        return "Security"
    # General keywords (including "Incident Report" in Sinhala)
    if any(w in low for w in ("general", "සාමාන්‍ය", "සිදුවීම්", "සිදුවිම්", "වාර්තාව")):
        return "General"
    return "Unknown"

# -----------------------------------------------------------------------------
# Processing Engine
# -----------------------------------------------------------------------------

def scan_dir(directory: str) -> dict:
    result = {}
    if not os.path.isdir(directory):
        log.error(f"Directory not found: {directory}")
        return result
    for fname in os.listdir(directory):
        if not fname.lower().endswith(".pdf"):
            continue
        date  = parse_date(fname)
        rtype = detect_type(fname)
        if date:
            key = f"{date}_{rtype}"
            result.setdefault(key, []).append(os.path.join(directory, fname))
    return result

def build_pairs() -> list:
    sin_map  = scan_dir(SINHALA_PDF_DIR)
    eng_map  = scan_dir(ENGLISH_PDF_DIR)
    all_keys = sorted(set(sin_map) | set(eng_map))
    pairs    = []
    for key in all_keys:
        date, rtype = key.rsplit("_", 1)
        s = sin_map.get(key, [])
        e = eng_map.get(key, [])
        if s and e:
            pairs.append({"date": date, "type": rtype, "sinhala": s[0], "english": e[0], "status": "PAIRED"})
        elif s:
            pairs.append({"date": date, "type": rtype, "sinhala": s[0], "english": None, "status": "MISSING_ENG"})
        else:
            pairs.append({"date": date, "type": rtype, "sinhala": None, "english": e[0], "status": "MISSING_SIN"})
    return pairs

def upsert_pair(conn: sqlite3.Connection, p: dict):
    """Insert or update a pdf_pair. Returns the row id."""
    conn.execute("""
        INSERT INTO pdf_pairs
            (report_date, report_type, sinhala_path, english_path,
             sinhala_text, english_text, char_count_sin, char_count_eng, status)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(report_date, report_type) DO UPDATE SET
            sinhala_path   = excluded.sinhala_path,
            english_path   = excluded.english_path,
            sinhala_text   = CASE WHEN excluded.sinhala_text != '' THEN excluded.sinhala_text ELSE sinhala_text END,
            english_text   = CASE WHEN excluded.english_text != '' THEN excluded.english_text ELSE english_text END,
            char_count_sin = CASE WHEN excluded.char_count_sin > 0 THEN excluded.char_count_sin ELSE char_count_sin END,
            char_count_eng = CASE WHEN excluded.char_count_eng > 0 THEN excluded.char_count_eng ELSE char_count_eng END,
            status         = excluded.status,
            added_at       = datetime('now')
    """, (
        p["date"], p["type"],
        p.get("sinhala"), p.get("english"),
        p.get("sin_text", ""), p.get("eng_text", ""),
        len(p.get("sin_text", "")), len(p.get("eng_text", "")),
        p["status"],
    ))
    conn.commit()
    row = conn.execute("SELECT id FROM pdf_pairs WHERE report_date=? AND report_type=?", (p["date"], p["type"])).fetchone()
    return row["id"] if row else None

def upsert_example(conn: sqlite3.Connection, pair_id: int, p: dict):
    """Creates a training example if text is valid."""
    user_prompt = (
        f"Translate the following Sri Lanka Police {p['type']} Report "
        f"dated {p['date']} from Sinhala to institutional English. "
        f"Preserve all incident details, station names, case numbers, and official terminology exactly.\n\n"
        f"--- SINHALA REPORT ---\n{p['sin_text']}\n--- END ---"
    )
    conn.execute("""
        INSERT OR IGNORE INTO training_examples
            (pair_id, report_date, report_type, system_prompt, user_prompt, assistant_reply)
        VALUES (?,?,?,?,?,?)
    """, (pair_id, p["date"], p["type"], SYSTEM_PROMPT, user_prompt, p["eng_text"]))
    conn.commit()

# -----------------------------------------------------------------------------
# Export / Reporting
# -----------------------------------------------------------------------------

def export_jsonl(conn: sqlite3.Connection, output_path: str) -> int:
    """Exports all valid examples to JSONL."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = conn.execute("""
        SELECT system_prompt, user_prompt, assistant_reply 
        FROM training_examples 
        WHERE length(user_prompt) > 50 AND length(assistant_reply) > 50
    """).fetchall()

    written = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "messages": [
                    {"role": "system",    "content": row["system_prompt"]},
                    {"role": "user",      "content": row["user_prompt"]},
                    {"role": "assistant", "content": row["assistant_reply"]},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    if written > 0:
        conn.execute("INSERT INTO export_log (example_count, output_path) VALUES (?,?)", (written, output_path))
        conn.commit()
    return written

def recover_from_main_db(date: str, rtype: str) -> str:
    """
    Attempts to reconstruct an English report by concatenating translations
    found in the main police_reports.db for the given date.
    """
    if not os.path.exists(MAIN_DB_PATH):
        return ""

    table = "security_translations" if rtype == "Security" else "general_translations"

    # Try different date formats (YYYY-MM-DD vs MM/DD or others)
    # Most likely in the DB it is stored as matched in the UI, often short formats.
    parts = date.split("-")
    if len(parts) < 3: return ""
    m, d = parts[1], parts[2]
    short_date = f"{int(m)}/{int(d)}" # e.g. 11/13

    try:
        conn = sqlite3.connect(MAIN_DB_PATH)
        conn.row_factory = sqlite3.Row

        # Querying by both exact and short date just in case
        rows = conn.execute(
            f"SELECT translation_english FROM {table} WHERE incident_date = ? OR incident_date = ?",
            (date, short_date)
        ).fetchall()

        conn.close()

        if rows:
            # Join all translations for that day
            return "\n\n".join(r["translation_english"] for r in rows if r["translation_english"])
    except Exception as e:
        log.warning(f"Main DB lookup failed: {e}")

    return ""

def write_report(conn: sqlite3.Connection):
    stats = {
        "total": conn.execute("SELECT COUNT(*) FROM pdf_pairs").fetchone()[0],
        "paired": conn.execute("SELECT COUNT(*) FROM pdf_pairs WHERE status='PAIRED'").fetchone()[0],
        "examples": conn.execute("SELECT COUNT(*) FROM training_examples").fetchone()[0],
    }
    report = f"""
==============================================================
POLICE AI — DATASET GENERATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================================================

DB Location: {DB_PATH}
Total Pairs Identified: {stats['total']}
Success (Paired):       {stats['paired']}
Valid Training Examples: {stats['examples']}

--------------------------------------------------------------
Next Steps:
1. Review 'training_dataset.db' for data quality.
2. Fine-tune model using 'dataset/training_data.jsonl'.
==============================================================
"""
    print(report)
    with open("dataset_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------

def main():
    print(f"\n🚀 POLICE AI — TRAINING DATASET BUILDER (SQLite Edition)\n{'='*60}")

    conn = get_db()
    log.info(f"Database: {DB_PATH}")

    log.info("Scanning directories for PDF pairs...")
    pairs = build_pairs()
    log.info(f"Found {len(pairs)} records total.")

    for i, p in enumerate(pairs, 1):
        tag = f"[{i:02d}/{len(pairs):02d}] {p['date']} ({p['type']})"

        # Check if already processed and has text
        existing = conn.execute("SELECT sinhala_text, english_text FROM pdf_pairs WHERE report_date=? AND report_type=?",
                                (p['date'], p['type'])).fetchone()

        if existing and existing['sinhala_text'] and existing['english_text']:
            print(f"  {tag}  ⏭️  Already in DB (Skipping OCR)")
            continue

        if p["status"] != "PAIRED":
            # Attempt recovery if English is missing
            if p["status"] == "MISSING_ENG":
                print(f"  {tag}  💊 Attempting Database Recovery...", end=" ", flush=True)
                recovered_text = recover_from_main_db(p["date"], p["type"])
                if recovered_text:
                    p["eng_text"] = recovered_text
                    p["sin_text"] = "\n".join(extract_text_from_pdf(p["sinhala"])).strip()
                    p["status"] = "RECOVERED_FROM_DB"
                    pair_id = upsert_pair(conn, p)
                    upsert_example(conn, pair_id, p)
                    print(f"✅ Success! ({len(recovered_text)}c recovered)")
                    continue
                else:
                    print("❌ No data found in DB.")
            else:
                print(f"  {tag}  ⚠️  {p['status']}")

            upsert_pair(conn, p)
            continue

        print(f"  {tag}  🔍 Running OCR...", end=" ", flush=True)
        try:
            p["sin_text"] = "\n".join(extract_text_from_pdf(p["sinhala"])).strip()
            p["eng_text"] = "\n".join(extract_text_from_pdf(p["english"])).strip()

            if len(p["sin_text"]) < 50 or len(p["eng_text"]) < 50:
                print("❌ Insufficient text extracted.")
                p["status"] = "EMPTY_TEXT"
                upsert_pair(conn, p)
                continue

            pair_id = upsert_pair(conn, p)
            upsert_example(conn, pair_id, p)
            print(f"✅ Saved! (SIN: {len(p['sin_text'])}c, ENG: {len(p['eng_text'])}c)")

        except Exception as e:
            print(f"❌ Error: {e}")
            p["status"] = "OCR_ERROR"
            upsert_pair(conn, p)

    print(f"\n{'='*60}")
    written = export_jsonl(conn, JSONL_PATH)
    log.info(f"Exported {written} gold examples to {JSONL_PATH}")

    write_report(conn)
    conn.close()
    print("Done.\n")

if __name__ == "__main__":
    main()
