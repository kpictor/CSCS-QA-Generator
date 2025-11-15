from . import ai_models

def generate_prompt(domain, level, content, example_questions=None):
    """Generates a prompt for the AI model, including few-shot examples if available."""
    
    example_section = ""
    if example_questions:
        formatted_examples = "\n\n".join(example_questions)
        example_section = f"""
    **Example Q&A:**
    ---
    {formatted_examples}
    ---
    """

    prompt = f"""
    Based on the following content from the CSCS study guide, please generate ONE new, original high-quality multiple-choice question.

    **Exam Domain:** {domain}
    **Cognitive Level:** {level}

    **Instructions:**
    1. The question must be original and not a copy of the examples.
    2. The question should accurately reflect the provided content.
    3. The cognitive level must match the selection ({level}).
       - **Recall:** Simple recognition of facts (e.g., "Which of the following...").
       - **Application:** Applying knowledge to a practical situation (e.g., "An athlete is... What should...").
       - **Analysis:** Evaluating multiple pieces of information to make a decision (e.g., "Given the following data... which is the MOST important...").
    4. Provide three plausible but distinct answer choices (a, b, c).
    5. Indicate the correct answer clearly on a new line, like: "Correct Answer: a".
    6. Ensure the generated question is different from the examples provided below.
    {example_section}
    **Content to Use for New Question:**
    ---
    {content}
    ---

    **Generated Q&A:**
    """
    return prompt

def validate_and_fetch_models(provider, api_key):
    """Validates the API key and fetches models for the provider."""
    return ai_models.validate_and_fetch_models(provider, api_key)

def generate_qa_with_ai(provider, model_name, api_key, prompt):
    """Generates Q&A using the specified AI model."""
    return ai_models.generate_qa(provider, model_name, api_key, prompt)