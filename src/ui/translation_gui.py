import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from ..core import qa_generator
from ..utils import config_manager
import os
import sys

DEFAULT_PROMPT = """
You are an expert translator and educational content editor specializing in Strength and Conditioning (CSCS).

**Your Task:**
1. **Translate** the following Q&A content into **Simplified Chinese (简体中文)**.
2. **Reorganize** the layout to make it highly readable and professional.
3. **Terminology:** Ensure accurate translation of technical CSCS terms (e.g., "Stretch-Shortening Cycle" -> "牵拉-缩短周期", "Hypertrophy" -> "肌肥大").

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

class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSCS Translator Tool")
        self.geometry("900x850")
        
        # Load Config
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_path = os.path.join(project_root, 'config.json')
        self.config_manager = config_manager.ConfigManager(config_path)

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- File Selection ---
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=70).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=5)

        # --- Configuration ---
        config_frame = ttk.LabelFrame(main_frame, text="AI Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Provider:").grid(row=0, column=0, padx=5)
        self.provider_var = tk.StringVar(value="Gemini")
        self.provider_menu = ttk.Combobox(config_frame, textvariable=self.provider_var, values=["Gemini", "OpenAI", "Qwen", "Claude"], state="readonly")
        self.provider_menu.grid(row=0, column=1, padx=5)
        self.provider_menu.bind("<<ComboboxSelected>>", self.on_provider_select)

        ttk.Label(config_frame, text="API Key:").grid(row=0, column=2, padx=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show='*', width=25)
        self.api_key_entry.grid(row=0, column=3, padx=5)

        ttk.Label(config_frame, text="Model:").grid(row=0, column=4, padx=5)
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(config_frame, textvariable=self.model_var, state="disabled", width=25)
        self.model_menu.grid(row=0, column=5, padx=5)

        ttk.Button(config_frame, text="Validate Key", command=self.validate_key).grid(row=0, column=6, padx=10)
        
        # --- Prompt Editor ---
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt Editor (Template)", padding="10")
        prompt_frame.pack(fill=tk.X, pady=5)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=10)
        self.prompt_text.pack(fill=tk.X, expand=True)
        self.prompt_text.insert(tk.END, DEFAULT_PROMPT)

        # --- Actions ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X)
        self.run_btn = ttk.Button(action_frame, text="Translate & Reorganize to Chinese", command=self.run_translation, state=tk.DISABLED)
        self.run_btn.pack(fill=tk.X, pady=5)

        # --- Output ---
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Init
        self.on_provider_select()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")])
        if path:
            self.file_path_var.set(path)

    def on_provider_select(self, event=None):
        provider = self.provider_var.get()
        key = self.config_manager.get(f"{provider.upper()}_API_KEY", "")
        self.api_key_var.set(key)
        self.model_menu.set('')
        self.model_menu.config(state="disabled")
        self.run_btn.config(state="disabled")

    def validate_key(self):
        provider = self.provider_var.get()
        api_key = self.api_key_var.get()
        if not api_key:
            messagebox.showerror("Error", "API Key is required.")
            return

        models = qa_generator.validate_and_fetch_models(provider, api_key)
        if models:
            self.model_menu['values'] = models
            self.model_menu.config(state="readonly")
            if models: self.model_menu.set(models[0])
            self.run_btn.config(state="normal")
            messagebox.showinfo("Success", "API Key Validated!")
        else:
            messagebox.showerror("Error", "Invalid API Key.")

    def run_translation(self):
        file_path = self.file_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Invalid File Path.")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return

        provider = self.provider_var.get()
        model = self.model_var.get()
        api_key = self.api_key_var.get()
        
        # Get Custom Prompt
        custom_prompt = self.prompt_text.get("1.0", tk.END).strip()

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Translating... Please wait.\n")
        self.update()

        try:
            translated_text = qa_generator.translate_and_reorganize(content, provider, model, api_key, custom_prompt)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated_text)
            
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_CN{ext}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            
            messagebox.showinfo("Success", f"Saved to:\n{output_path}")
            
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError: {e}")

if __name__ == "__main__":
    try:
        print("Initializing Translation App...")
        app = TranslationApp()
        print("App initialized. Starting mainloop...")
        app.mainloop()
    except Exception as e:
        import traceback
        print("CRITICAL ERROR:")
        traceback.print_exc()
        input("Press Enter to exit...")
