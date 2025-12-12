import pytest
import os
import shutil
from ontologymirror.core.vector_store import SchemaVectorStore

# Use a separate test directory or the main one? 
# For read-only search tests, using the existing main index is faster/easier 
# as building it takes network requests.
# However, strictly unit tests should be isolated. 
# For this "verification" request, I will test against the *actual* built index 
# to confirm it works as expected for the user.

def test_store_initialization():
    store = SchemaVectorStore()
    assert store.vector_db is not None

def test_search_email():
    store = SchemaVectorStore()
    # Check if index is empty, if so, we might need to skip or fail with helpful message
    if store.vector_db._collection.count() == 0:
        pytest.skip("Vector index is empty. Run demo_vector_search.py first or allow test to build it (slow).")
        
    results = store.search("user email address", k=5)
    labels = [doc.metadata.get("label") for doc in results]
    print(f"\nSearch 'user email address' -> {labels}")
    
    # Expectation: Should find something related to Email or Contact or Person
    # Common matches: PostalAddress, EmailMessage, ContactPoint, Person
    found_relevant = any(x in labels for x in ["EmailMessage", "PostalAddress", "ContactPoint", "Person"])
    assert found_relevant, f"Did not find relevant class for email. Got: {labels}"

def test_search_flight():
    store = SchemaVectorStore()
    if store.vector_db._collection.count() == 0:
        pytest.skip("Vector index is empty.")

    results = store.search("flight reservation", k=5)
    labels = [doc.metadata.get("label") for doc in results]
    print(f"\nSearch 'flight reservation' -> {labels}")
    
    assert "FlightReservation" in labels, f"Expected FlightReservation, got {labels}"

def test_search_product():
    store = SchemaVectorStore()
    if store.vector_db._collection.count() == 0:
        pytest.skip("Vector index is empty.")

    results = store.search("product price", k=5)
    labels = [doc.metadata.get("label") for doc in results]
    print(f"\nSearch 'product price' -> {labels}")
    
    # UnitPriceSpecification is the typical schema.org match for price
    # Product is also a good match
    assert "UnitPriceSpecification" in labels or "Product" in labels or "PriceSpecification" in labels
