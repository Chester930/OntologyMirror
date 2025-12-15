import unittest
from unittest.mock import MagicMock, patch
import json
from ontologymirror.core.domain import RawTable, RawColumn
from ontologymirror.mappers.semantic_mapper import SemanticMapper, MappedTable

class TestSemanticMapper(unittest.TestCase):
    
    @patch('ontologymirror.mappers.semantic_mapper.LLMClient')
    @patch('ontologymirror.mappers.semantic_mapper.SchemaVectorStore')
    def setUp(self, MockVectorStore, MockLLMClient):
        # Setup Mocks
        self.mock_llm_instance = MockLLMClient.return_value
        self.mock_vector_store_instance = MockVectorStore.return_value
        
        # Mock Vector Store search to return dummy docs
        mock_doc = MagicMock()
        mock_doc.metadata = {"label": "Person"}
        mock_doc.page_content = "A person (alive, dead, undead, or fictional)."
        self.mock_vector_store_instance.search.return_value = [mock_doc]
        
        self.mapper = SemanticMapper()

    def test_map_table_success(self):
        """Test mapping a table successfully using a mocked LLM response."""
        
        # Input Table
        raw_table = RawTable(
            name="users",
            columns=[
                RawColumn(name="id", original_type="INT", is_primary_key=True),
                RawColumn(name="full_name", original_type="VARCHAR"),
                RawColumn(name="email_addr", original_type="VARCHAR")
            ],
            source_file="test.sql",
            raw_content=""
        )
        
        # Mock LLM Response
        mock_response_json = {
            "schema_class": "Person",
            "rationale": "Users usually map to Person.",
            "mappings": [
                {"original_name": "id", "schema_property": "identifier", "reason": "PK"},
                {"original_name": "full_name", "schema_property": "name", "reason": "Name match"},
                {"original_name": "email_addr", "schema_property": "email", "reason": "Email match"}
            ]
        }
        self.mock_llm_instance.generate.return_value = json.dumps(mock_response_json)
        
        # Execute
        result = self.mapper.map_table(raw_table)
        
        # Verify
        self.assertIsInstance(result, MappedTable)
        self.assertEqual(result.schema_class, "Person")
        self.assertEqual(len(result.columns), 3)
        
        email_map = next((m for m in result.columns if m.original_name == "email_addr"), None)
        self.assertEqual(email_map.schema_property, "email")

    def test_map_table_bad_json(self):
        """Test handling of invalid JSON from LLM."""
        raw_table = RawTable(name="test", columns=[], source_file="", raw_content="")
        
        # Mock Invalid JSON
        self.mock_llm_instance.generate.return_value = "This is not JSON"
        
        result = self.mapper.map_table(raw_table)
        
        self.assertEqual(result.schema_class, "Error")
        self.assertEqual(result.rationale, "Parsing Failed")

if __name__ == '__main__':
    unittest.main()
