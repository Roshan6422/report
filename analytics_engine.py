import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from db_manager import DB_PATH

# Ensure render directory exists
RENDER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
if not os.path.exists(RENDER_DIR):
    os.makedirs(RENDER_DIR)

class AnalyticsEngine:
    def __init__(self):
        self.db_path = DB_PATH
        sns.set_theme(style="darkgrid")
        plt.rcParams['figure.facecolor'] = '#121212'
        plt.rcParams['axes.facecolor'] = '#1e1e1e'
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'lightgray'
        plt.rcParams['xtick.color'] = 'gray'
        plt.rcParams['ytick.color'] = 'gray'

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def generate_crime_distribution_by_province(self):
        """
        Generates a bar chart showing incident counts across provinces.
        """
        conn = self._get_conn()
        query = """
        SELECT province, COUNT(*) as count 
        FROM incidents 
        GROUP BY province 
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return None

        plt.figure(figsize=(10, 6))
        sns.barplot(x='count', y='province', data=df, palette='viridis')
        plt.title('Crime Distribution by Province', fontsize=16, pad=20)
        plt.xlabel('Incident Count')
        plt.ylabel('Province')

        output_path = os.path.join(RENDER_DIR, "province_distribution.png")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path

    def generate_incident_trend(self):
        """
        Generates a line chart showing incident trends over time.
        """
        conn = self._get_conn()
        # Join with reports to get dates
        query = """
        SELECT r.report_date, COUNT(i.id) as count
        FROM reports r
        JOIN sections s ON r.id = s.report_id
        JOIN incidents i ON s.id = i.section_id
        GROUP BY r.report_date
        ORDER BY r.report_date ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return None

        df['report_date'] = pd.to_datetime(df['report_date'])

        plt.figure(figsize=(12, 6))
        plt.plot(df['report_date'], df['count'], marker='o', linestyle='-', color='#00d1ff')
        plt.fill_between(df['report_date'], df['count'], color='#00d1ff', alpha=0.1)
        plt.title('Incident Trends (Daily Report Count)', fontsize=16)
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.xticks(rotation=45)

        output_path = os.path.join(RENDER_DIR, "incident_trend.png")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path

    def get_summary_stats(self):
        """
        Returns a dictionary of key metrics for the dashboard header.
        """
        stats = {
            'total_reports': 0, 'total_incidents': 0,
            'security_incidents': 0, 'general_incidents': 0
        }
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
            if not cursor.fetchone():
                return stats

            cursor.execute("SELECT COUNT(*) FROM reports")
            stats['total_reports'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM incidents")
            stats['total_incidents'] = cursor.fetchone()[0]

            # Use try/except for specific translation tables which might be missing in older schemas
            try:
                cursor.execute("SELECT COUNT(*) FROM security_translations")
                stats['security_incidents'] = cursor.fetchone()[0]
            except Exception: pass

            try:
                cursor.execute("SELECT COUNT(*) FROM general_translations")
                stats['general_incidents'] = cursor.fetchone()[0]
            except Exception: pass

            conn.close()
        except Exception as e:
            print(f"[Analytics] Stats fetch failed: {e}")
        return stats

if __name__ == "__main__":
    engine = AnalyticsEngine()
    print("Generating charts...")
    p1 = engine.generate_crime_distribution_by_province()
    p2 = engine.generate_incident_trend()
    print(f"Done. Province Chart: {p1}, Trend Chart: {p2}")
