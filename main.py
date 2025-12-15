import argparse
import os
import sys
import time

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontologymirror import __version__
from ontologymirror.extractors.sql_parser import SqlExtractor
from ontologymirror.mappers.semantic_mapper import SemanticMapper
from ontologymirror.generators.sql_generator import SqlGenerator
from ontologymirror.generators.json_generator import JsonGenerator

def main():
    parser = argparse.ArgumentParser(description=f"OntologyMirror v{__version__} - AI-Powered Schema Mapper")
    parser.add_argument("--path", required=True, help="Path to input SQL file or directory of SQL files")
    parser.add_argument("--output", required=True, help="Directory to save generated artifacts")
    
    args = parser.parse_args()
    
    print(f"🚀 OntologyMirror v{__version__} Starting...")
    print(f"   Input:  {args.path}")
    print(f"   Output: {args.output}")
    print("-" * 40)

    # Ensure output dir exists
    os.makedirs(args.output, exist_ok=True)

    # 1. Extraction
    print("\n[1/3] 📂 Extracting Schemas...")
    extractor = SqlExtractor()
    try:
        if os.path.isfile(args.path):
             # Extractor expects directory usually, but let's handle file case or dir case logic here or in extractor
             # Previous tests showed passing directory works best for now.
             # Let's try to pass key directory if it is a file
             target_dir = os.path.dirname(args.path)
             # Note: extractor.extract currently scans the dir. We might want to filter?
             # For v0.1 let's trust it scans the directory.
             raw_tables = extractor.extract(target_dir)
             # Filter if specific file was requested?
             # For now, simplistic approach: process all found tables in that dir.
        else:
            raw_tables = extractor.extract(args.path)
    except Exception as e:
        print(f"❌ Extraction Failed: {e}")
        return

    if not raw_tables:
        print("⚠️ No tables found. Exiting.")
        return
    
    print(f"      ✅ Extracted {len(raw_tables)} tables.")

    # 2. Semantic Mapping
    print("\n[2/3] 🧠 Semantic Mapping (AI)...")
    mapper = SemanticMapper()
    mapped_tables = []
    
    start_time = time.time()
    for table in raw_tables:
        print(f"      👉 Mapping '{table.name}'...", end="", flush=True)
        try:
            result = mapper.map_table(table)
            mapped_tables.append(result)
            print(f" Done. [{result.schema_class}]")
        except Exception as e:
            print(f" Failed! ({e})")
            
    duration = time.time() - start_time
    print(f"      ✅ Mapped {len(mapped_tables)} tables in {duration:.2f}s.")

    # 3. Generation
    print("\n[3/3] ⚙️ Generating Output...")
    
    # SQL
    sql_gen = SqlGenerator()
    sql_ddl = sql_gen.generate_ddl(mapped_tables)
    sql_path = os.path.join(args.output, "schema_mapped.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql_ddl)
    print(f"      📄 SQL DDL: {sql_path}")
    
    # JSON Report
    json_gen = JsonGenerator()
    json_report = json_gen.generate_report(mapped_tables)
    report_path = os.path.join(args.output, "mapping_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(json_report)
    print(f"      📊 Report:  {report_path}")

    print("-" * 40)
    print("✨ Process Complete Successfully!")

if __name__ == "__main__":
    main()
