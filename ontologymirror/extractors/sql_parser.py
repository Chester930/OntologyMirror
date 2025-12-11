import os
import re
from typing import List
from .base import BaseExtractor
from ..core.domain import RawTable, RawColumn

class SqlExtractor(BaseExtractor):
    """
    Basic SQL Extractor.
    Scans for .sql files and parses CREATE TABLE statements using Regex.
    (Note: For production, a robust parser like `sqlparse` or `antlr` is better,
     but Regex is sufficient for a prototype/skeleton).
    """

    def extract(self, source_path: str) -> List[RawTable]:
        raw_tables = []
        
        # 1. Walk through the directory to find .sql files
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith(".sql"):
                    full_path = os.path.join(root, file)
                    print(f"🔍 Parsing SQL file: {full_path}")
                    tables = self._parse_sql_file(full_path)
                    raw_tables.extend(tables)
                    
        return raw_tables

    def _parse_sql_file(self, file_path: str) -> List[RawTable]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        tables = []
        # Regex to find CREATE TABLE blocks
        # This is a simplified regex and might need tuning for complex SQL
        table_pattern = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`\[]?(\w+)[\"`\]]?\s*\((.*?)\);', re.DOTALL | re.IGNORECASE)
        
        matches = table_pattern.findall(content)
        
        for table_name, columns_block in matches:
            columns = self._parse_columns(columns_block)
            
            table = RawTable(
                name=table_name,
                columns=columns,
                source_file=file_path,
                raw_content=columns_block
            )
            tables.append(table)
            
        return tables

    def _parse_columns(self, block: str) -> List[RawColumn]:
        columns = []
        # Split by comma, but be careful about commas inside parentheses (e.g. DECIMAL(10,2))
        # For prototype, we split by simple comma first. 
        # TODO: Use a proper tokenizer for nested structures.
        lines = [line.strip() for line in block.split(',')]
        
        for line in lines:
            if not line or line.upper().startswith(("CONSTRAINT", "PRIMARY KEY", "FOREIGN KEY", "INDEX", "UNIQUE")):
                continue
                
            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0].strip('"`[]')
                col_type = " ".join(parts[1:]) 
                
                # Check for descriptors
                is_pk = "PRIMARY KEY" in col_type.upper()
                
                col = RawColumn(
                    name=col_name,
                    original_type=col_type,
                    is_primary_key=is_pk,
                    description=None
                )
                columns.append(col)
                
        return columns
