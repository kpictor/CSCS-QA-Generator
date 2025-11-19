import fitz  # PyMuPDF
import os
import re
import json

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def clean_text(text):
    """Cleans the extracted text by removing headers, footers, and page numbers."""
    # Remove headers (e.g., CHAPTER 10)
    text = re.sub(r'CHAPTER\s*\d+\s*', '', text)
    # Remove footers
    text = re.sub(r'Essentials of Strength Training and Conditioning', '', text)
    # Remove page numbers
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove lines with just a number
    text = re.sub(r'\n\d+\n', '\n', text)
    # Remove extra whitespace
    text = re.sub(r'\s*\n\s*', '\n', text)
    return text.strip()

def structure_text(text):
    """Structures the text into a list of sections with headings and content."""
    # This is a simple heuristic-based approach and might need refinement.
    # It assumes that headings are short lines that don't end with a period.
    lines = text.split('\n')
    structured_content = []
    current_heading = "Introduction"
    current_content = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Simple heuristic for a heading: short line, no period at the end, maybe title case
        if len(line.split()) < 8 and not line.endswith('.') and line[0].isupper():
            if current_content:
                structured_content.append({"heading": current_heading, "content": current_content.strip()})
            current_heading = line
            current_content = ""
        else:
            current_content += " " + line
    
    # Add the last section
    if current_content:
        structured_content.append({"heading": current_heading, "content": current_content.strip()})

    return structured_content

def main():
    """Main function to process all PDFs."""
    # content is in data/pdfs (root/data/pdfs)
    # script is in src/data_processing
    # so we need to go up two levels to get to root
    pdf_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'pdfs'))
    
    # output should be in src/processed_chapters
    # so we need to go up one level from src/data_processing
    output_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'processed_chapters'))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processing {pdf_path}...")
            
            raw_text = extract_text_from_pdf(pdf_path)
            if not raw_text:
                continue

            cleaned_text = clean_text(raw_text)
            structured_data = structure_text(cleaned_text)

            if structured_data:
                json_filename = os.path.splitext(filename)[0] + '.json'
                json_path = os.path.join(output_directory, json_filename)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=4, ensure_ascii=False)
                print(f"Successfully processed and saved to {json_path}")
            else:
                print(f"Could not structure text for {filename}")
            print("-" * 20)

if __name__ == "__main__":
    main()
