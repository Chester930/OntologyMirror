import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.extractors.sql_parser import SqlExtractor
from ontologymirror.mappers.semantic_mapper import SemanticMapper
from ontologymirror.generators.sql_generator import SqlGenerator
from ontologymirror.generators.json_generator import JsonGenerator

def main():
    print("🚦 Starting Phase 4 Demo: Generation")
    print("===================================")
    
    # 1. Extraction (Using fixture)
    sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/fixtures/test_schema.sql'))
    print(f"📂 Reading {os.path.basename(sql_path)}...")
    
    extractor = SqlExtractor()
    # Assuming the Extractor works on dir or file, using dir for safety as per before
    # Or actually pass the file if it supports it. Looking at recent verify script, we passed dir.
    # But wait, verify_phase_1_3 passed os.path.dirname(sql_path).
    raw_tables = extractor.extract(os.path.dirname(sql_path))
    
    # 2. Mapping
    print("🧠 Mapping Tables...")
    mapper = SemanticMapper()
    mapped_tables = []
    
    for t in raw_tables:
        # Just map auth_user and blog_post for cleaner demo output if others exist
        if t.name in ["auth_user", "blog_post"]:
             result = mapper.map_table(t)
             mapped_tables.append(result)
             print(f"   - {t.name} -> {result.schema_class}")
             
    # 3. Generation
    print("\n⚙️ Generating Artifacts...")
    
    # SQL
    sql_gen = SqlGenerator()
    sql_output = sql_gen.generate_ddl(mapped_tables)
    
    out_sql_path = "output_schema.sql"
    with open(out_sql_path, "w", encoding="utf-8") as f:
        f.write(sql_output)
    print(f"✅ Generated SQL: {out_sql_path}")
    print("-" * 20)
    print(sql_output)
    print("-" * 20)
    
    # JSON
    json_gen = JsonGenerator()
    json_output = json_gen.generate_report(mapped_tables)
    
    out_json_path = "output_report.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\n✅ Generated Report: {out_json_path}")

if __name__ == "__main__":
    main()
