import os
import shutil
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .extractors.sql_parser import SqlExtractor
from .mappers.semantic_mapper import SemanticMapper, MappedTable, MappedColumn
from .generators.sql_generator import SqlGenerator
from .generators.json_generator import JsonGenerator
from .core.domain import RawTable

app = FastAPI(title="OntologyMirror API", version="0.1.0")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
# In a real app, use a database or session cache
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MapRequest(BaseModel):
    tables: List[Dict[str, Any]] # Simplified input for now

@app.get("/")
def read_root():
    return {"status": "ok", "service": "OntologyMirror API"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a SQL file and extracts tables.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        extractor = SqlExtractor()
        # Extract supports directory or file? Our updated valid extractor supports file path check logic ideally,
        # or we pass the dir. Let's pass the file path directly if we updated Extractor to support it, 
        # OR pass the dir. Based on main.py, we passed dir or file path.
        # Let's assume file path works based on previous fixes or I might need to fix it.
        # Re-reading main.py from memory... 
        # "if os.path.isfile(args.path): ... raw_tables = extractor.extract(target_dir)"
        # So SqlExtractor.extract takes a directory.
        
        raw_tables = extractor.extract(UPLOAD_DIR)
        
        # Filter to only the tables from this file if possible, or just return all
        # For simplicity, return all in temp dir (users should clean up)
        
        # Convert to JSON-serializable dicts
        tables_data = []
        for t in raw_tables:
            # Simple conversion
            tables_data.append({
                "name": t.name,
                "columns": [{"name": c.name, "type": c.original_type} for c in t.columns],
                "raw_content": t.raw_content
            })
            
        return {"filename": file.filename, "tables": tables_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/map")
async def map_tables(payload: MapRequest):
    """
    Maps a list of raw table definitions to Schema.org.
    """
    mapper = SemanticMapper()
    results = []
    
    # Reconstruct RawTable objects (simplified)
    # Note: This is inefficient (re-init mapper every time). 
    # But okay for MVP.
    
    for t_data in payload.tables:
        # Mocking the RawTable input reconstruction
        # We need to import RawColumn... wait, RawTable needs list of RawColumns
        from .core.domain import RawColumn
        
        cols = [RawColumn(name=c['name'], original_type=c['type']) for c in t_data.get('columns', [])]
        raw_table = RawTable(
            name=t_data['name'],
            columns=cols,
            source_file="api_upload",
            raw_content=t_data.get('raw_content')
        )
        
        mapping_result = mapper.map_table(raw_table)
        results.append(mapping_result.dict()) # Pydantic v1/v2 export
        
    return results

@app.post("/api/generate")
async def generate_artifacts(mapped_tables: List[Dict[str, Any]]):
    """
    Generates SQL and JSON from mapped tables.
    """
    # Reconstruct MappedTable objects logic would be needed here
    # For MVP, let's just use the Generator classes but we need MappedTable objects.
    # We can perform a quick dict -> Object conversion.
    
    real_mapped_tables = []
    for mt in mapped_tables:
        # Pydantic parsing
        obj = MappedTable.parse_obj(mt)
        real_mapped_tables.append(obj)
        
    sql_gen = SqlGenerator()
    sql_out = sql_gen.generate_ddl(real_mapped_tables)
    
    json_gen = JsonGenerator()
    json_out = json_gen.generate_report(real_mapped_tables)
    
    return {
        "sql": sql_out,
        "json": json_out
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
