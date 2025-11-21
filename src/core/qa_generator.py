from ..api import ai_models
from .scenario_generator import ScenarioGenerator

def generate_batch_prompt(key_terms, content, example_questions=None, cognitive_level="Recall"):
    """
    Generates a prompt to create questions for a specific list of Key Terms, 
    tailored to a specific Cognitive Level, with Scenario Injection and Chain-of-Thought.
    """
    
    # 1. Generate a Random Scenario for Context (Vital for Application/Analysis)
    scenario_gen = ScenarioGenerator()
    scenario_context = scenario_gen.generate_profile()
    
    # 2. Cognitive Level Definitions & Logic
    if cognitive_level == "Recall":
        instruction = """
        **Cognitive Level: Recall (Level 1)**
        - **Goal:** Test specific knowledge of facts, definitions, or standard procedures.
        - **Style:** Direct questions ("What is...", "Which of the following...").
        - **Context:** You may ignore the specific athlete scenario if it complicates a simple definition, but prefer using it to frame the question if possible (e.g., "For this athlete, which muscle is...").
        """
    elif cognitive_level == "Application":
        instruction = f"""
        **Cognitive Level: Application (Level 2)**
        - **Goal:** Apply knowledge to a specific situation.
        - **Style:** "If, Then" scenarios. Calculations. interpretations.
        - **Context:** **MANDATORY.** You MUST use the provided 'Scenario Context' (Athlete Profile) to frame the questions.
        - **Requirement:** Connect the 'Key Term' to the 'Athlete's Goal' or 'Training Phase'.
        """
    else: # Analysis
        instruction = f"""
        **Cognitive Level: Analysis (Level 3 - Highest Complexity)**
        - **Goal:** Evaluate multiple variables, synthesize information, and determine the *best* course of action among plausible alternatives.
        - **Style:** Complex scenarios with competing factors (e.g., fatigue vs. intensity, age vs. volume).
        - **Context:** **MANDATORY.** Use the 'Scenario Context'. 
        - **Requirement:** The correct answer should not be obvious. It requires weighing the Athlete's Status against the Goal and the Key Term's physiological/mechanical implications.
        """

    example_section = ""
    if example_questions:
        formatted_examples = "\n\n".join(example_questions[:2])
        example_section = f"### Style Reference (Do not copy, just match tone):\n{formatted_examples}"

    terms_list = "\n".join([f"- {term}" for term in key_terms])

    prompt = f"""
You are a Lead CSCS Exam Writer for the NSCA. Your goal is to create "Gold Standard" exam questions that test true competency, not just memorization.

**Your Task:**
Generate exactly {len(key_terms)} multiple-choice questions.
ONE question for EACH of the following Key Terms:
{terms_list}

{scenario_context}

{instruction}

**Source Material:**
Use the provided text content below. If the text is insufficient, apply standard NSCA/CSCS principles and established exercise science research.

**Chain of Thought (Perform this internally for each question):**
1. **Define:** Briefly recall the definition of the Key Term and its physiological/biomechanical basis.
2. **Contextualize:** How does this term apply to the {scenario_context.splitlines()[1] if scenario_context else 'athlete scenario'}?
3. **Complicate:** What is a common misconception, conflicting factor, or nuanced application for this scenario?
4. **Draft:** Create the question stem and the correct answer.
5. **Distract:** Create 2 plausible but incorrect distractors.

**Distractor Quality Guidelines (CRITICAL):**
Your distractors must be plausible to someone with partial knowledge. Good distractors:
- Mix up similar concepts (e.g., "Type I fibers" vs "Type IIx fibers" in a power question)
- Use partially correct logic (e.g., correct principle applied to wrong population)
- Reflect common student misconceptions from CSCS prep
- Are quantitatively similar but qualitatively wrong (e.g., "85% 1RM" vs "70% 1RM" for different goals)

**Output Format (Strictly follow this for parsing):**
**Key Term: [Term Name]**
Question: [Your high-quality question text]
A. [Option A]
B. [Option B]
C. [Option C]
Correct Answer: [A, B, or C - LETTER ONLY]
Explanation: [Provide a comprehensive explanation:
1. WHY the correct answer is optimal (cite NSCA principle, textbook concept, or research basis)
2. WHY each distractor is incorrect or suboptimal for THIS specific athlete/scenario
3. Include quantitative reasoning where applicable (e.g., "because power requires 30-60% 1RM, not 85%")]
---

**Quality Self-Check (Complete before finalizing each question):**
Before outputting, verify:
☑ Question clearly tests the specified Key Term
☑ Scenario details are actually relevant to the answer (not just decoration)
☑ Correct answer is defensible via NSCA guidelines or established research
☑ Distractors could fool someone with incomplete knowledge
☑ Explanation cites specific principles or research (not vague generalities)

{example_section}

### Source Text Content:
{content}
"""
    return prompt

