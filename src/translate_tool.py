import os
import sys
import argparse
from .api import ai_models
from .utils import config_manager

# --- EDITABLE PROMPT HERE ---
# You can modify the instructions below to change how the translation and reorganization is performed.
TRANSLATION_PROMPT_TEMPLATE = """
You are an expert translator and educational content editor specializing in Strength and Conditioning (CSCS).

**Your Task:**
1. **Translate** the following Q&A content into **Simplified Chinese (简体中文)**.
2. **Reorganize** the layout to make it highly readable and professional.
3. **Terminology:** Ensure accurate translation of technical CSCS terms (e.g., "Stretch-Shortening Cycle" -> "牵拉-缩短周期", "Hypertrophy" -> "肌肥大", "Rate of Force Development" -> "发力率").

**Desired Output Format (for each question):**
## 关键术语: [English Term] ([Chinese Term])
**问题:** [Translated Question]
A. [Translated Option A]
B. [Translated Option B]
C. [Translated Option C]

**正确答案:** [Option]
**解析:**
[Translated Explanation]
---

**Source Content:**
{content}
"""
# ----------------------------

def translate_content(content, provider, model_name, api_key):
    """
    Translates content using the defined prompt and specified AI provider.
    """
    prompt = TRANSLATION_PROMPT_TEMPLATE.format(content=content)
    return ai_models.generate_qa(provider, model_name, api_key, prompt)

def main():
    parser = argparse.ArgumentParser(description="Translate CSCS Q&A files to Simplified Chinese.")
    parser.add_argument("input_file", help="Path to the markdown file to translate.")
    parser.add_argument("--provider", default="Gemini", choices=["Gemini", "OpenAI", "Qwen", "Claude"], help="AI Provider to use.")
    parser.add_argument("--model", help="Specific model name (optional).")
    parser.add_argument("--api_key", help="API Key (optional, will try to load from config if not provided).")
    
    args = parser.parse_args()
    
    # Load Config if API Key not provided
    if not args.api_key:
        # Try to find config relative to this script
        # Assuming this script is in src/
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        cm = config_manager.ConfigManager(project_root)
        api_key = cm.get(f"{args.provider.upper()}_API_KEY")
        
        if not api_key:
            print(f"Error: No API Key provided and none found in config for {args.provider}.")
            sys.exit(1)

    # Validate/Fetch Model if not provided
    if not args.model:
        print(f"Fetching available models for {args.provider}...")
        models = ai_models.validate_and_fetch_models(args.provider, api_key)
        if not models:
            print("Error: Could not fetch models. Check your API Key.")
            sys.exit(1)
        args.model = models[0]
        print(f"Using default model: {args.model}")

    # Read Input
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {args.input_file} not found.")
        sys.exit(1)

    print(f"Translating {args.input_file} using {args.provider} ({args.model})...")
    
    # Translate
    translated_text = translate_content(content, args.provider, args.model, api_key)
    
    # Save Output
    base, ext = os.path.splitext(args.input_file)
    output_path = f"{base}_CN{ext}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)
        
    print(f"Success! Translated file saved to: {output_path}")

if __name__ == "__main__":
    main()
