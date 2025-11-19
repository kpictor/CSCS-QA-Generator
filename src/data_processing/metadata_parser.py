import re
import os
import json

def parse_exam_content_outline(file_path):
    """Parses the ExamContentOutline.md file into a hierarchical dictionary."""
    outline = {}
    current_section = None
    current_domain = None
    current_subdomain = None

    # Heuristics for Roman Numerals and Numbers
    section_map = {"SCIENTIFIC FOUNDATIONS": "I", "PRACTICAL/APPLIED": "II"} 
    
    with open(file_path, 'r', encoding='utf-8') as f:
        current_section_roman = ""
        current_domain_num = ""

        for line in f:
            line = line.strip()
            if not line or line.startswith('---') or line.startswith('# CSCS') or 'CSCS SAMPLE QUESTIONS' in line:
                continue

            # Match Section (e.g., ## SCIENTIFIC FOUNDATIONS > ...)
            section_match = re.match(r'^(## .*)', line)
            if section_match:
                current_section_header = section_match.group(1)
                clean_header = current_section_header.replace('## ', '').replace('**', '')
                current_section_name = clean_header.split('>')[0].strip()
                
                current_section_roman = section_map.get(current_section_name, "I")
                if "PRACTICAL" in current_section_name: current_section_roman = "II"

                outline[current_section_name] = {
                    'header': clean_header,
                    'id': current_section_roman,
                    'domains': {}
                }
                current_section = current_section_name
                current_domain = None
                current_subdomain = None
                continue

            # Match Domain (e.g., ### 1. EXERCISE SCIENCES  Recall: ...)
            domain_match = re.match(r'^(### .*)', line)
            if domain_match and current_section:
                current_domain_header = domain_match.group(1)
                clean_header = current_domain_header.replace('### ', '').replace(')Total', ') | Total')
                
                domain_title_match = re.match(r'###\s*(\d+)\.\s*([^|]+)', current_domain_header)
                if domain_title_match:
                    current_domain_num = domain_title_match.group(1)
                    domain_text = domain_title_match.group(2).strip()
                    current_domain_name = f"{current_domain_num}. {domain_text}" 
                    
                    outline[current_section]['domains'][current_domain_name] = {
                        'header': clean_header,
                        'id': f"{current_section_roman}.{current_domain_num}",
                        'subdomains': {}
                    }
                    current_domain = current_domain_name
                    current_subdomain = None
                    continue

            # Match Subdomain (e.g., **A. Apply Knowledge...**)
            subdomain_match = re.match(r'^(\*\*\s*([A-Z])\.\s*(.*)\*\*)', line)
            if subdomain_match and current_domain:
                full_subdomain_text = subdomain_match.group(1)
                subdomain_letter = subdomain_match.group(2)
                subdomain_text = subdomain_match.group(3)
                
                clean_subdomain_name = f"{subdomain_letter}. {subdomain_text.strip()}"
                
                outline[current_section]['domains'][current_domain]['subdomains'][clean_subdomain_name] = {
                    'header': full_subdomain_text.replace('**', ''),
                    'id': f"{current_section_roman}.{current_domain_num}.{subdomain_letter}",
                    'tasks': []
                }
                current_subdomain = clean_subdomain_name
                continue
            
            # Match Task (e.g., 1. Muscle anatomy...)
            task_match = re.match(r'^(\d+\.\s*.*)', line)
            if task_match and current_subdomain:
                task = task_match.group(1).strip()
                outline[current_section]['domains'][current_domain]['subdomains'][current_subdomain]['tasks'].append(task)

    return outline

def parse_study_guide(file_path):
    """Parses the study_guide.md file to extract key terms and study questions for each chapter."""
    study_data = {}
    current_chapter = None
    capture_mode = None 
    current_question_buffer = ""

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# Chapter'):
                chapter_match = re.match(r'#\s*(Chapter\s*\d+.*)', line)
                if chapter_match:
                    current_chapter = chapter_match.group(1).strip()
                    
                    # Extract "Chapter N" specifically to use as key (handles titles with/without colons)
                    match_short = re.match(r'(Chapter\s+\d+)', current_chapter)
                    short_chapter_key = match_short.group(1) if match_short else current_chapter.split(':')[0].strip()
                    
                    study_data[short_chapter_key] = {
                        'full_title': current_chapter,
                        'key_terms': [], 
                        'study_questions': [], 
                        'chapter_objectives': []
                    }
                    current_chapter = short_chapter_key
                    capture_mode = None
                    current_question_buffer = ""
                continue

            if current_chapter:
                if line.startswith('## Learning Aids'):
                    continue
                elif line.startswith('### Key Terms'):
                    capture_mode = 'key_terms'
                    continue
                elif line.startswith('### Study Questions'):
                    if capture_mode == 'study_questions' and current_question_buffer:
                         study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())
                    capture_mode = 'study_questions'
                    current_question_buffer = ""
                    continue
                elif line.startswith('---'):
                    if capture_mode == 'study_questions' and current_question_buffer:
                         study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())
                    capture_mode = None
                    current_chapter = None
                    current_question_buffer = ""
                    continue

                if capture_mode == 'key_terms' and line:
                    cleaned_line = line.rstrip('.')
                    terms = [term.strip().lower() for term in cleaned_line.split(',') if term.strip()]
                    study_data[current_chapter]['key_terms'].extend(terms)
                
                elif capture_mode == 'study_questions':
                    if re.match(r'^\d+\.\s', line):
                        if current_question_buffer:
                            study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())
                        current_question_buffer = line + "\n"
                    elif line:
                        if current_question_buffer:
                            current_question_buffer += line + "\n"
        
        if current_chapter and capture_mode == 'study_questions' and current_question_buffer:
            study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())

    return study_data

