from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# ==========================================
# Phase 1: Raw Schema (From Extractor)
# ==========================================

class RawColumn(BaseModel):
    """
    Represents a single column extracted from the source code.
    代表從原始碼中提取出的單一欄位。
    """
    name: str = Field(..., description="The original column name (e.g., 'f_name', 'is_active')")
    original_type: str = Field(..., description="The original data type (e.g., 'VARCHAR(255)', 'models.BooleanField')")
    is_primary_key: bool = False
    is_nullable: bool = True
    description: Optional[str] = Field(None, description="Comments or docstrings associated with this column")

class RawTable(BaseModel):
    """
    Represents a table or model definition extracted from the source.
    代表從原始碼提取出的資料表或 Model 定義。
    """
    name: str = Field(..., description="The original table or class name (e.g., 'auth_user', 'UserProfile')")
    columns: List[RawColumn]
    source_file: str = Field(..., description="Where this table was found (e.g., 'src/models.py')")
    raw_content: Optional[str] = Field(None, description="The full original code block for context")

# ==========================================
# Phase 2: Semantic Schema (From Mapper)
# ==========================================

class MappedProperty(BaseModel):
    """
    Represents a mapping from a raw column to a Schema.org property.
    代表一個原始欄位到 Schema.org 屬性的映射結果。
    """
    raw_column: RawColumn
    schema_org_property: str = Field(..., description="The matched Schema.org property (e.g., 'givenName')")
    normalized_type: str = Field(..., description="The standard SQL type mapped to (e.g., 'VARCHAR(255)')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the mapping")
    reasoning: str = Field(..., description="Explanation from the LLM for this mapping decision")

class MappedEntity(BaseModel):
    """
    Represents a fully mapped entity corresponding to a Schema.org Type.
    代表一個完整的實體，已映射到 Schema.org 類型。
    """
    raw_table_name: str
    schema_org_type: str = Field(..., description="The matched Schema.org Type (e.g., 'Person', 'Organization')")
    description: str = Field(..., description="Description of what this entity represents")
    properties: List[MappedProperty]
