"""
Fix the walk_tree function in gui.py to only collect leaf nodes.
This script reads the file, makes the targeted fix, and writes it back.
"""
import re

file_path = r'c:\Users\Dicrix\OneDrive\GitHub\CSCS-QA-Generator\src\ui\gui.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old walk_tree function
old_walk_tree = """            def walk_tree(item_id):
                text = self.domain_tree.item(item_id, "text")
                values = self.domain_tree.item(item_id, "values")
                if text.startswith("☑ ") and values:
                    selected_items.append({
                        "id": values[0],
                        "text": text[2:],
                        "node_id": item_id,
                        "type": "topic"
                    })
                for child in self.domain_tree.get_children(item_id):
                    walk_tree(child)"""

# Define the new walk_tree function
new_walk_tree = """            def walk_tree(item_id):
                text = self.domain_tree.item(item_id, "text")
                values = self.domain_tree.item(item_id, "values")
                children = self.domain_tree.get_children(item_id)
                
                # Only add if checked AND it's a leaf node (no children)
                if text.startswith("☑ ") and values and not children:
                    # This is a leaf node (task), add it
                    selected_items.append({
                        "id": values[0],
                        "text": text[2:],
                        "node_id": item_id,
                        "type": "topic"
                    })
                
                # Recursively process all children
                for child in children:
                    walk_tree(child)"""

# Replace
content = content.replace(old_walk_tree, new_walk_tree)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed walk_tree function to only collect leaf nodes!")
print("✓ File updated successfully!")
