import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from . import qa_generator
from . import content_orchestrator
from . import config_manager

class App(tk.Tk):
    def __init__(self, content_orchestrator_instance, config_manager_instance):
        super().__init__()

        self.title("CSCS Q&A Generator")
        self.geometry("800x600")
        self.content_orchestrator = content_orchestrator_instance
        self.config_manager = config_manager_instance

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        config_frame.columnconfigure(1, weight=1)

        # Provider Selection
        ttk.Label(config_frame, text="AI Provider:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.provider_var = tk.StringVar(value="Gemini") # Default provider
        self.provider_menu = ttk.Combobox(
            config_frame,
            textvariable=self.provider_var,
            values=["Gemini", "OpenAI"],
            state="readonly"
        )
        self.provider_menu.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        self.provider_menu.bind("<<ComboboxSelected>>", self.on_provider_select)

        # API Key Input
        self.api_key_label = ttk.Label(config_frame, text="API Key:")
        self.api_key_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show='*')
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        # Validation
        self.validate_button = ttk.Button(config_frame, text="Validate Key", command=self.validate_api_key)
        self.validate_button.grid(row=1, column=2, padx=5, pady=2)
        self.validation_status_label = ttk.Label(config_frame, text="", font=("Arial", 10, "bold"))
        self.validation_status_label.grid(row=1, column=3, padx=5, pady=2)

        # --- Generation Controls ---
        gen_controls_frame = ttk.LabelFrame(main_frame, text="Generation Controls", padding="10")
        gen_controls_frame.pack(fill=tk.X, pady=5)
        gen_controls_frame.columnconfigure(1, weight=1)

        # AI Model Selection
        ttk.Label(gen_controls_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ai_model_var = tk.StringVar()
        self.ai_model_menu = ttk.Combobox(
            gen_controls_frame,
            textvariable=self.ai_model_var,
            state="disabled"
        )
        self.ai_model_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.ai_model_menu.bind("<<ComboboxSelected>>", self.on_model_select)

        # Domain & Level
        ttk.Label(gen_controls_frame, text="Exam Outline:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        self.domain_tree_frame = self._create_domain_treeview(gen_controls_frame)
        self.domain_tree_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        gen_controls_frame.rowconfigure(1, weight=1) # Allow the treeview to expand vertically

        ttk.Label(gen_controls_frame, text="Cognitive Level:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.level_var = tk.StringVar(value="Recall")
        self.level_menu = ttk.Combobox(gen_controls_frame, textvariable=self.level_var, values=["Recall", "Application", "Analysis"], state="readonly")
        self.level_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # --- Action Buttons Frame ---
        action_buttons_frame = ttk.Frame(main_frame)
        action_buttons_frame.pack(fill=tk.X, pady=5)
        action_buttons_frame.columnconfigure(0, weight=1)
        action_buttons_frame.columnconfigure(1, weight=1)

        self.generate_button = ttk.Button(action_buttons_frame, text="Generate Prompt", command=self.generate_and_display_prompt, state=tk.DISABLED)
        self.generate_button.grid(row=0, column=0, sticky=tk.EW, padx=(0, 2))

        self.send_button = ttk.Button(action_buttons_frame, text="Send to AI", command=self.send_prompt_to_ai, state=tk.DISABLED)
        self.send_button.grid(row=0, column=1, sticky=tk.EW, padx=(2, 0))

        # --- Prompt Frame ---
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, width=80, height=10)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        # --- Output Frame ---
        output_frame = ttk.LabelFrame(main_frame, text="Generated Q&A", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.on_provider_select() # Initial setup

    def _create_domain_treeview(self, parent):
        """Creates and populates the Treeview for the exam outline."""
        tree_frame = ttk.Frame(parent)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.domain_tree = ttk.Treeview(tree_frame, height=7)
        self.domain_tree.heading("#0", text="Domain/Topic", anchor=tk.W)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.domain_tree.yview)
        self.domain_tree.configure(yscrollcommand=scrollbar.set)
        
        self.domain_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Populate the tree from the dynamically loaded outline
        outline = self.content_orchestrator.detailed_outline

        for section_name, section_data in outline.items():
            section_id = self.domain_tree.insert("", "end", text=section_data['header'], open=True)
            
            if 'domains' not in section_data: continue

            for domain_name, domain_data in section_data['domains'].items():
                domain_id = self.domain_tree.insert(section_id, "end", text=domain_data['header'], open=True)
                
                if 'subdomains' not in domain_data: continue

                for subdomain_name, tasks in domain_data['subdomains'].items():
                    subdomain_id = self.domain_tree.insert(domain_id, "end", text=subdomain_name, open=False)
                    if isinstance(tasks, list):
                        for task in tasks:
                            self.domain_tree.insert(subdomain_id, "end", text=task)

        return tree_frame

    def on_provider_select(self, event=None):
        """Handles provider selection change."""
        provider = self.provider_var.get()
        key_name = f"{provider.upper()}_API_KEY"
        self.api_key_var.set(self.config_manager.get(key_name, ""))
        self.validation_status_label.config(text="")
        self.ai_model_menu.set('')
        self.ai_model_menu.config(state="disabled")
        self.generate_button.config(state="disabled")
        self.send_button.config(state="disabled")

    def validate_api_key(self):
        """Validates the key and fetches models."""
        provider = self.provider_var.get()
        api_key = self.api_key_var.get()
        if not api_key:
            messagebox.showwarning("Input Error", "Please enter an API key.")
            return

        self.validation_status_label.config(text="Validating...", foreground="orange")
        self.update_idletasks()

        models = qa_generator.validate_and_fetch_models(provider, api_key)

        if models:
            self.validation_status_label.config(text="Validated ✔", foreground="green")
            self.config_manager.set(f"{provider.upper()}_API_KEY", api_key)
            self.config_manager.save()
            
            self.ai_model_menu['values'] = models
            self.ai_model_menu.config(state="readonly")
            
            last_used_model = self.config_manager.get(f"LAST_USED_{provider.upper()}_MODEL")
            if last_used_model in models:
                self.ai_model_menu.set(last_used_model)
            else:
                self.ai_model_menu.current(0)
            self.generate_button.config(state="normal")
            self.send_button.config(state="normal")
        else:
            self.validation_status_label.config(text="Invalid ✖", foreground="red")
            self.ai_model_menu.set('')
            self.ai_model_menu.config(state="disabled")
            self.generate_button.config(state="disabled")
            self.send_button.config(state="disabled")

    def on_model_select(self, event=None):
        """Saves the selected model to config."""
        provider = self.provider_var.get()
        model_name = self.ai_model_var.get()
        self.config_manager.set(f"LAST_USED_{provider.upper()}_MODEL", model_name)
        self.config_manager.save()

    def generate_and_display_prompt(self):
        """Generates the prompt and displays it in the prompt text area."""
        selected_item = self.domain_tree.focus()
        if not selected_item:
            messagebox.showwarning("Input Error", "Please select a topic from the Exam Outline.")
            return
        
        topic_path_cleaned = []
        current_item = selected_item
        while current_item:
            text = self.domain_tree.item(current_item, "text")
            cleaned_text = text.split('(')[0].strip()
            topic_path_cleaned.insert(0, cleaned_text)
            current_item = self.domain_tree.parent(current_item)
        
        domain_key = topic_path_cleaned[1] if len(topic_path_cleaned) > 1 else topic_path_cleaned[0]

        refined_content = self.content_orchestrator.get_refined_content(topic_path_cleaned)
        example_questions = self.content_orchestrator.get_example_questions_for_domain(domain_key)

        prompt = qa_generator.generate_prompt(
            " / ".join(topic_path_cleaned), 
            self.level_var.get(), 
            refined_content,
            example_questions
        )
        
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, prompt)

    def send_prompt_to_ai(self):
        """Sends the prompt from the text area to the AI and displays the result."""
        provider = self.provider_var.get()
        api_key = self.config_manager.get(f"{provider.upper()}_API_KEY")
        model_name = self.ai_model_var.get()
        
        if not all([provider, api_key, model_name]):
            messagebox.showerror("Error", "Configuration is incomplete. Please validate your key and select a model.")
            return

        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Input Error", "Prompt is empty. Please generate a prompt first.")
            return

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Sending prompt to {model_name}... Please wait.\n\n")
        self.update_idletasks()

        try:
            generated_qa = qa_generator.generate_qa_with_ai(provider, model_name, api_key, prompt)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, generated_qa)
        except Exception as e:
            messagebox.showerror("Generation Error", f"An error occurred: {e}")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"An error occurred: {e}")