def validate_and_fetch_models(provider, api_key):
    """Validates the API key and fetches models for the provider."""
    return ai_models.validate_and_fetch_models(provider, api_key)

def generate_qa_with_ai(provider, model_name, api_key, prompt):
    """Generates Q&A using the specified AI model."""
    return ai_models.generate_qa(provider, model_name, api_key, prompt)

def _split_content_into_chunks(content, max_chunk_size=15000):
    """
    Splits content into chunks by markdown sections to avoid breaking questions.
    Attempts to split at section boundaries (## headers or --- separators).
    
    Args:
        content: The full content to split
        max_chunk_size: Maximum characters per chunk (default ~25k chars = ~6k tokens)
    
    Returns:
        List of content chunks
    """
    import re
    
    # If content is small enough, return as-is
    if len(content) <= max_chunk_size:
        return [content]
    
    # Split by markdown headers or horizontal rules
    # Pattern matches: lines starting with ## or lines that are ---
    split_pattern = r'(?=^#{2,}\s+.*$|^---+$)'
    sections = re.split(split_pattern, content, flags=re.MULTILINE)
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        if not section.strip():
            continue
            
        # If adding this section would exceed limit, save current chunk and start new one
        if len(current_chunk) + len(section) > max_chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = section
        else:
            current_chunk += section
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    # If we still have chunks that are too large, split them by character count
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chunk_size:
            final_chunks.append(chunk)
        else:
            # Force split by character count as last resort
            for i in range(0, len(chunk), max_chunk_size):
                final_chunks.append(chunk[i:i + max_chunk_size])
    
    return final_chunks


def translate_and_reorganize(content, provider, model_name, api_key, prompt_template, progress_callback=None):
    """
    Translates content using the provided prompt template.
    For large files, splits into chunks and processes separately.
    
    Args:
        content: Content to translate
        provider: AI provider name
        model_name: Model to use
        api_key: API key
        prompt_template: Translation prompt template
        progress_callback: Optional callback function(current, total, message) for progress updates
    
    Returns:
        Translated content
    """
    # Determine if we need chunking (files > 20KB)
    file_size_kb = len(content.encode('utf-8')) / 1024
    
    if file_size_kb < 20:
        # Small file - translate normally
        try:
            final_prompt = prompt_template.format(content=content)
        except KeyError:
            final_prompt = f"{prompt_template}\n\n{content}"
        
        if progress_callback:
            progress_callback(1, 1, "Translating...")
        
        return ai_models.generate_qa(provider, model_name, api_key, final_prompt)
    
    # Large file - use chunking
    chunks = _split_content_into_chunks(content)
    total_chunks = len(chunks)
    translated_chunks = []
    
    if progress_callback:
        progress_callback(0, total_chunks, f"Processing large file ({file_size_kb:.1f}KB) in {total_chunks} chunks...")
    
    for i, chunk in enumerate(chunks, 1):
        max_retries = 5
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Format prompt for this chunk
                try:
                    final_prompt = prompt_template.format(content=chunk)
                except KeyError:
                    final_prompt = f"{prompt_template}\n\n{chunk}"
                
                if progress_callback:
                    retry_msg = f" (retry {retry_count}/{max_retries})" if retry_count > 0 else ""
                    progress_callback(i, total_chunks, f"Translating chunk {i}/{total_chunks}{retry_msg}...")
                
                # Translate this chunk
                translated_chunk = ai_models.generate_qa(provider, model_name, api_key, final_prompt)
                
                # Check for error in response
                if translated_chunk.startswith("Error during generation"):
                    raise Exception(translated_chunk)
                
                translated_chunks.append(translated_chunk)
                
                # Add delay between chunks to avoid rate limiting (skip delay after last chunk)
                if i < total_chunks:
                    import time
                    time.sleep(5)
                
                break  # Success - exit retry loop
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                if retry_count < max_retries:
                    # Wait before retrying (exponential backoff: 5s, 10s, 20s, 40s, 80s)
                    import time
                    wait_time = 5 * (2 ** retry_count)
                    if progress_callback:
                        progress_callback(i, total_chunks, f"Chunk {i}/{total_chunks} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # All retries exhausted
                    error_msg = f"Failed on chunk {i}/{total_chunks} after {max_retries} retries: {str(last_error)}"
                    if progress_callback:
                        progress_callback(i, total_chunks, error_msg)
                    raise Exception(error_msg)
    
    # Reassemble all chunks
    if progress_callback:
        progress_callback(total_chunks, total_chunks, "Reassembling translated content...")
    
    # Join chunks with double newline to maintain separation
    return "\n\n".join(translated_chunks)

