import google.generativeai as genai
from openai import OpenAI
import dashscope
import anthropic

def validate_and_fetch_models(provider, api_key):
    """Validates the API key and fetches available models for the provider."""
    try:
        if provider == "Gemini":
            genai.configure(api_key=api_key)
            # Filter for models that support content generation
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Clean up the model names
            return sorted([model.replace("models/", "") for model in models])
        
        elif provider == "OpenAI":
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            # Return a sorted list of model IDs
            return sorted([model.id for model in models.data])

        elif provider == "Qwen":
            dashscope.api_key = api_key
            models = dashscope.Model.list()
            return sorted([model['id'] for model in models['data']])

        elif provider == "Claude":
            client = anthropic.Anthropic(api_key=api_key)
            # Placeholder for fetching models, as the Claude API does not have a standard list_models function.
            # A predefined list of common models is returned instead.
            return sorted([
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0",
                "claude-instant-1.2"
            ])
            
    except Exception as e:
        print(f"API key validation failed for {provider}: {e}")
        return None

def generate_qa(provider, model_name, api_key, prompt):
    """Generates Q&A using the specified provider and model."""
    try:
        if provider == "Gemini":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text

        elif provider == "OpenAI":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates multiple-choice questions based on provided text."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        elif provider == "Qwen":
            dashscope.api_key = api_key
            response = dashscope.Generation.call(
                model=model_name,
                prompt=prompt
            )
            return response.output['text']

        elif provider == "Claude":
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return message.content[0].text

    except Exception as e:
        return f"Error during generation with {model_name}: {e}"
