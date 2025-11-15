import re
import os

def parse_exam_content_outline(file_path):
    """Parses the ExamContentOutline.md file into a hierarchical dictionary."""
    outline = {}
    current_section = None
    current_domain = None
    current_subdomain = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('---') or line.startswith('# CSCS') or 'CSCS SAMPLE QUESTIONS' in line:
                continue

            # Match Section (e.g., ## SCIENTIFIC FOUNDATIONS > ...)
            section_match = re.match(r'^(## .*)', line)
            if section_match:
                current_section_header = section_match.group(1)
                # Clean the header for display
                clean_header = current_section_header.replace('## ', '').replace('**', '')
                current_section_name = clean_header.split('>')[0].strip()
                outline[current_section_name] = {
                    'header': clean_header,
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
                # Clean the header for display
                clean_header = current_domain_header.replace('### ', '').replace(')Total', ') | Total')
                
                domain_title_match = re.match(r'###\s*(\d+\.\s*[^|]+)', current_domain_header)
                if domain_title_match:
                    current_domain_name = domain_title_match.group(1).strip()
                    outline[current_section]['domains'][current_domain_name] = {
                        'header': clean_header,
                        'subdomains': {}
                    }
                    current_domain = current_domain_name
                    current_subdomain = None
                    continue

            # Match Subdomain (e.g., **A. Apply Knowledge...**)
            subdomain_match = re.match(r'^(\*\*\s*[A-Z]\.\s*.*\*\*)', line)
            if subdomain_match and current_domain:
                current_subdomain_header = subdomain_match.group(1)
                current_subdomain_name = current_subdomain_header.strip().replace("**", "")
                outline[current_section]['domains'][current_domain]['subdomains'][current_subdomain_name] = []
                current_subdomain = current_subdomain_name
                continue
            
            # Match Task (e.g., 1. Muscle anatomy...)
            task_match = re.match(r'^(\d+\.\s*.*)', line)
            if task_match and current_subdomain:
                task = task_match.group(1).strip()
                outline[current_section]['domains'][current_domain]['subdomains'][current_subdomain].append(task)

    return outline

def parse_study_guide(file_path):
    """Parses the study_guide.md file to extract key terms and study questions for each chapter."""
    study_data = {}
    current_chapter = None
    capture_mode = None # Can be 'key_terms' or 'study_questions'

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# Chapter'):
                chapter_match = re.match(r'#\s*(Chapter\s*\d+)', line)
                if chapter_match:
                    current_chapter = chapter_match.group(1).strip()
                    study_data[current_chapter] = {'key_terms': [], 'study_questions': []}
                    capture_mode = None
                continue

            if current_chapter:
                if line.startswith('### Key Terms'):
                    capture_mode = 'key_terms'
                    continue
                elif line.startswith('### Study Questions'):
                    capture_mode = 'study_questions'
                    # Reset question buffer
                    current_question_buffer = ""
                    continue
                elif line.startswith('---'):
                    # End of chapter section
                    if capture_mode == 'study_questions' and current_question_buffer:
                         study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())
                    capture_mode = None
                    current_chapter = None
                    continue

                if capture_mode == 'key_terms' and line:
                    terms = [term.strip().lower() for term in line.split(',')]
                    study_data[current_chapter]['key_terms'].extend(terms)
                
                elif capture_mode == 'study_questions':
                    # Match a question start (e.g., "1.")
                    if re.match(r'^\d+\.\s', line):
                        # If there's a question in the buffer, save it first
                        if current_question_buffer:
                            study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())
                        current_question_buffer = line + "\n"
                    # If it's part of the current question (e.g., an option "a."), append it
                    elif line and current_question_buffer:
                        current_question_buffer += line + "\n"
        
        # Add the last question from the buffer if it exists
        if current_chapter and capture_mode == 'study_questions' and current_question_buffer:
            study_data[current_chapter]['study_questions'].append(current_question_buffer.strip())


    return study_data

def parse_exam_stats(file_path):
    """Parses CSCS Exam Content.txt to get stats."""
    # This is complex to parse reliably, so we'll keep the hardcoded version
    # in ContentOrchestrator for now, but this function can be built out later.
    return {}

class MetadataManager:
    def __init__(self, base_path='.'):
        self.exam_outline_path = os.path.join(base_path, '..', 'data', 'metadata', 'ExamContentOutline.md')
        self.study_guide_path = os.path.join(base_path, '..', 'data', 'metadata', 'study_guide.md')
        
        self.exam_outline = self._load_exam_outline()
        self.study_guide_data = self._load_study_guide_data()

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

if __name__ == '__main__':
    # Example usage for testing
    metadata_manager = MetadataManager(base_path='cscs_qa_generator')
    
    # Print Exam Outline
    import json
    print("--- Exam Outline ---")
    print(json.dumps(metadata_manager.exam_outline, indent=2))

    # Print Study Guide Data for a chapter
    print("\n--- Study Guide Data for Chapter 1 ---")
    print(json.dumps(metadata_manager.study_guide_data.get('Chapter 1'), indent=2))
