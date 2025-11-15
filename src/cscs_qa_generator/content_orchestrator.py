import os
import json
import re
from . import metadata_parser

class ContentOrchestrator:
    def __init__(self, base_path='.'):
        self.processed_chapters_path = os.path.join(base_path, 'processed_chapters')
        self.match_analysis_path = os.path.join(base_path, '..', 'data', 'metadata', 'Match analysis.md')
        
        self.metadata = metadata_parser.MetadataManager(base_path)
        self.detailed_outline = self.metadata.exam_outline
        
        self.domain_to_chapters = self._parse_match_analysis()
        self.chapter_data = self._load_processed_data()
        self.exam_stats = self._get_exam_stats()

    def get_exam_stats(self):
        """Returns the exam statistics including cognitive level distribution and total questions."""
        return self.exam_stats

    def _get_exam_stats(self):
        """Returns hardcoded exam statistics based on CSCS Exam Content.txt and ExamContentOutline.pdf."""
        # This remains hardcoded as parsing the text file is complex and the data is static.
        return {
            "SCIENTIFIC FOUNDATIONS": {
                "total_questions": 80,
                "domains": {
                    "1. EXERCISE SCIENCES": {"percent": 55, "questions": 44, "recall": 15, "application": 26, "analysis": 7},
                    "2. SPORT PSYCHOLOGY": {"percent": 24, "questions": 19, "recall": 6, "application": 12, "analysis": 2},
                    "3. NUTRITION": {"percent": 21, "questions": 17, "recall": 3, "application": 6, "analysis": 3}
                }
            },
            "PRACTICAL/APPLIED": { # Note the key change to match the parsed outline
                "total_questions": 110,
                "domains": {
                    "1. PROGRAM DESIGN": {"percent": 35, "questions": 38, "recall": 2, "application": 21, "analysis": 21},
                    "2. EXERCISE TECHNIQUE": {"percent": 36, "questions": 40, "recall": 5, "application": 15, "analysis": 8},
                    "3. PROGRAM IMPLEMENTATION": {"percent": 18, "questions": 20, "recall": 3, "application": 12, "analysis": 7},
                    "4. ORGANIZATION AND ADMINISTRATION": {"percent": 11, "questions": 12, "recall": 11, "application": 5, "analysis": 0}
                }
            }
        }

    def _parse_match_analysis(self):
        """Parses the Match analysis.md file to map domains to chapters."""
        domain_to_chapters = {}
        current_domain = ""
        try:
            with open(self.match_analysis_path, 'r', encoding='utf-8') as f:
                for line in f:
                    domain_match = re.match(r'###\s*(\d+\.\s*.*)', line)
                    if domain_match:
                        # Use the parsed domain name directly for mapping
                        current_domain = domain_match.group(1).strip()
                        domain_to_chapters[current_domain] = []

                    chapter_match = re.search(r'\*\*\s*(Chapter\s*\d+):', line)
                    if chapter_match and current_domain:
                        chapter_name = chapter_match.group(1).replace(':', '').strip()
                        normalized_name = self._normalize_chapter_name(chapter_name)
                        if normalized_name not in domain_to_chapters[current_domain]:
                            domain_to_chapters[current_domain].append(normalized_name)
        except FileNotFoundError:
            print(f"Warning: {self.match_analysis_path} not found. Domain mapping will be empty.")
        return domain_to_chapters

    def _normalize_chapter_name(self, chapter_name):
        """Normalizes chapter names (e.g., "Chapter 1") to match the JSON filenames (e.g., "Chapter_1_...")."""
        try:
            num = chapter_name.split()[-1]
            prefix = f"Chapter_{num}_"
            # This relies on the processed_chapters_path being accessible.
            # A better approach might be to list files during init if this fails.
            if not os.path.exists(self.processed_chapters_path):
                return chapter_name # Fallback if directory not found yet

            for fname in os.listdir(self.processed_chapters_path):
                if fname.startswith(prefix):
                    return os.path.splitext(fname)[0]
        except (IndexError, FileNotFoundError):
             return chapter_name # Fallback
        return chapter_name # Fallback

    def _load_processed_data(self):
        """Loads all processed JSON data from the 'processed_chapters' directory."""
        processed_data = {}
        try:
            for filename in os.listdir(self.processed_chapters_path):
                if filename.endswith('.json'):
                    chapter_name = os.path.splitext(filename)[0]
                    file_path = os.path.join(self.processed_chapters_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        processed_data[chapter_name] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Directory '{self.processed_chapters_path}' not found. No chapter data loaded.")
        return processed_data

    def get_chapters_for_domain(self, domain_key):
        """Finds the corresponding chapters for a given domain key from the parsed outline."""
        # The domain_key from the GUI might have extra info, so we find the base key.
        for domain in self.domain_to_chapters.keys():
            if domain_key.startswith(domain):
                return self.domain_to_chapters[domain]
        return []

    def get_content_for_domain(self, domain_key):
        """Retrieves and concatenates content for all chapters in a given domain."""
        chapters = self.get_chapters_for_domain(domain_key)
        content = ""
        for chapter_name in chapters:
            chapter_content = self.chapter_data.get(chapter_name)
            if chapter_content:
                content += f"--- Content from {chapter_name.replace('_', ' ')} ---\n\n"
                for section in chapter_content:
                    content += f"Heading: {section.get('heading', 'N/A')}\n"
                    content += f"{section.get('content', '')}\n\n"
        return content if content else "No content found for this domain."

    def get_refined_content(self, topic_path):
        """
        Retrieves refined content by searching for key terms from the study guide
        within the relevant chapters for the selected domain.
        """
        # topic_path is like: ['SCIENTIFIC FOUNDATIONS', '1. EXERCISE SCIENCES', 'A. ...', '1. ...']
        if len(topic_path) < 2:
            return "Please select a more specific topic."

        section_key = topic_path[0]
        domain_key = topic_path[1]
        
        chapters = self.get_chapters_for_domain(domain_key)
        if not chapters:
            return self.get_content_for_domain(domain_key) # Fallback

        # Get key terms from all relevant chapters
        all_keywords = set()
        for chapter_name in chapters:
            # Convert 'Chapter_1_...' to 'Chapter 1' to match study guide keys
            simple_chapter_name = " ".join(chapter_name.split('_')[:2])
            chapter_study_data = self.metadata.study_guide_data.get(simple_chapter_name)
            if chapter_study_data:
                all_keywords.update(term.lower() for term in chapter_study_data.get('key_terms', []))

        # Add keywords from the topic itself
        leaf_topic = topic_path[-1]
        topic_keywords = re.findall(r'\b\w+\b', leaf_topic.lower())
        stopwords = set(['and', 'the', 'of', 'in', 'a', 'to', 'e.g', 'is', 'are', 'for', 'from', 'or'])
        topic_keywords = [word for word in topic_keywords if word.isalpha() and word not in stopwords]
        all_keywords.update(topic_keywords)

        refined_content = ""
        for chapter_name in chapters:
            chapter_content = self.chapter_data.get(chapter_name)
            if chapter_content:
                for section in chapter_content:
                    section_text = f"Heading: {section.get('heading', 'N/A')}\n{section.get('content', '')}"
                    # If any keyword is in the section, add the whole section
                    if any(keyword in section_text.lower() for keyword in all_keywords):
                        refined_content += f"--- Relevant snippet from {chapter_name.replace('_', ' ')} ---\n"
                        refined_content += section_text + "\n\n"
        
        if not refined_content:
            return self.get_content_for_domain(domain_key) # Fallback if no keywords match

        return refined_content

    def get_example_questions_for_domain(self, domain_key):
        """Gets example questions from the study guide for the relevant chapters."""
        chapters = self.get_chapters_for_domain(domain_key)
        questions = []
        for chapter_name in chapters:
            simple_chapter_name = " ".join(chapter_name.split('_')[:2])
            chapter_study_data = self.metadata.study_guide_data.get(simple_chapter_name)
            if chapter_study_data:
                questions.extend(chapter_study_data.get('study_questions', []))
        return questions
