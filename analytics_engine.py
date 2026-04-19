"""
analytics_engine.py — Police Report Analytics & Visualization
Version: v3.0.0
Features: Safe DB queries, Robust plotting, Proper resource cleanup
"""
import os
import sqlite3
import logging
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from db_manager import DB_PATH

logger = logging.getLogger(__name__)

# Ensure render directory exists
RENDER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

class AnalyticsEngine:
    def __init__(self):
        self.db_path = DB_PATH
        sns.set_theme(style="darkgrid")
        plt.rcParams.update({
            'figure.facecolor': '#121212',
            'axes.facecolor': '#1e1e1e',
            'text.color': 'white',
            'axes.labelcolor': 'lightgray',
            'xtick.color': 'gray',
            'ytick.color': 'gray',
            'axes.titlesize': 14,
            'axes.labelsize': 11,
        })

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with timeout."""
        return sqlite3.connect(self.db_path, timeout=10)

    def generate_crime_distribution_by_province(self) -> str | None:
        """Generates a bar chart showing incident counts across provinces."""
        conn = None
        try:
            conn = self._get_conn()
            query = """
            SELECT province, COUNT(*) as count 
            FROM incidents 
            WHERE province IS NOT NULL AND province != ''
            GROUP BY province 
            ORDER BY count DESC
            """
            df = pd.read_sql_query(query, conn)

            if df.empty:
                logger.info("  [Analytics] No province data available for chart.")
                return None

            plt.figure(figsize=(10, 6))
            sns.barplot(x='count', y='province', data=df, palette='viridis')
            plt.title('Crime Distribution by Province', fontsize=16, pad=20)
            plt.xlabel('Incident Count')
            plt.ylabel('Province')
            plt.tight_layout()

            output_path = os.path.join(RENDER_DIR, "province_distribution.png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            logger.info(f"  [Analytics] Province chart saved: {output_path}")
            return output_path

        except sqlite3.OperationalError as e:
            logger.error(f"  [Analytics] DB Query Error: {e}")
            return None
        except Exception as e:
            logger.error(f"  [Analytics] Chart generation failed: {type(e).__name__}: {e}")
            return None
        finally:
            if conn:
                conn.close()
            plt.close('all')

    def generate_incident_trend(self) -> str | None:
        """Generates a line chart showing incident trends over time."""
        conn = None
        try:
            conn = self._get_conn()
            query = """
            SELECT r.report_date, COUNT(i.id) as count
            FROM reports r
            JOIN sections s ON r.id = s.report_id
            JOIN incidents i ON s.id = i.section_id
            WHERE r.report_date IS NOT NULL
            GROUP BY r.report_date
            ORDER BY r.report_date ASC
            """
            df = pd.read_sql_query(query, conn)

            if df.empty:
                logger.info("  [Analytics] No temporal data available for trend chart.")
                return None

            df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
            df = df.dropna(subset=['report_date'])

            if df.empty:
                return None

            plt.figure(figsize=(12, 6))
            plt.plot(df['report_date'], df['count'], marker='o', linestyle='-', color='#00d1ff', linewidth=2)
            plt.fill_between(df['report_date'], df['count'], color='#00d1ff', alpha=0.1)
            plt.title('Incident Trends (Daily Report Count)', fontsize=16)
            plt.xlabel('Date')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            output_path = os.path.join(RENDER_DIR, "incident_trend.png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            logger.info(f"  [Analytics] Trend chart saved: {output_path}")
            return output_path

        except sqlite3.OperationalError as e:
            logger.error(f"  [Analytics] DB Query Error: {e}")
            return None
        except Exception as e:
            logger.error(f"  [Analytics] Trend chart failed: {type(e).__name__}: {e}")
            return None
        finally:
            if conn:
                conn.close()
            plt.close('all')

    def get_summary_stats(self) -> dict:
        """Returns a dictionary of key metrics for the dashboard header."""
        stats = {
            'total_reports': 0, 'total_incidents': 0,
            'security_incidents': 0, 'general_incidents': 0
        }
        conn = None
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
            if not cursor.fetchone():
                logger.warning("  [Analytics] 'reports' table not found.")
                return stats

            cursor.execute("SELECT COUNT(*) FROM reports")
            stats['total_reports'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM incidents")
            stats['total_incidents'] = cursor.fetchone()[0]

            for table, key in [("security_translations", "security_incidents"),
                              ("general_translations", "general_incidents")]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[key] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    logger.debug(f"  [Analytics] Table '{table}' not found, skipping.")
                except Exception as e:
                    logger.warning(f"  [Analytics] Failed to query {table}: {e}")

        except sqlite3.Error as e:
            logger.error(f"  [Analytics] Database error: {e}")
        except Exception as e:
            logger.error(f"  [Analytics] Stats fetch failed: {type(e).__name__}: {e}")
        finally:
            if conn:
                conn.close()
        return stats

    def get_top_stations(self, limit: int = 10) -> list[dict]:
        """Returns top N stations by incident count."""
        conn = None
        try:
            conn = self._get_conn()
            query = """
            SELECT station, COUNT(*) as count
            FROM incidents
            WHERE station IS NOT NULL AND station != ''
            GROUP BY station
            ORDER BY count DESC
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df.to_dict('records') if not df.empty else []
        except Exception as e:
            logger.error(f"  [Analytics] Top stations query failed: {e}")
            return []
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = AnalyticsEngine()
    print("Generating analytics charts...")
    p1 = engine.generate_crime_distribution_by_province()
    p2 = engine.generate_incident_trend()
    stats = engine.get_summary_stats()
    print(f"✓ Province Chart: {p1}")
    print(f"✓ Trend Chart: {p2}")
    print(f"✓ Stats: {stats}")