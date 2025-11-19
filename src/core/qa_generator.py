from ..api import ai_models

def generate_batch_prompt(key_terms, content, example_questions=None, cognitive_level="Recall"):
    """
    Generates a prompt to create questions for a specific list of Key Terms, 
    tailored to a specific Cognitive Level.
    """
    
    # Cognitive Level Definitions
    level_instructions = {
        "Recall": """
        **Cognitive Level: Recall**
        - Focus on recognizing facts, concepts, principles, or procedures.
        - Questions should ask "What is X?" or identifying definitions.
        - Avoid complex scenarios. Stick to direct knowledge retrieval.
        """,
        "Application": """
        **Cognitive Level: Application**
        - Focus on applying knowledge to specific situations.
        - Use "If, Then" scenarios.
        - Include basic calculations or identifying relationships between concepts.
        - Example: "If an athlete has X heart rate, what is their training zone?"
        """,
        "Analysis": """
        **Cognitive Level: Analysis**
        - Focus on evaluating multiple variables to determine the best course of action.
        - Use complex scenarios involving athlete profiles (age, sport, training status, test results).
        - Require the test-taker to synthesize information (e.g., identifying the weakest link in a performance profile).
        """
    }
    
    selected_instruction = level_instructions.get(cognitive_level, level_instructions["Recall"])

    example_section = ""
    if example_questions:
        # Limit examples to first 3 to save tokens but give flavor
        formatted_examples = "\n\n".join(example_questions[:3])
        example_section = f"""
### Example Questions (Reference for Style only, stick to the requested Cognitive Level):
{formatted_examples}
"""

    terms_list = "\n".join([f"- {term}" for term in key_terms])

    prompt = f"""
You are an expert CSCS (Certified Strength and Conditioning Specialist) exam question writer.

**Your Task:**
Generate exactly {len(key_terms)} multiple-choice questions.
You must generate ONE question for EACH of the following Key Terms:
{terms_list}

{selected_instruction}

**Source Material:**
Use strictly the text content provided below to derive the questions.

**Format Requirements:**
1. **Question:** Clear, professional, CSCS-style. Adhere strictly to the **{cognitive_level}** level defined above.
2. **Options:** Provide 3 plausible options (A, B, C).
3. **Correct Answer:** Clearly state the correct option.
4. **Explanation:** Briefly explain why the answer is correct based on the text.
5. **Output Format:**
   **Key Term: [Term Name]**
   Question: ...
   A. ...
   B. ...
   C. ...
   Correct Answer: ...
   Explanation: ...
   (Separator) ---

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

