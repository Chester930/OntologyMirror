import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.extractors.sql_parser import SqlExtractor
from ontologymirror.mappers.semantic_mapper import SemanticMapper

def main():
    print("🚦 Starting End-to-End Mapper Demo (Stage 3)...")
    
    # 1. Extract (Simulate)
    # We use the existing fixture or create a known table object
    from ontologymirror.core.domain import RawTable, RawColumn
    
    raw_table = RawTable(
        name="auth_user",
        source_file="dummy.sql",
        columns=[
            RawColumn(name="id", original_type="INT", is_primary_key=True),
            RawColumn(name="username", original_type="VARCHAR"),
            RawColumn(name="email", original_type="VARCHAR"),
            RawColumn(name="is_active", original_type="BOOLEAN")
        ]
    )
    
    # 2. Initialize Mapper
    mapper = SemanticMapper()
    
    # 3. Run Mapping
    print("\n🔮 Mapping Table 'auth_user'...")
    result = mapper.map_table(raw_table)
    
    # 4. Show Result
    print("\n✅ Mapping Result:")
    print(f"   📂 Original Table: {result.original_table}")
    print(f"   🌟 Mapped Class:   {result.schema_class}")
    print(f"   🤔 Rationale:      {result.rationale}")
    print("\n   📝 Column Mappings:")
    for col in result.columns:
        print(f"      - {col.original_name.ljust(15)} -> {col.schema_property} ({col.reason})")

if __name__ == "__main__":
    main()
