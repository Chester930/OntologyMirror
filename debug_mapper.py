import os
import sys
import traceback
from dotenv import load_dotenv

# Load env variables (CRITICAL for real API)
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontologymirror.mappers.semantic_mapper import SemanticMapper
from ontologymirror.core.domain import RawTable, RawColumn

def debug_mapping():
    print("🔍 Starting Debug Mapping...")
    try:
        mapper = SemanticMapper()
        
        # Create a dummy table similar to 'employees'
        table = RawTable(
            name="employees",
            source_file="debug",
            columns=[
                RawColumn(name="emp_no", original_type="int"),
                RawColumn(name="birth_date", original_type="date"),
                RawColumn(name="first_name", original_type="varchar"),
                RawColumn(name="last_name", original_type="varchar"),
            ]
        )
        
        print(f"👉 Mapping table: {table.name} using provider: {mapper.llm.provider}")
        result = mapper.map_table(table)
        print("✅ Success!")
        print(result.json(indent=2))
        
    except Exception:
        print("❌ Error Caught:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_mapping()
