# FILE NAME: my_agent/DatabaseManager.py

import sqlite3
from typing import List, Any
import os

class DatabaseManager:
    def __init__(self, db_file=r"C:\Users\priya\OneDrive\Music\Desktop\one_day_test\data\sih_4y4.db"):
        self.db_file = os.path.abspath(db_file)
        print(f"---LOG: Database connected at: {self.db_file}---")

    def get_schema(self, uuid: str = None) -> str:
        """Retrieve the CREATE TABLE statements for the database schema."""
        if not os.path.exists(self.db_file):
            return "Database file not found."
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                schema_statements = [row[0] for row in cursor.fetchall()]
                return "\n".join(schema_statements)
        except Exception as e:
            print(f"Database schema error: {e}")
            return ""

    def execute_query(self, uuid: str = None, query: str = None) -> List[Any]:
        """Execute a read-only SQL query and return results as a list of dictionaries."""
        print(f"---LOG: Executing query: {query}---")
        if not query or not (query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("WITH")):
            return [{"error": "Invalid or non-SELECT query."}]
            
        try:
            # Connect in read-only mode
            with sqlite3.connect(f"file:{self.db_file}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row # This allows accessing columns by name
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                results_dict = [dict(row) for row in results]
                print(f"---LOG: Query returned {len(results_dict)} rows---")
                return results_dict
        except Exception as e:
            print(f"Database execution error: {e}")
            return [{"error": str(e)}]