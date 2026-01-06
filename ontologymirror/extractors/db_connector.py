from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from ..core.domain import RawTable, RawColumn
from .base import BaseExtractor

class DbExtractor(BaseExtractor):
    """
    Extracts schema metadata and sample data from a live database.
    Supports any DB supported by SQLAlchemy (Postgres, MySQL, SQLite, etc.)
    """

    def __init__(self, connection_string: str):
        """
        Args:
            connection_string: SQLAlchemy URI (e.g., 'postgresql://user:pass@localhost/db')
        """
        self.engine: Engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)

    def extract(self, _target=None) -> List[RawTable]:
        """
        Extracts all tables from the connected database.
        Note: '_target' argument is ignored as source is the DB connection.
        """
        table_names = self.inspector.get_table_names()
        raw_tables = []

        print(f"🔌 Connected to DB. Found {len(table_names)} tables.")

        for table_name in table_names:
            try:
                # Get Columns
                columns_info = self.inspector.get_columns(table_name)
                pk_constraint = self.inspector.get_pk_constraint(table_name)
                pk_cols = pk_constraint.get('constrained_columns', [])

                raw_columns = []
                for col in columns_info:
                    raw_columns.append(RawColumn(
                        name=col['name'],
                        original_type=str(col['type']),
                        is_primary_key=(col['name'] in pk_cols),
                        description=col.get('comment')
                    ))
                
                # Fetch Sample Data (New Feature)
                samples = self.get_sample_data(table_name, limit=3)
                
                # We store the sample data in the 'raw_content' or a new field.
                # Since RawTable might not have a sample_data field yet, we'll append it to raw_content for now
                # or updated the Domain model. For now, let's append compatibility string.
                sample_str = "\n-- SAMPLE DATA PREVIEW --\n"
                if samples:
                    headers = samples[0].keys()
                    sample_str += f"-- Columns: {', '.join(headers)}\n"
                    for row in samples:
                         sample_str += f"-- {list(row.values())}\n"
                
                raw_tables.append(RawTable(
                    name=table_name,
                    columns=raw_columns,
                    source_file="[Live Database]",
                    raw_content=f"-- Extracted from Live DB\n{sample_str}" 
                ))

            except Exception as e:
                print(f"⚠️ Failed to inspect table {table_name}: {e}")
        
        return raw_tables

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches actual rows from the table.
        """
        query = text(f"SELECT * FROM {table_name} LIMIT :limit")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                # Convert to list of dicts
                return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"⚠️ Could not fetch samples for {table_name}: {e}")
            return []
