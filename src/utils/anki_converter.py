"""
Anki Flashcard Converter
Converts translated Chinese Q&A markdown files to Anki-compatible TXT format.
"""

import re
import os


def parse_translated_markdown(content):
    """
    Parse translated Chinese Q&A markdown into structured question objects.
    
    Expected format:
    ## 关键术语: [English Term] ([Chinese Term])
    **问题:** [Question Text]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    
    **正确答案:** [Answer]
    **解析:**
    [Explanation]
    ---
    
    Args:
        content: Markdown file content
        
    Returns:
        List of question dictionaries with keys: key_term, question, options, answer, explanation
    """
    questions = []
    
    # Split by horizontal rule to separate questions
    sections = re.split(r'\n---+\n', content)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        question_obj = {}
        
        # Extract key term (optional - might not always be present)
        key_term_match = re.search(r'##\s*关键术语[:：]\s*(.+?)(?=\n|$)', section)
        if key_term_match:
            question_obj['key_term'] = key_term_match.group(1).strip()
        else:
            question_obj['key_term'] = ''
        
        # Extract question text
        question_match = re.search(r'\*\*问题[:：]\*\*\s*(.+?)(?=\n[A-D]\.|\n\*\*|$)', section, re.DOTALL)
        if question_match:
            question_obj['question'] = question_match.group(1).strip()
        else:
            # Skip this section if no question found
            continue
        
        # Extract options A, B, C (some questions might have D)
        options = {}
        for option_letter in ['A', 'B', 'C', 'D']:
            option_pattern = rf'{option_letter}\.\s*(.+?)(?=\n[A-D]\.|\n\*\*|$)'
            option_match = re.search(option_pattern, section, re.DOTALL)
            if option_match:
                options[option_letter] = option_match.group(1).strip()
        
        question_obj['options'] = options
        
        # Extract correct answer
        answer_match = re.search(r'\*\*正确答案[:：]\*\*\s*([A-D])', section)
        if answer_match:
            question_obj['answer'] = answer_match.group(1).strip()
        else:
            question_obj['answer'] = ''
        
        # Extract explanation
        explanation_match = re.search(r'\*\*解析[:：]\*\*\s*(.+?)(?=\n---|$)', section, re.DOTALL)
        if explanation_match:
            question_obj['explanation'] = explanation_match.group(1).strip()
        else:
            question_obj['explanation'] = ''
        
        # Only add if we have at least a question and answer
        if question_obj.get('question') and question_obj.get('answer'):
            questions.append(question_obj)
    
    return questions


def create_anki_flashcard(question_obj, tags=''):
    """
    Convert a question object into an Anki-compatible flashcard.
    
    Format:
    - Front: Key term (if present) + Question + All options
    - Back: Correct answer + Explanation
    - Tags: Optional tags
    
    Args:
        question_obj: Dictionary with question data
        tags: Space-separated tags string
        
    Returns:
        Tuple of (front, back, tags) strings
    """
    # Build front of card
    front_parts = []
    
    # Add key term if present
    if question_obj.get('key_term'):
        front_parts.append(f"<b>{question_obj['key_term']}</b><br><br>")
    
    # Add question
    front_parts.append(f"{question_obj['question']}<br><br>")
    
    # Add options
    options = question_obj.get('options', {})
    for letter in sorted(options.keys()):
        front_parts.append(f"{letter}. {options[letter]}<br>")
    
    front = ''.join(front_parts)
    
    # Build back of card
    back_parts = []
    
    # Add correct answer
    answer_letter = question_obj.get('answer', '')
    if answer_letter and answer_letter in options:
        back_parts.append(f"<b>正确答案: {answer_letter}</b><br>")
        back_parts.append(f"{options[answer_letter]}<br><br>")
    
    # Add explanation
    if question_obj.get('explanation'):
        back_parts.append(f"<b>解析:</b><br>{question_obj['explanation']}")
    
    back = ''.join(back_parts)
    
    return (front, back, tags)


def convert_to_anki_txt(md_file_path, output_path=None):
    """
    Convert a translated markdown file to Anki-compatible TXT format.
    
    Args:
        md_file_path: Path to the markdown file (*_CN.md)
        output_path: Optional custom output path. If None, generates *_CN_anki.txt
        
    Returns:
        Output file path if successful, None if failed
    """
    try:
        # Read markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse questions
        questions = parse_translated_markdown(content)
        
        if not questions:
            raise ValueError("No valid questions found in the markdown file")
        
        # Generate tags from filename
        filename = os.path.basename(md_file_path)
        # Extract useful parts from filename (e.g., Analysis_Topic_Chapter_1_20251120_CN.md)
        # Remove _CN.md suffix and use parts as tags
        name_parts = filename.replace('_CN.md', '').split('_')
        tags = ' '.join([part for part in name_parts if part and not part.isdigit()])
        
        # Determine output path
        if output_path is None:
            base, _ = os.path.splitext(md_file_path)
            # Remove _CN suffix if present
            if base.endswith('_CN'):
                base = base[:-3]
            output_path = f"{base}_CN_anki.txt"
        
        # Write Anki TXT file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write file headers for Anki 2.1.54+
            f.write("#separator:tab\n")
            f.write("#html:true\n")
            f.write("#notetype:Basic\n")
            f.write("#tags column:3\n")
            f.write("\n")
            
            # Write each flashcard
            for q in questions:
                front, back, card_tags = create_anki_flashcard(q, tags)
                
                # Escape tabs and newlines within fields (shouldn't be any, but just in case)
                front = front.replace('\t', ' ').replace('\n', '<br>')
                back = back.replace('\t', ' ').replace('\n', '<br>')
                
                # Write tab-delimited line: Front\tBack\tTags
                f.write(f"{front}\t{back}\t{card_tags}\n")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to convert {md_file_path}: {str(e)}")


def batch_convert_to_anki(file_paths):
    """
    Batch convert multiple markdown files to Anki format.
    
    Args:
        file_paths: List of markdown file paths
        
    Returns:
        Dictionary with 'success' and 'failed' lists containing tuples of (input_path, output_path/error)
    """
    results = {'success': [], 'failed': []}
    
    for file_path in file_paths:
        try:
            output_path = convert_to_anki_txt(file_path)
            results['success'].append((file_path, output_path))
        except Exception as e:
            results['failed'].append((file_path, str(e)))
    
    return results
