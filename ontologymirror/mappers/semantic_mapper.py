import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..core.domain import RawTable
from ..core.vector_store import SchemaVectorStore
from ..core.llm_client import LLMClient

class MappedColumn(BaseModel):
    """Represents a mapping from a raw SQL column to a Schema.org Property."""
    original_name: str
    schema_property: str  # e.g., "email", "givenName"
    confidence: float
    reason: str

class MappedTable(BaseModel):
    """Represents the final mapping decision for a table."""
    original_table: str
    schema_class: str     # e.g., "Person", "Organization"
    columns: List[MappedColumn]
    rationale: str

class SemanticMapper:
    """
    Coordinates the semantic mapping process.
    Steps:
      1. Receive RawTable
      2. Consult VectorStore for candidate Schema.org classes
      3. Ask LLM to pick the best class and map columns
    """
    
    def __init__(self):
        self.vector_store = SchemaVectorStore()
        # Ensure index exists (light check)
        if self.vector_store.vector_db._collection.count() == 0:
            print("⚠️ Index is empty, building now...")
            self.vector_store.build_index()
            
        self.llm = LLMClient()
        
    def map_table(self, table: RawTable) -> MappedTable:
        """
        Main entry point to map a single table.
        """
        print(f"🔄 Mapping Table: {table.name}")
        
        # 1. Retrieve Candidates
        # Construct a query string from table metadata
        query = f"Table {table.name} with columns: {', '.join([c.name for c in table.columns])}"
        candidates_docs = self.vector_store.search(query, k=3)
        
        candidates = []
        for doc in candidates_docs:
            candidates.append({
                "class": doc.metadata.get("label"),
                "description": doc.page_content,
                "recall_score": 0.0 # Placeholder if we had scores
            })
            
        print(f"   Candidates: {[c['class'] for c in candidates]}")
        
        # 2. Construct Prompt for LLM
        system_prompt = """You are an expert Ontology Engineer. Your task is to map a legacy SQL table to a standardized Schema.org Class.
        
        Output strictly in JSON format matching this structure:
        {
            "schema_class": "BestMatchingClassOrNone",
            "rationale": "Why you chose this class...",
            "mappings": [
                {"original_name": "col_name", "schema_property": "mappedProperty", "reason": "why"}
            ]
        }
        """
        
        # Serialize input data for the prompt
        table_def = {
            "table_name": table.name,
            "columns": [{"name": c.name, "type": c.original_type} for c in table.columns]
        }
        
        user_prompt = f"""
        INPUT TABLE:
        {json.dumps(table_def, indent=2)}
        
        CANDIDATE SCHEMA.ORG CLASSES (Retrieved from Knowledge Base):
        {json.dumps(candidates, indent=2)}
        
        INSTRUCTIONS:
        1. Select the SINGLE best Schema.org Class from the candidates that represents this table.
        2. If none are good matches, use "Thing" or "None".
        3. Map each column in the Input Table to a valid property of that Class.
        4. If a column has no semantic equivalent (e.g. internal DB IDs), map it to "identifier" or leave blank/null.
        """
        
        # 3. Call LLM
        response_text = self.llm.generate(system_prompt, user_prompt)
        
        # 4. Parse Response (Mock handling or JSON parsing)
        try:
            # If Mock env, the response might be simple string, so we force a valid structure for demo if needed
            if hasattr(self.llm.model, "responses"): # It's a FakeListChatModel
                 # In Mock mode, provide a fake valid response relevant to the table context if possible
                 # But FakeListChatModel just cycles responses.
                 # Let's just try to parse whatever comes back.
                 pass
            
            # Basic cleanup for common markdown block issues ```json ... ```
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            mapped_cols = []
            for m in data.get("mappings", []):
                mapped_cols.append(MappedColumn(
                    original_name=m["original_name"],
                    schema_property=m["schema_property"],
                    confidence=0.9, # Mock confidence
                    reason=m.get("reason", "")
                ))
                
            return MappedTable(
                original_table=table.name,
                schema_class=data.get("schema_class", "Thing"),
                columns=mapped_cols,
                rationale=data.get("rationale", "")
            )
            
        except json.JSONDecodeError:
            print(f"❌ LLM Output was not valid JSON: {response_text}")
            # Return empty/error object
            return MappedTable(original_table=table.name, schema_class="Error", columns=[], rationale="Parsing Failed")

