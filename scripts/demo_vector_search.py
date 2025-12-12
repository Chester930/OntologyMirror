import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.core.vector_store import SchemaVectorStore

def main():
    print("🚦 Starting Vector Store Demo (Stage 1)...")
    
    # 1. Initialize Store
    store = SchemaVectorStore()
    
    # 2. Build Index (only if empty or forced)
    # Note: On first run, this might take a minute to download embedding model and index data
    store.build_index()
    
    # 3. Test Queries
    test_queries = [
        "user email address",
        "company organization",
        "blog post article",
        "product price",
        "flight reservation"
    ]
    
    print("\n🧐 Testing Retrieval Accuracy:")
    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        results = store.search(query, k=2)
        for i, doc in enumerate(results):
            label = doc.metadata.get("label", "Unknown")
            print(f"   {i+1}. [Class: {label}]")
            # Print first 100 chars of description
            desc = doc.page_content.split("Description: ")[1][:100] + "..."
            print(f"      {desc}")

if __name__ == "__main__":
    main()
