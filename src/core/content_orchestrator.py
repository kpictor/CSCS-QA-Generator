import os
import json
import re
from ..data_processing import metadata_parser

class ContentOrchestrator:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        self.processed_chapters_path = os.path.join(base_path, 'processed_chapters')
        # MetadataManager expects the project root, but base_path here is 'src'
        root_path = os.path.dirname(base_path)
        self.metadata = metadata_parser.MetadataManager(root_path)
        self.chapter_data = self._load_processed_data()
        
        # Create a mapping from "Chapter X" or "Chapter X: Title" to filename "Chapter_X_..."
        self.chapter_file_map = self._create_chapter_file_map()

    def get_exam_weighting(self):
        """Returns the parsed exam weighting statistics."""
        return self.metadata.exam_weighting

    def get_outline(self):
        """Returns the full exam content outline."""
        return self.metadata.exam_outline

    def _load_processed_data(self):
        """Loads all processed JSON data from the 'processed_chapters' directory."""
        processed_data = {}
        if not os.path.exists(self.processed_chapters_path):
            print(f"Warning: Directory '{self.processed_chapters_path}' not found.")
            return processed_data
            
        try:
            for filename in os.listdir(self.processed_chapters_path):
                if filename.endswith('.json'):
                    # Store full content loaded
                    file_path = os.path.join(self.processed_chapters_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        processed_data[filename] = json.load(f) # Key is filename for now
        except Exception as e:
            print(f"Error loading processed data: {e}")
        return processed_data

    def _create_chapter_file_map(self):
        """
        Maps variations of chapter names to their specific JSON filename.
        e.g. "Chapter 1" -> "Chapter_1_Structure_....json"
        e.g. "Chapter 1: Structure..." -> "Chapter_1_Structure_....json"
        """
        mapping = {}
        if not self.chapter_data:
            return mapping

        for filename in self.chapter_data.keys():
            # filename example: Chapter_1_Structure_and_Function_of_Body_Systems.json
            # We extract the "Chapter_1" part to map "Chapter 1"
            match = re.match(r'(Chapter)_(\d+)_', filename)
            if match:
                # Map "Chapter 1"
                short_key = f"{match.group(1)} {match.group(2)}" # "Chapter 1"
                mapping[short_key] = filename
                
                # Map full title if possible (replacing underscores with spaces)
                full_title_key = filename.replace('.json', '').replace('_', ' ')
                mapping[full_title_key] = filename
        return mapping

    def _resolve_filenames(self, chapter_identifiers):
        """
        Takes a list of chapter identifiers (e.g. ["Chapter 1", "Chapter 7: ..."])
        and returns the list of corresponding JSON filenames.
        """
        filenames = set()
        for ident in chapter_identifiers:
            # 1. Try exact match
            if ident in self.chapter_file_map:
                filenames.add(self.chapter_file_map[ident])
                continue
            
            # 2. Try matching "Chapter X" prefix
            short_match = re.match(r'(Chapter\s+\d+)', ident)
            if short_match:
                short_key = short_match.group(1)
                if short_key in self.chapter_file_map:
                    filenames.add(self.chapter_file_map[short_key])
        return list(filenames)

    def get_context_for_node(self, node_id):
        """
        Retrieves all necessary context for a specific Outline Node ID.
        
        Returns:
            dict: {
                "chapters": [list of filenames],
                "text_content": "combined text content...",
                "key_terms": [list of key terms],
                "example_questions": [list of example questions]
            }
        """
        # 1. Get Chapter Identifiers from Metadata
        chapter_ids = self.metadata.get_chapters_for_node(node_id)
        
        # 2. Resolve to Filenames
        filenames = self._resolve_filenames(chapter_ids)
        
        context = {
            "chapters": filenames,
            "text_content": "",
            "key_terms": [],
            "example_questions": []
        }
        
        # 3. Aggregate Data
        for fname in filenames:
            # Content
            chapter_json = self.chapter_data.get(fname)
            if chapter_json:
                # Extract chapter number for display/header
                chap_title = fname.replace('_', ' ').replace('.json', '')
                context["text_content"] += f"\n\n--- CONTENT FROM: {chap_title} ---"
                for section in chapter_json:
                    heading = section.get('heading', 'Section')
                    body = section.get('content', '')
                    context["text_content"] += f"### {heading}\n{body}\n"

            # Key Terms & Questions
            # We need the "Chapter X" key to lookup in metadata
            match = re.match(r'(Chapter)_(\d+)_', fname)
            if match:
                short_key = f"{match.group(1)} {match.group(2)}" # "Chapter 1"
                
                terms = self.metadata.get_key_terms_for_chapter(short_key)
                context["key_terms"].extend(terms)
                
                questions = self.metadata.get_study_questions_for_chapter(short_key)
                context["example_questions"].extend(questions)

        # Deduplicate terms
        context["key_terms"] = sorted(list(set(context["key_terms"])))
        
        return context