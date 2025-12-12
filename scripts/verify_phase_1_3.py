import sys
import os

# Create a path to the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.extractors.sql_parser import SqlExtractor
from ontologymirror.mappers.semantic_mapper import SemanticMapper
from ontologymirror.core.domain import RawTable

def main():
    print("🛑 OntologyMirror Phase Review / 階段性驗收")
    print("==========================================")
    
    # Path to our test fixture
    sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/fixtures/test_schema.sql'))
    
    # 1. Phase 1: Extraction (SQL -> Raw Objects)
    print(f"\n[Phase 1] Extracting from: {os.path.basename(sql_path)}...")
    if not os.path.exists(sql_path):
        print(f"❌ File not found: {sql_path}")
        return

    extractor = SqlExtractor()
    raw_tables = extractor.extract(os.path.dirname(sql_path)) # SqlExtractor takes a dir usually, let's check
    # Actually SqlExtractor.extract implementation:
    # def extract(self, source_path: str) -> List[RawTable]:
    #    ... if os.path.isfile(source_path): ...
    # So passing the specific file or dir should work if implemented correctly.
    # Let's pass the directory to be safe as per previous demos
    
    print(f"✅ Extracted {len(raw_tables)} tables.")
    for t in raw_tables:
        print(f"   - Found table: {t.name} (Columns: {len(t.columns)})")

    # 2. Phase 3: Semantic Mapping (Raw Objects -> Schema.org)
    print(f"\n[Phase 3] Semantic Analysis & Mapping...")
    mapper = SemanticMapper()
    
    for table in raw_tables:
        print(f"\n   🔮 Processing '{table.name}'...")
        result = mapper.map_table(table)
        
        print(f"      👉 Mapped to Class: [{result.schema_class}]")
        print(f"      📝 Rationale: {result.rationale}")
        print("      mapped columns:")
        for col in result.columns:
            print(f"         - {col.original_name} -> {col.schema_property}")

    print("\n==========================================")
    print("✅ Phase Review Complete.")

if __name__ == "__main__":
    main()
