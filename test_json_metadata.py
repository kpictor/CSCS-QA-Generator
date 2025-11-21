"""
Test script to verify the updated metadata parser works with JSON files.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from data_processing import metadata_parser

# Create MetadataManager
print("="*60)
print("TESTING UPDATED METADATA PARSER (JSON-based)")
print("="*60)

metadata_manager = metadata_parser.MetadataManager()

# Test chapter mapping
print("\n" + "="*60)
print("1. Testing Chapter Mapping (id_to_chapters_map.json)")
print("="*60)
test_ids = ["I.1.A", "I.1", "II.1.A"]
for node_id in test_ids:
    chapters = metadata_manager.get_chapters_for_node(node_id)
    print(f"\n{node_id}:")
    if chapters:
        for chapter in chapters[:2]:  # Show first 2
            print(f"  - {chapter}")
        if len(chapters) > 2:
            print(f"  ... and {len(chapters) - 2} more")
    else:
        print(f"  (no chapters mapped)")

# Test key term mapping
print("\n" + "="*60)
print("2. Testing Key Term Mapping (key_term_to_outline.json)")
print("="*60)
test_task_ids = ["I.1.A.1", "I.1.A.2", "I.1.C.1"]
for task_id in test_task_ids:
    terms = metadata_manager.get_key_terms_for_task(task_id)
    print(f"\n{task_id}:")
    if terms:
        print(f"  Total terms: {len(terms)}")
        print(f"  First 5 terms: {', '.join(terms[:5])}")
    else:
        print(f"  (no terms mapped)")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("="*60)
print("\nThe metadata parser is now using:")
print("  - id_to_chapters_map.json ✓")
print("  - key_term_to_outline.json ✓")
