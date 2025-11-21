"""
Test script to verify and demonstrate the chapter_to_outline_map.json issue.
"""
import json
import os

# Load the chapter_to_outline_map.json
map_path = r'c:\Users\Dicrix\OneDrive\GitHub\CSCS-QA-Generator\data\metadata\chapter_to_outline_map.json'

with open(map_path, 'r', encoding='utf-8') as f:
    chapter_map = json.load(f)

print("="*60)
print("CURRENT STRUCTURE (Chapter -> Outline Path)")
print("="*60)
for i, (key, value) in enumerate(list(chapter_map.items())[:3]):
    print(f"{i+1}. Key: {key}")
    print(f"   Value: {value}")
    print()

print("="*60)
print("WHAT THE CODE EXPECTS (Outline ID -> List of Chapters)")
print("="*60)
print("Example: Looking up 'I.1.A' should return:")
print("  ['Chapter 1: Structure and Function of Body Systems']")
print()
print("But with current structure:")
test_id = "I.1.A"
result = chapter_map.get(test_id, [])
print(f"  chapter_map.get('{test_id}') = {result}")
print()

print("="*60)
print("PROPOSED FIX: Reverse and Build Proper Mapping")
print("="*60)
print("Need to:")
print("1. Parse outline paths to extract IDs (I, I.1, I.1.A, etc.)")
print("2. Map each ID -> list of chapters that reference it")
print()
