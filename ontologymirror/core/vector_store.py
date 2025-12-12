import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings  # For testing without API keys, replace later
# from langchain_openai import OpenAIEmbeddings # For production
from langchain_core.documents import Document

from ..mappers.schema_loader import SchemaOrgLoader
from ..config.settings import settings

class SchemaVectorStore:
    """
    Manages the vector index of Schema.org definitions.
    Uses ChromaDB to store and retrieve 'Rich Class Documents'.
    """
    
    COLLECTION_NAME = "schema_org_classes"
    
    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory:
            self.persist_dir = persist_directory
        else:
            self.persist_dir = str(settings.DATA_DIR / "vector_store")
            
        # Ensure directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
            
        # TODO: Switch to real embeddings (OpenAI or HuggingFace) when ready
        # For Stage 1 demo, we can use a SentenceTransformer locally if installed,
        # or FakeEmbeddings to just test the flow (but Fake won't give semantic results).
        # Let's try to load a real local model if possible, or fallback to Fake for now.
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            print("🧠 Loading local embedding model (all-MiniLM-L6-v2)...")
            self.embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except ImportError:
            print("⚠️ sentence-transformers not found, using FakeEmbeddings (Results will be random!)")
            self.embedding_fn = FakeEmbeddings(size=384)

        self.vector_db = Chroma(
            collection_name=self.COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            persist_directory=self.persist_dir
        )
        self.loader = SchemaOrgLoader()

    def build_index(self, force_rebuild: bool = False):
        """
        Loads Schema.org data, converts to Documents, and indexes them.
        """
        # Check if already indexed
        if not force_rebuild and self.vector_db._collection.count() > 0:
            count = self.vector_db._collection.count()
            print(f"✅ Vector store already contains {count} documents. Skipping build.")
            return

        print("🚀 Building Vector Index from Schema.org...")
        
        # 1. Get raw classes
        classes = self.loader.get_classes()
        properties = self.loader.get_properties()
        
        # Organize properties by domain for faster lookup (optional optimization)
        # For now, we just index classes and include their description
        
        docs = []
        print(f"   Processing {len(classes)} classes...")
        
        for cls in classes:
            class_id = cls.get("@id", "")
            label = cls.get("rdfs:label", "")
            comment = cls.get("rdfs:comment", "")
            
            # Simple Text Representation
            # "Class: Person. Description: A person (alive, dead, undead, or fictional)."
            
            # Ensure label is a string
            if isinstance(label, dict):
                label = label.get("@value", "")
            
            # Ensure class_id is a string
            if isinstance(class_id, dict):
                class_id = str(class_id)
                
            page_content = f"Class: {label}\nDescription: {comment}"
            
            metadata = {
                "source": "schema.org",
                "id": str(class_id),
                "label": str(label)
            }
            
            docs.append(Document(page_content=page_content, metadata=metadata))

        # 2. Add to Chroma
        # Batching might be needed for 1000+ docs, Chroma handles some, but let's see.
        print("   Inserting into ChromaDB... (this may take a moment)")
        self.vector_db.add_documents(docs)
        # Chroma automatically persists in newer versions, but explicitly calling it logic if needed
        print(f"✅ Indexed {len(docs)} classes successfully.")

    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieves top-k most relevant Schema.org classes.
        """
        print(f"🔎 Searching for: '{query}'")
        results = self.vector_db.similarity_search(query, k=k)
        return results
