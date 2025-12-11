import os
import re
import sqlparse
from sqlparse.sql import Statement, TokenList, Function, Parenthesis, IdentifierList, Identifier
from sqlparse.tokens import Keyword, Name, DML, DDL, Punctuation
from typing import List
from .base import BaseExtractor
from ..core.domain import RawTable, RawColumn

class SqlExtractor(BaseExtractor):
    """
    Robust SQL Extractor using `sqlparse`.
    Parses .sql files to extract table definitions and columns, handling constraints and nuances better than Regex.
    """

    def extract(self, source_path: str) -> List[RawTable]:
        raw_tables = []
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith(".sql"):
                    full_path = os.path.join(root, file)
                    print(f"🔍 Parsing SQL file: {full_path}")
                    try:
                        tables = self._parse_sql_file(full_path)
                        raw_tables.extend(tables)
                    except Exception as e:
                        print(f"⚠️ Error parsing {file}: {e}")
        return raw_tables

    def _parse_sql_file(self, file_path: str) -> List[RawTable]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # sqlparse.parse returns a list of statements
        parsed_statements = sqlparse.parse(content)
        tables = []

        for statement in parsed_statements:
            if statement.get_type() == 'CREATE':
                table = self._extract_table_from_statement(statement, file_path)
                if table:
                    tables.append(table)
        
        return tables

    def _extract_table_from_statement(self, statement: Statement, file_path: str) -> RawTable | None:
        idx_table_keyword = -1
        for i, token in enumerate(statement.tokens):
            if token.match(Keyword, 'TABLE'):
                idx_table_keyword = i
                break
        
        if idx_table_keyword == -1:
            return None

        # Look for table name
        idx_identifier = -1
        table_name = "unknown"
        for i in range(idx_table_keyword + 1, len(statement.tokens)):
            token = statement.tokens[i]
            if token.is_whitespace or token.ttype is Punctuation:
                continue
            
            table_name = str(token.value).strip('`"[] ')
            idx_identifier = i
            break
            
        if idx_identifier == -1:
            return None

        # Look for the main Parenthesis with columns
        columns = []
        raw_content = str(statement)
        
        for i in range(idx_identifier + 1, len(statement.tokens)):
            token = statement.tokens[i]
            if isinstance(token, Parenthesis):
                columns = self._parse_columns_from_parenthesis(token)
                break
        
        if not columns:
            return None

        return RawTable(
            name=table_name,
            columns=columns,
            source_file=file_path,
            raw_content=raw_content
        )

    def _parse_columns_from_parenthesis(self, parenthesis: Parenthesis) -> List[RawColumn]:
        columns = []
        
        # We need to flatten the content inside ( ... ) but respect nested parens.
        # sqlparse usually nests IdentifierList if it sees commas.
        
        content_tokens = parenthesis.tokens[1:-1] # Remove outer ( )
        
        # If the content is an IdentifierList, iterate its tokens.
        # If not, it's a mix of tokens.
        
        # Strategy: Reconstruct string and split by comma normally, 
        # but count parens to avoid splitting inside DECIMAL(10,2).
        # This is often more reliable than trusting sqlparse's incomplete grouping for complex DDL.
        
        full_content_str = "".join([str(t) for t in content_tokens])
        
        definitions = self._split_sql_by_comma(full_content_str)
        
        for definition_str in definitions:
            col_def = self._process_column_definition(definition_str.strip())
            if col_def:
                columns.append(col_def)

        return columns

    def _split_sql_by_comma(self, text: str) -> List[str]:
        """
        Splits SQL text by comma, ignoring commas inside parentheses.
        """
        definitions = []
        current = []
        paren_depth = 0
        
        for char in text:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                definitions.append("".join(current))
                current = []
            else:
                current.append(char)
                
        if current:
            definitions.append("".join(current))
            
        return definitions

    def _process_column_definition(self, definition: str) -> RawColumn | None:
        """
        Analyzes a single definition string.
        """
        # Clean up whitespace
        definition = definition.strip()
        if not definition:
            return None
            
        # Ignore comments
        if definition.startswith("--") or definition.startswith("#"):
            return None

        # Upper case for keyword checking
        upper_def = definition.upper()
        
        # Skip constraints and keys
        skip_keywords = ["PRIMARY KEY", "FOREIGN KEY", "KEY", "INDEX", "UNIQUE", "CONSTRAINT", "FULLTEXT", "CHECK", "SPATIAL"]
        
        # Check if the instruction starts with any of these
        # Use simple string matching for checking start
        first_word = definition.split()[0].upper().strip('`"[]')
        
        if first_word in skip_keywords:
            return None
            
        # Edge case: 'KEY `idx_name` ...'
        if upper_def.startswith("KEY ") or upper_def.startswith("INDEX ") or upper_def.startswith("PRIMARY KEY"):
            return None

        # Heuristic: If it has "REFERENCES", it's likely a FK definition often written as "CONSTRAINT... " or just "FOREIGN KEY..."
        # But sometimes inline FKs exist: "user_id INT REFERENCES users(id)" -> This IS a column.
        # So we only skip if it STARTS with constraint keywords.

        # Extract Name and Type
        parts = definition.split(maxsplit=1)
        if len(parts) < 2:
            # Could be just a name? Unlikely in valid SQL DDL.
            return None
            
        col_name = parts[0].strip('`"[]')
        remaining = parts[1]
        
        is_pk = "PRIMARY KEY" in upper_def
        
        return RawColumn(
            name=col_name,
            original_type=remaining,
            is_primary_key=is_pk,
            description=None
        )
