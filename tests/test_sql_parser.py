import unittest
import os
from ontologymirror.extractors.sql_parser import SqlExtractor

class TestSqlExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SqlExtractor()
        # Path to the fixture file we just created
        self.fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_schema.sql')

    def test_parse_simple_create_table(self):
        """Test parsing of standard CREATE TABLE statements."""
        if not os.path.exists(self.fixture_path):
            self.skipTest("Fixture file not found")
            
        tables = self.extractor._parse_sql_file(self.fixture_path)
        
        self.assertEqual(len(tables), 2, "Should find 2 tables")
        
        # Verify 'users' table
        users_table = next((t for t in tables if t.name == 'users'), None)
        self.assertIsNotNone(users_table)
        self.assertEqual(len(users_table.columns), 4)
        
        col_names = [c.name for c in users_table.columns]
        self.assertIn('username', col_names)
        self.assertIn('email', col_names)

        # Verify 'orders' table
        orders_table = next((t for t in tables if t.name == 'orders'), None)
        self.assertIsNotNone(orders_table)
        
    def test_parse_columns_correctly(self):
        """Test specific column attributes."""
        tables = self.extractor._parse_sql_file(self.fixture_path)
        users_table = next((t for t in tables if t.name == 'users'), None)
        
        id_col = next((c for c in users_table.columns if c.name == 'id'), None)
        self.assertTrue(id_col.is_primary_key, "ID should be PK")
        
        email_col = next((c for c in users_table.columns if c.name == 'email'), None)
        self.assertFalse(email_col.is_primary_key)

    def test_parse_with_constraints(self):
        """Test that foreign keys don't break the parser."""
        tables = self.extractor._parse_sql_file(self.fixture_path)
        orders_table = next((t for t in tables if t.name == 'orders'), None)
        
        # 'orders' has a FOREIGN KEY line, parser should ignore it as a column
        # columns: order_id, user_id, amount
        self.assertEqual(len(orders_table.columns), 3) 
        col_names = [c.name for c in orders_table.columns]
        self.assertNotIn('FOREIGN', col_names)

if __name__ == '__main__':
    unittest.main()
