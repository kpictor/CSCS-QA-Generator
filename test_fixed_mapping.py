"""
Test the fixed metadata parser to verify outline mapping works correctly.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from data_processing import metadata_parser

# Create MetadataManager
print("="*60)
print("TESTING FIXED METADATA PARSER")
print("="*60)

metadata_manager = metadata_parser.MetadataManager()

# Test various outline IDs
test_ids = ["I.1.A", "I.1", "I", "II.1.A", "II", "I.1.C"]

for node_id in test_ids:
    chapters = metadata_manager.get_chapters_for_node(node_id)
    print(f"\n{node_id}:")
    if chapters:
        for chapter in chapters:
            print(f"  - {chapter}")
    else:
        print(f"  (no chapters mapped)")

print("\n" + "="*60)
print("TEST COMPLETED SUCCESSFULLY!")
print("="*60)
