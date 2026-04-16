import sqlite3
import os

DB_PATH = "police_reports.db"

def research():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Table: security_translations ---")
    try:
        cursor.execute("SELECT COUNT(*) FROM security_translations")
        print(f"Total rows: {cursor.fetchone()[0]}")
        cursor.execute("SELECT * FROM security_translations LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"Sample: Date={row['incident_date']}, Station={row['station']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Table: general_translations ---")
    try:
        cursor.execute("SELECT COUNT(*) FROM general_translations")
        print(f"Total rows: {cursor.fetchone()[0]}")
        cursor.execute("SELECT * FROM general_translations LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"Sample: Date={row['incident_date']}, Station={row['station']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Available Dates with Translations ---")
    try:
        cursor.execute("SELECT incident_date, 'Security' as type, COUNT(*) as count FROM security_translations GROUP BY incident_date UNION ALL SELECT incident_date, 'General' as type, COUNT(*) as count FROM general_translations GROUP BY incident_date ORDER BY incident_date DESC LIMIT 10")
        for row in cursor.fetchall():
            print(f"Date: {row['incident_date']} | Type: {row['type']} | Count: {row['count']}")
    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    research()
