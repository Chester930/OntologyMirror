import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.mappers.schema_loader import SchemaOrgLoader

def main():
    loader = SchemaOrgLoader()
    
    # This should trigger download if not exists
    loader.ensure_schema_loaded()
    
    classes = loader.get_classes()
    props = loader.get_properties()
    
    print(f"\n📊 Statistics:")
    print(f"   Entities (Classes): {len(classes)}")
    print(f"   Properties: {len(props)}")
    
    # Show some examples
    print("\n🧐 Random Examples:")
    if classes:
        print(f"   Class: {classes[0].get('rdfs:label', 'Unknown')}")
    if props:
        print(f"   Property: {props[0].get('rdfs:label', 'Unknown')}")

if __name__ == "__main__":
    main()
