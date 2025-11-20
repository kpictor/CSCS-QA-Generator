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
You are a Lead CSCS Exam Writer. Your goal is to create "Gold Standard" exam questions that test true competency, not just memorization.

**Your Task:**
Generate exactly {len(key_terms)} multiple-choice questions.
ONE question for EACH of the following Key Terms:
{terms_list}

{scenario_context}

{instruction}

**Source Material:**
Use the provided text content. If the text is insufficient, apply standard NSCA/CSCS principles.

**Chain of Thought (Perform this internally for each question):**
1. **Define:** Briefly recall the definition of the Key Term.
2. **Contextualize:** How does this term apply to the {scenario_context.splitlines()[1]}?
3. **Complicate:** What is a common misconception or a conflicting factor for this athlete?
4. **Draft:** Create the question and the correct answer.
5. **Distract:** Create 2 wrong answers that *look* correct to an untrained person (plausible distractors).

**Output Format (Strictly follow this for parsing):**
**Key Term: [Term Name]**
Question: [Your high-quality question text]
A. [Option A]
B. [Option B]
C. [Option C]
Correct Answer: [Option Letter]
Explanation: [Provide a detailed explanation. 1. Why the correct answer is right (referencing the text/principles). 2. Why the distractors are wrong/less optimal for this specific athlete.]
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

def translate_and_reorganize(content, provider, model_name, api_key, prompt_template):
    """
    Translates content using the provided prompt template.
    """
    # The prompt template expects {content} to be present
    try:
        final_prompt = prompt_template.format(content=content)
    except KeyError:
        # Fallback if user messed up the template, just append content
        final_prompt = f"{prompt_template}\n\n{content}"
        
    return ai_models.generate_qa(provider, model_name, api_key, final_prompt)

