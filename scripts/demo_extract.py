import sys
import os

# Add project root to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.extractors.git_loader import GitLoader
from ontologymirror.extractors.sql_parser import SqlExtractor

def main():
    # 1. Test Git Loader (Optional, if URL provided)
    target_dir = ""
    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        repo_url = sys.argv[1]
        print(f"🚀 Starting extraction for {repo_url}")
        loader = GitLoader()
        target_dir = loader.load_repo(repo_url)
    else:
        # Default to a local test directory if no URL
        print("⚠️ No URL provided, looking for local .sql files in ./tests/fixtures")
        target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/fixtures'))
        os.makedirs(target_dir, exist_ok=True)
        
        # Create a dummy SQL file for testing if empty
        dummy_sql = os.path.join(target_dir, "test_schema.sql")
        if not os.path.exists(dummy_sql):
            with open(dummy_sql, "w") as f:
                f.write("""
                CREATE TABLE auth_user (
                    id INT PRIMARY KEY,
                    username VARCHAR(150),
                    email VARCHAR(254),
                    is_active BOOLEAN
                );
                CREATE TABLE blog_post (
                    id INT PRIMARY KEY,
                    title VARCHAR(200),
                    content TEXT,
                    author_id INT
                );
                """)
            print(f"📄 Created dummy SQL file at {dummy_sql}")

    # 2. Run Extractor
    extractor = SqlExtractor()
    tables = extractor.extract(target_dir)

    # 3. Output Results
    print(f"\n✅ Extraction Complete! Found {len(tables)} tables.\n")
    for table in tables:
        print(f"📦 Table: {table.name}")
        print(f"   📂 Source: {table.source_file}")
        print("   📝 Columns:")
        for col in table.columns:
            pk_mark = "🔑 " if col.is_primary_key else "   "
            print(f"   {pk_mark}{col.name.ljust(15)} | {col.original_type}")
        print("-" * 40)

if __name__ == "__main__":
    main()
