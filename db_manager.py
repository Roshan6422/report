import os
import sqlite3

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE_DIR, "police_reports.db")
SCHEMA_PATH = os.path.join(_BASE_DIR, "schema.sql")

def get_connection():
    """Returns a SQLite connection object with WAL mode for concurrent access safety."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    """Initializes the database using the schema.sql file."""
    if not os.path.exists(DB_PATH):
        print(f"  [DB] Creating database at {DB_PATH}...")

    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("  [DB] Database initialized successfully.")

def save_report(filename, report_date, report_type, raw_hash):
    """Saves report metadata and returns the report_id."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check if exists
    cursor.execute("SELECT id FROM reports WHERE raw_hash = ?", (raw_hash,))
    res = cursor.fetchone()
    if res:
        conn.close()
        return res[0]

    cursor.execute(
        "INSERT INTO reports (filename, report_date, report_type, raw_hash) VALUES (?, ?, ?, ?)",
        (filename, report_date, report_type, raw_hash)
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def save_section(report_id, title, content):
    """Saves a section and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sections (report_id, title, content_sinhala) VALUES (?, ?, ?)",
        (report_id, title, content)
    )
    sid = cursor.lastrowid
    conn.commit()
    conn.close()
    return sid

def save_incident(section_id, station, province, body, ref, confidence=1.0, consensus="OllamaOnly"):
    """Saves an incident to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO incidents (section_id, station, province, translation_english, reference_code, confidence_score, consensus_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (section_id, station, province, body, ref, confidence, consensus)
    )
    iid = cursor.lastrowid
    conn.commit()
    conn.close()
    return iid

def log_ai_call(incident_id, engine, prompt, response):
    """Logs an AI call for auditing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ai_logs (incident_id, engine, prompt, response) VALUES (?, ?, ?, ?)",
        (incident_id, engine, prompt, response)
    )
    conn.commit()
    conn.close()

# Valid table names for translated incidents (whitelist to prevent SQL injection)
_VALID_TRANSLATION_TABLES = frozenset({"security_translations", "general_translations"})

def save_translated_incident(report_type, incident_date, station, sinhala, english, confidence=1.0, engine=""):
    """Saves a translation to the specialized table based on report_type."""
    table = "security_translations" if report_type == "Security" else "general_translations"
    if table not in _VALID_TRANSLATION_TABLES:
        raise ValueError(f"Invalid translation table: {table}")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {table} (incident_date, station, original_sinhala, translation_english, confidence, engine_used) VALUES (?, ?, ?, ?, ?, ?)",
        (incident_date, station, sinhala, english, confidence, engine)
    )
    conn.commit()
    conn.close()

def log_generated_file(filepath, file_type, category):
    """Logs a generated report file for the recent files sidebar."""
    if not filepath or not os.path.exists(filepath):
        return
    filename = os.path.basename(filepath)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO recent_files (filename, filepath, file_type, report_category) VALUES (?, ?, ?, ?)",
            (filename, filepath, file_type, category)
        )
        conn.commit()
    except Exception as e:
        print(f"  [DB] Failed to log file {filename}: {e}")
    finally:
        conn.close()

def get_recent_files(limit=10):
    """Retrieves the last N generated files."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, filepath, file_type, report_category FROM recent_files ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"filename": r[0], "filepath": r[1], "file_type": r[2], "category": r[3]} for r in rows]

if __name__ == "__main__":
    init_db()
