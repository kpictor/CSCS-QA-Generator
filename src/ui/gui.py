import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ..core import qa_generator
from ..core import content_orchestrator
from ..utils import config_manager
import os
from datetime import datetime
import threading

class App(tk.Tk):
    def __init__(self, content_orchestrator_instance, config_manager_instance):
        super().__init__()

        self.title("CSCS Q&A Generator")
        self.geometry("1000x800")
        self.content_orchestrator = content_orchestrator_instance
        self.config_manager = config_manager_instance

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        config_frame.columnconfigure(1, weight=1)

        ttk.Label(config_frame, text="AI Provider:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.provider_var = tk.StringVar(value="Gemini")
        self.provider_menu = ttk.Combobox(config_frame, textvariable=self.provider_var, values=["Gemini", "OpenAI", "Qwen", "Claude"], state="readonly")
        self.provider_menu.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        self.provider_menu.bind("<<ComboboxSelected>>", self.on_provider_select)

        self.api_key_label = ttk.Label(config_frame, text="API Key:")
        self.api_key_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show='*')
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        self.validate_button = ttk.Button(config_frame, text="Validate Key", command=self.validate_api_key)
        self.validate_button.grid(row=1, column=2, padx=5, pady=2)
        self.validation_status_label = ttk.Label(config_frame, text="", font=("Arial", 10, "bold"))
        self.validation_status_label.grid(row=1, column=3, padx=5, pady=2)

        # --- Generation Controls Frame ---
        gen_controls_frame = ttk.LabelFrame(main_frame, text="Generation Controls", padding="10")
        gen_controls_frame.pack(fill=tk.X, pady=5)
        gen_controls_frame.columnconfigure(1, weight=1)

        ttk.Label(gen_controls_frame, text="Select Model:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ai_model_var = tk.StringVar()
        self.ai_model_menu = ttk.Combobox(gen_controls_frame, textvariable=self.ai_model_var, state="disabled")
        self.ai_model_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.ai_model_menu.bind("<<ComboboxSelected>>", self.on_model_select)

        ttk.Label(gen_controls_frame, text="Mode:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.generation_mode_var = tk.StringVar(value="Targeted Practice (Outline)")
        # Prioritize Outline Mode
        self.generation_mode_menu = ttk.Combobox(gen_controls_frame, textvariable=self.generation_mode_var, values=["Targeted Practice (Outline)"], state="readonly")
        self.generation_mode_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.generation_mode_menu.bind("<<ComboboxSelected>>", self.on_generation_mode_select)

        ttk.Label(gen_controls_frame, text="Cognitive Level:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.cognitive_level_var = tk.StringVar(value="Recall")
        self.cognitive_level_menu = ttk.Combobox(gen_controls_frame, textvariable=self.cognitive_level_var, values=["Recall", "Application", "Analysis"], state="readonly")
        self.cognitive_level_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # Dynamic Content Area (Treeview)
        self.dynamic_options_frame = ttk.Frame(gen_controls_frame)
        self.dynamic_options_frame.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        gen_controls_frame.rowconfigure(3, weight=1)
        self.dynamic_options_frame.columnconfigure(0, weight=1)

        self.generate_qa_button = ttk.Button(gen_controls_frame, text="Generate Q&A", command=self.start_qa_generation_thread, state=tk.DISABLED)
        self.generate_qa_button.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.EW)

        # --- Post-Processing Frame (Translation) ---
        pp_frame = ttk.LabelFrame(main_frame, text="Post-Processing (Translation)", padding="10")
        pp_frame.pack(fill=tk.X, pady=5)
        
        # Translation Configuration (Independent of Generation)
        ttk.Label(pp_frame, text="Provider:").grid(row=0, column=0, padx=5, pady=5)
        self.trans_provider_var = tk.StringVar(value="Gemini")
        self.trans_provider_menu = ttk.Combobox(pp_frame, textvariable=self.trans_provider_var, values=["Gemini", "OpenAI", "Qwen", "Claude"], state="readonly", width=10)
        self.trans_provider_menu.grid(row=0, column=1, padx=5, pady=5)
        self.trans_provider_menu.bind("<<ComboboxSelected>>", self.on_trans_provider_select)

        ttk.Label(pp_frame, text="Key:").grid(row=0, column=2, padx=5, pady=5)
        self.trans_api_key_var = tk.StringVar()
        self.trans_api_key_entry = ttk.Entry(pp_frame, textvariable=self.trans_api_key_var, show='*', width=15)
        self.trans_api_key_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(pp_frame, text="Model:").grid(row=0, column=4, padx=5, pady=5)
        self.trans_model_var = tk.StringVar()
        self.trans_model_menu = ttk.Combobox(pp_frame, textvariable=self.trans_model_var, state="disabled", width=20)
        self.trans_model_menu.grid(row=0, column=5, padx=5, pady=5)
        
        # Validate Button for Translation (Small)
        self.trans_validate_btn = ttk.Button(pp_frame, text="✓", width=3, command=self.validate_trans_key)
        self.trans_validate_btn.grid(row=0, column=6, padx=2)

        self.translate_btn = ttk.Button(pp_frame, text="Reorganize & Translate to Chinese", command=self.start_translation_thread, state=tk.DISABLED)
        self.translate_btn.grid(row=0, column=7, padx=10, pady=5, sticky=tk.EW)
        
        pp_frame.columnconfigure(7, weight=1)

        # --- Output Area ---
        output_frame = ttk.LabelFrame(main_frame, text="Generation Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.last_saved_path = None

        # Initialize
        self.on_provider_select()
        self.on_generation_mode_select()
        self.on_trans_provider_select()

    def _create_domain_treeview(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.domain_tree = ttk.Treeview(tree_frame, height=10, columns=("id",), displaycolumns=())
        self.domain_tree.heading("#0", text="Select an Exam Outline Topic", anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.domain_tree.yview)
        self.domain_tree.configure(yscrollcommand=scrollbar.set)
        
        self.domain_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        outline = self.content_orchestrator.get_outline()
        
        for section_name, section_data in outline.items():
            # Section
            sec_id = self.domain_tree.insert("", "end", text=section_data['header'], values=(section_data['id'],), open=True)
            
            for domain_name, domain_data in section_data.get('domains', {}).items():
                # Domain
                dom_id = self.domain_tree.insert(sec_id, "end", text=domain_data['header'], values=(domain_data['id'],), open=False)
                
                for subdomain_name, subdomain_data in domain_data.get('subdomains', {}).items():
                    # Subdomain (This is where the mapping usually lives)
                    sub_id = self.domain_tree.insert(dom_id, "end", text=subdomain_data['header'], values=(subdomain_data['id'],), open=False)
                    
                    # Tasks (Optional, but good for context)
                    for task in subdomain_data.get('tasks', []):
                         # Extract Task Number from string (e.g., "1. Muscle anatomy...")
                         try:
                             task_num = task.split('.')[0].strip()
                             task_id = f"{subdomain_data['id']}.{task_num}"
                             self.domain_tree.insert(sub_id, "end", text=task, values=(task_id,))
                         except:
                             # Fallback if format is unexpected
                             self.domain_tree.insert(sub_id, "end", text=task, values=(subdomain_data['id'],))

        return tree_frame

    def on_provider_select(self, event=None):
        provider = self.provider_var.get()
        self.api_key_var.set(self.config_manager.get(f"{provider.upper()}_API_KEY", ""))
        self.validation_status_label.config(text="")
        self.ai_model_menu.set('')
        self.ai_model_menu.config(state="disabled")
        self.generate_qa_button.config(state="disabled")

    # --- Translation UI Handlers ---
    def on_trans_provider_select(self, event=None):
        provider = self.trans_provider_var.get()
        # Try to pre-fill with the main key if available, otherwise empty
        existing_key = self.config_manager.get(f"{provider.upper()}_API_KEY", "")
        self.trans_api_key_var.set(existing_key)
        self.trans_model_menu.set('')
        self.trans_model_menu.config(state="disabled")
        self.translate_btn.config(state="disabled")

    def validate_trans_key(self):
        provider = self.trans_provider_var.get()
        api_key = self.trans_api_key_var.get()
        if not api_key:
             messagebox.showwarning("Input Error", "Please enter a Translation API key.")
             return
        
        models = qa_generator.validate_and_fetch_models(provider, api_key)
        if models:
            self.trans_model_menu['values'] = models
            self.trans_model_menu.config(state="readonly")
            if models: self.trans_model_menu.set(models[0])
            self.translate_btn.config(state="normal")
        else:
            messagebox.showerror("Error", "Invalid Key for Translation Provider")

    def start_translation_thread(self):
        threading.Thread(target=self.run_translation_logic, daemon=True).start()

    def run_translation_logic(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content or "Analyzing content for:" in content and len(content) < 200:
            self.output_text.insert(tk.END, "\n[Error] No generated content found to translate.\n")
            return

        provider = self.trans_provider_var.get()
        model = self.trans_model_var.get()
        api_key = self.trans_api_key_var.get()

        self.output_text.insert(tk.END, f"\n\n--- Starting Translation ({provider} : {model}) ---\n")
        self.output_text.see(tk.END)

        try:
            translated_text = qa_generator.translate_and_reorganize(content, provider, model, api_key)
            
            self.output_text.insert(tk.END, f"\n--- Translation Result ---\n{translated_text}\n")
            self.output_text.see(tk.END)

            # Save Translation
            if self.last_saved_path:
                base, ext = os.path.splitext(self.last_saved_path)
                new_path = f"{base}_CN{ext}"
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(translated_text)
                self.output_text.insert(tk.END, f"\nTranslated file saved to: {new_path}\n")
            else:
                # Fallback if no previous save (unlikely if flow followed)
                save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'generated_qa')
                filename = f"Translated_QA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                path = os.path.join(save_dir, filename)
                with open(path, 'w', encoding='utf-8') as f: f.write(translated_text)
                self.output_text.insert(tk.END, f"\nTranslated file saved to: {path}\n")

        except Exception as e:
            self.output_text.insert(tk.END, f"\nTranslation Failed: {e}\n")
    # -------------------------------

    def validate_api_key(self):
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
            last_model = self.config_manager.get(f"LAST_USED_{provider.upper()}_MODEL")
            self.ai_model_menu.set(last_model if last_model in models else models[0])
            self.generate_qa_button.config(state="normal")
        else:
            self.validation_status_label.config(text="Invalid ✖", foreground="red")
            self.ai_model_menu.set('')
            self.ai_model_menu.config(state="disabled")
            self.generate_qa_button.config(state="disabled")

    def on_model_select(self, event=None):
        provider = self.provider_var.get()
        model_name = self.ai_model_var.get()
        self.config_manager.set(f"LAST_USED_{provider.upper()}_MODEL", model_name)
        self.config_manager.save()

    def on_generation_mode_select(self, event=None):
        for widget in self.dynamic_options_frame.winfo_children():
            widget.destroy()
        
        # Always default to treeview for now as it is the primary requirement
        self._create_domain_treeview(self.dynamic_options_frame)

    def start_qa_generation_thread(self):
        threading.Thread(target=self.start_qa_generation, daemon=True).start()

    def start_qa_generation(self):
        api_key = self.api_key_var.get()
        model_name = self.ai_model_var.get()
        provider = self.provider_var.get()
        cognitive_level = self.cognitive_level_var.get()

        if not all([api_key, model_name, provider]):
            messagebox.showerror("Error", "Configuration is incomplete.")
            return

        # Get Selected Outline Node
        selected_item = self.domain_tree.focus()
        if not selected_item:
             messagebox.showwarning("Selection Error", "Please select a topic from the Outline.")
             return
             
        item_values = self.domain_tree.item(selected_item, 'values')
        if not item_values:
            # Likely a section header without an ID or a task
            # Try parent
            parent_item = self.domain_tree.parent(selected_item)
            item_values = self.domain_tree.item(parent_item, 'values')
            
            if not item_values:
                messagebox.showwarning("Selection Error", "Please select a specific Subdomain or Task.")
                return
        
        node_id = item_values[0]
        item_text = self.domain_tree.item(selected_item, 'text')

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Analyzing content for: {item_text} (ID: {node_id})...")
        self.output_text.insert(tk.END, f"\nSelected Cognitive Level: {cognitive_level}\n")
        
        try:
            # 1. Retrieve Context
            context = self.content_orchestrator.get_context_for_node(node_id)
            
            key_terms = context.get('key_terms', [])
            text_content = context.get('text_content', '')
            examples = context.get('example_questions', [])
            chapters = context.get('chapters', [])
            
            if not text_content:
                self.output_text.insert(tk.END, "Error: No content found for this topic. It might not be mapped to a chapter yet.\n")
                return

            self.output_text.insert(tk.END, f"Found {len(chapters)} relevant chapters.\n")
            self.output_text.insert(tk.END, f"Found {len(key_terms)} Key Terms: {', '.join(key_terms[:10])}...")
            self.output_text.insert(tk.END, "Starting Batch Generation...\n\n")

            if not key_terms:
                self.output_text.insert(tk.END, "Warning: No specific Key Terms found. Generating generic questions based on text.\n")
                # Fallback to generic generation if needed, or create a dummy "General Concepts" term
                key_terms = ["General Concepts"]

            # 2. Batch Generation
            batch_size = 5
            for i in range(0, len(key_terms), batch_size):
                batch_terms = key_terms[i:i+batch_size]
                self.output_text.insert(tk.END, f"Processing Batch {i//batch_size + 1}: {', '.join(batch_terms)}")
                self.output_text.see(tk.END)
                
                prompt = qa_generator.generate_batch_prompt(batch_terms, text_content, examples, cognitive_level)
                
                response = qa_generator.generate_qa_with_ai(provider, model_name, api_key, prompt)
                
                self.output_text.insert(tk.END, f"\n--- Batch Results ---\n{response}\n\n")
                self.output_text.see(tk.END)
            
            self.output_text.insert(tk.END, "Generation Complete.\n")
            
            # Save Logic
            self._save_generated_qa(self.output_text.get("1.0", tk.END), node_id)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.output_text.insert(tk.END, f"\nCritical Error: {e}\n")

    def _save_generated_qa(self, content, topic_id):
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'generated_qa')
        os.makedirs(save_dir, exist_ok=True)
        filename = f"Topic_{topic_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(save_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
            self.last_saved_path = file_path
            self.output_text.insert(tk.END, f"Full report saved to: {file_path}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Failed to save report: {e}\n")

if __name__ == '__main__':
    pass