def parse_exam_stats(file_path):
    """Parses ExamContentOutline.md to get exam statistics including cognitive level distribution and total questions."""
    exam_stats = {}
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Match Section (e.g., ## SCIENTIFIC FOUNDATIONS > ...)
            # Regex improved to be more robust and match literal pipe
            section_match = re.match(r'^##\s*(.*?)\s*>\s*\**Cognitive Level:\**\s*Recall:\s*(\d+),\s*Application:\s*(\d+),\s*Analysis:\s*(\d+)\s*\|\s*\**Total Items:\**\s*(\d+)', line)
            if section_match:
                section_header = section_match.group(1).strip()
                recall = int(section_match.group(2))
                application = int(section_match.group(3))
                analysis = int(section_match.group(4))
                total_items = int(section_match.group(5))
                
                current_section = section_header
                exam_stats[current_section] = {
                    "total_questions": total_items,
                    "cognitive_level": {
                        "Recall": recall,
                        "Application": application,
                        "Analysis": analysis
                    },
                    "domains": {}
                }
                continue

            # Match Domain
            # Corrected regex to match literal pipes and sequential structure
            domain_match = re.match(r'^###\s*(\d+\.\s.*?)\s*Recall:.*?\|\s*Application:.*?\|\s*Analysis:.*?Total Section Weight:\s*(\d+)/\d+\s*\((.*?)\)', line)
            if domain_match and current_section:
                domain_name = domain_match.group(1).strip()
                domain_questions = int(domain_match.group(2))
                domain_percent = float(domain_match.group(3).replace('%', ''))

                exam_stats[current_section]['domains'][domain_name] = {
                    "questions": domain_questions,
                    "percent": domain_percent
                }
                continue

    return exam_stats

class MetadataManager:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.exam_outline_path = os.path.join(base_path, 'data', 'metadata', 'ExamContentOutline.md')
        self.study_guide_path = os.path.join(base_path, 'data', 'metadata', 'study_guide.md')
        self.chapter_map_path = os.path.join(base_path, 'data', 'metadata', 'chapter_to_outline_map.json')
        
        self.exam_outline = self._load_exam_outline()
        self.study_guide_data = self._load_study_guide_data()
        self.chapter_mapping = self._load_chapter_mapping()
        self.exam_weighting = self._load_exam_weighting()

    def _load_exam_outline(self):
        try:
            return parse_exam_content_outline(self.exam_outline_path)
        except FileNotFoundError:
            print(f"Warning: {self.exam_outline_path} not found. Exam outline will be empty.")
            return {}

    def _load_study_guide_data(self):
        try:
            return parse_study_guide(self.study_guide_path)
        except FileNotFoundError:
            print(f"Warning: {self.study_guide_path} not found. Study guide data will be empty.")
            return {}

    def _load_chapter_mapping(self):
        try:
            with open(self.chapter_map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.chapter_map_path} not found. Chapter mapping will be empty.")
            return {}
            
    def _load_exam_weighting(self):
        try:
            return parse_exam_stats(self.exam_outline_path)
        except FileNotFoundError:
            print(f"Warning: {self.exam_outline_path} not found. Exam weighting will be empty.")
            return {}

    def get_chapters_for_node(self, node_id):
        return self.chapter_mapping.get(node_id, [])

    def get_key_terms_for_chapter(self, chapter_name):
        short_name = chapter_name.split(':')[0].strip()
        return self.study_guide_data.get(short_name, {}).get('key_terms', [])

    def get_study_questions_for_chapter(self, chapter_name):
        short_name = chapter_name.split(':')[0].strip()
        return self.study_guide_data.get(short_name, {}).get('study_questions', [])

if __name__ == '__main__':
    # Example usage for testing
    metadata_manager = MetadataManager()
    print("--- Mapping Test (I.1.A) ---")
    print(metadata_manager.get_chapters_for_node("I.1.A"))
