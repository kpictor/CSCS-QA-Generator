"""
Script to analyze and fix the chapter_to_outline_map.json structure.

The issue: 
- Current map: Chapter -> Outline Path (text string)
- Code expects: Outline ID -> [List of chapters]

Solution:
- Parse outline paths to extract hierarchical IDs
- Build reverse mapping from IDs to chapters
"""
import json
import re

def parse_outline_path_to_ids(outline_path):
    """
    Converts an outline path to a list of hierarchical IDs.
    
    Example:
      "SCIENTIFIC FOUNDATIONS > 1. EXERCISE SCIENCES > A. Apply Knowledge..."
      Returns: ["I", "I.1", "I.1.A"]
    """
    # Section mapping
    section_map = {
        "SCIENTIFIC FOUNDATIONS": "I",
        "PRACTICAL/APPLIED": "II",
        "PRACTICAL / APPLIED": "II"
    }
    
    parts = [p.strip() for p in outline_path.split('>')]
    ids = []
    
    # Parse section (first part)
    if len(parts) >= 1:
        section_name = parts[0]
        for key, roman in section_map.items():
            if key in section_name:
                ids.append(roman)
                section_id = roman
                break
        else:
            return ids  # Couldn't identify section
    
    # Parse domain (second part, e.g., "1. EXERCISE SCIENCES")
    if len(parts) >= 2:
        domain_match = re.match(r'(\d+)\.', parts[1])
        if domain_match:
            domain_num = domain_match.group(1)
            domain_id = f"{section_id}.{domain_num}"
            ids.append(domain_id)
        else:
            return ids  # No domain number
    
    # Parse subdomain (third part, e.g., "A. Apply Knowledge...")
    if len(parts) >= 3:
        subdomain_match = re.match(r'([A-Z])\.', parts[2])
        if subdomain_match:
            subdomain_letter = subdomain_match.group(1)
            subdomain_id = f"{section_id}.{domain_num}.{subdomain_letter}"
            ids.append(subdomain_id)
        else:
            return ids  # No subdomain letter
    
    # Parse task (fourth part, e.g., "1. Task description")
    if len(parts) >= 4:
        task_match = re.match(r'(\d+)\.', parts[3])
        if task_match:
            task_num = task_match.group(1)
            task_id = f"{section_id}.{domain_num}.{subdomain_letter}.{task_num}"
            ids.append(task_id)
    
    return ids

# Load existing mapping
map_path = r'c:\Users\Dicrix\OneDrive\GitHub\CSCS-QA-Generator\data\metadata\chapter_to_outline_map.json'

with open(map_path, 'r', encoding='utf-8') as f:
    chapter_to_path = json.load(f)

# Build the reverse mapping: ID -> [chapters]
id_to_chapters = {}

print("Processing chapters...")
for chapter, outline_path in chapter_to_path.items():
    ids = parse_outline_path_to_ids(outline_path)
    print(f"\n{chapter}")
    print(f"  Path: {outline_path}")
    print(f"  IDs: {ids}")
    
    # Add this chapter to all extracted IDs
    for outline_id in ids:
        if outline_id not in id_to_chapters:
            id_to_chapters[outline_id] = []
        if chapter not in id_to_chapters[outline_id]:
            id_to_chapters[outline_id].append(chapter)

print("\n" + "="*60)
print("RESULTING ID -> CHAPTERS MAPPING")
print("="*60)
for outline_id in sorted(id_to_chapters.keys()):
    print(f"\n{outline_id}:")
    for chapter in id_to_chapters[outline_id]:
        print(f"  - {chapter}")

# Save the new mapping
output_path = r'c:\Users\Dicrix\OneDrive\GitHub\CSCS-QA-Generator\data\metadata\id_to_chapters_map.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(id_to_chapters, f, indent=2, ensure_ascii=False)

print(f"\n\nNew mapping saved to: {output_path}")

# Test the new mapping
print("\n" + "="*60)
print("TESTING - Looking up I.1.A")
print("="*60)
result = id_to_chapters.get("I.1.A", [])
print(f"Chapters for I.1.A: {result}")
