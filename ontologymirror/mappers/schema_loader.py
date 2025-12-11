import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
from ..config.settings import settings

class SchemaOrgLoader:
    """
    Downloads and provides access to Schema.org definitions (JSON-LD).
    Source: https://schema.org/docs/developers.html
    """
    
    # We use the 'all' variant to cover core + all extensions (like auto, bib, etc.)
    # Using HTTPS version as per best practice.
    DOWNLOAD_URL = "https://schema.org/version/latest/schemaorg-all-https.jsonld"
    
    def __init__(self):
        self.kb_dir = settings.DATA_DIR / "knowledge_base"
        self.file_path = self.kb_dir / "schemaorg-all-https.jsonld"
        self.graph: List[Dict[str, Any]] = []
        
    def ensure_schema_loaded(self):
        """
        Ensures the JSON-LD file exists locally and loads it into memory.
        """
        if not self.file_path.exists():
            self._download_schema()
            
        if not self.graph:
            self._load_from_disk()
            
    def _download_schema(self):
        print(f"📥 Downloading Schema.org definitions from {self.DOWNLOAD_URL}...")
        os.makedirs(self.kb_dir, exist_ok=True)
        
        try:
            response = requests.get(self.DOWNLOAD_URL, timeout=30)
            response.raise_for_status()
            
            with open(self.file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Schema.org definitions saved to {self.file_path}")
            
        except Exception as e:
            print(f"❌ Failed to download schema: {e}")
            raise

    def _load_from_disk(self):
        print(f"📖 Loading Schema.org graph from {self.file_path}...")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # The JSON-LD usually has a "@graph" key containing the list of nodes
                if "@graph" in data:
                    self.graph = data["@graph"]
                else:
                    # Some versions might be a direct list, but @graph is standard for the 'all' dump
                    self.graph = data
            print(f"🧠 Loaded {len(self.graph)} definitions into memory.")
        except Exception as e:
            print(f"❌ Failed to load schema from disk: {e}")
            raise

    def get_classes(self) -> List[Dict[str, Any]]:
        """
        Returns all nodes that are Classes (e.g. Person, Event).
        In Schema.org JSON-LD, these have "@type": "rdfs:Class" or "rdfs:Class" in the list.
        """
        self.ensure_schema_loaded()
        classes = []
        for node in self.graph:
            node_type = node.get("@type")
            # @type can be a string or list
            if node_type == "rdfs:Class" or (isinstance(node_type, list) and "rdfs:Class" in node_type):
                classes.append(node)
        return classes

    def get_properties(self) -> List[Dict[str, Any]]:
        """
        Returns all nodes that are Properties (e.g. givenName, email).
        In Schema.org JSON-LD, these have "@type": "rdf:Property".
        """
        self.ensure_schema_loaded()
        props = []
        for node in self.graph:
            node_type = node.get("@type")
            if node_type == "rdf:Property" or (isinstance(node_type, list) and "rdf:Property" in node_type):
                props.append(node)
        return props
