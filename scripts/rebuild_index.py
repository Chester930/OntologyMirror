import os
import sys
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontologymirror.core.vector_store import SchemaVectorStore

def rebuild():
    print("🔄 Force rebuilding Schema.org Vector Index...")
    try:
        # Initialize store
        store = SchemaVectorStore()
        
        # Force rebuild
        store.build_index(force_rebuild=True)
        
        print("✅ Rebuild complete! The new JSON-LD data is now indexed.")
        
    except Exception as e:
        print(f"❌ Rebuild failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    rebuild()
