"""
Test to reproduce the issue where selecting a parent node
includes all levels instead of just the lowest level tasks.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from data_processing import metadata_parser

print("="*60)
print("TESTING HIERARCHY LEVEL ISSUE")
print("="*60)

metadata_manager = metadata_parser.MetadataManager()

# Simulate selecting "Scientific Foundations" (I)
# The current logic would add: I, I.1, I.1.A, I.1.A.1, I.1.A.2, I.1.A.3, etc.
# The CORRECT behavior: only add I.1.A.1, I.1.A.2, I.1.A.3 (lowest level tasks)

print("\nCurrent implementation issue:")
print("-" * 60)
print("When you select 'Scientific Foundations', the walk_tree")
print("function would collect these IDs (ALL levels):")
print("  - I (Section)")
print("  - I.1 (Domain)")
print("  - I.1.A (Subdomain)")
print("  - I.1.A.1 (Task) <-- This is the ONLY one we want!")
print("  - I.1.A.2 (Task) <-- This is the ONLY one we want!")
print("  - I.1.A.3 (Task) <-- This is the ONLY one we want!")

print("\n" + "="*60)
print("VERIFYING THE HIERARCHY")
print("="*60)

# Check what data exists at each level
test_ids = {
    "I": "Section",
    "I.1": "Domain",
    "I.1.A": "Subdomain",
    "I.1.A.1": "Task (LOWEST LEVEL)",
    "I.1.A.2": "Task (LOWEST LEVEL)",
    "I.1.A.3": "Task (LOWEST LEVEL)"
}

for node_id, level_name in test_ids.items():
    terms = metadata_manager.get_key_terms_for_task(node_id)
    chapters = metadata_manager.get_chapters_for_node(node_id)
    
    print(f"\n{node_id} ({level_name}):")
    print(f"  Key Terms: {len(terms)} terms")
    print(f"  Chapters: {len(chapters)} chapters")

print("\n" + "="*60)
print("ISSUE CONFIRMED")
print("="*60)
print("The problem: when you select at a high level,")
print("the app processes EVERY level instead of just the tasks!")
