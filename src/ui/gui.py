import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from ..core import qa_generator
from ..core import content_orchestrator
from ..utils import config_manager
import os
from datetime import datetime
import threading

DEFAULT_TRANSLATION_PROMPT = """
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

class App(tk.Tk):
    def __init__(self, content_orchestrator_instance, config_manager_instance):
        super().__init__()

        self.title("CSCS Q&A Generator & Translator")
        self.geometry("1100x850")
        self.content_orchestrator = content_orchestrator_instance
        self.config_manager = config_manager_instance

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Global Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Global Configuration", padding="10")
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

        ttk.Label(config_frame, text="Select Model:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.ai_model_var = tk.StringVar()
        self.ai_model_menu = ttk.Combobox(config_frame, textvariable=self.ai_model_var, state="disabled")
        self.ai_model_menu.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        self.ai_model_menu.bind("<<ComboboxSelected>>", self.on_model_select)

        # --- Notebook (Tabs) ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Q&A Generation
        self.gen_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gen_tab, text="Q&A Generation")
        self._init_generation_tab(self.gen_tab)

        # Tab 2: Translation
        self.trans_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.trans_tab, text="Translation Tool")
        self._init_translation_tab(self.trans_tab)

        # Initialize Config
        self.on_provider_select()

    # =========================================
    # Tab 1: Generation Logic
    # =========================================
    def _init_generation_tab(self, parent):
        # Controls
        controls_frame = ttk.LabelFrame(parent, text="Generation Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text="Mode:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.generation_mode_var = tk.StringVar(value="Targeted Practice (Outline)")
        self.generation_mode_menu = ttk.Combobox(controls_frame, textvariable=self.generation_mode_var, values=["Targeted Practice (Outline)", "Practice by Chapter"], state="readonly")
        self.generation_mode_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.generation_mode_menu.bind("<<ComboboxSelected>>", self.on_generation_mode_select)

        ttk.Label(controls_frame, text="Cognitive Level:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.cognitive_level_var = tk.StringVar(value="Recall")
        self.cognitive_level_menu = ttk.Combobox(controls_frame, textvariable=self.cognitive_level_var, values=["Recall", "Application", "Analysis"], state="readonly")
        self.cognitive_level_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        self.dynamic_options_frame = ttk.Frame(controls_frame)
        self.dynamic_options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        controls_frame.rowconfigure(2, weight=1)
        self.dynamic_options_frame.columnconfigure(0, weight=1)

        self.generate_qa_button = ttk.Button(controls_frame, text="Generate Q&A", command=self.start_qa_generation_thread, state=tk.DISABLED)
        self.generate_qa_button.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)

        # Output
        output_frame = ttk.LabelFrame(parent, text="Generation Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize Default View
        self.on_generation_mode_select()

    # =========================================
    # Tab 2: Translation Logic
    # =========================================
    def _init_translation_tab(self, parent):
        # File Selection
        file_frame = ttk.LabelFrame(parent, text="Batch File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.trans_files_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.trans_files_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="Browse Files...", command=self.browse_translation_files).pack(side=tk.LEFT, padx=5)

        # Prompt
        prompt_frame = ttk.LabelFrame(parent, text="Translation Prompt (Template)", padding="10")
        prompt_frame.pack(fill=tk.X, pady=5)
        self.trans_prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=8)
        self.trans_prompt_text.pack(fill=tk.X, expand=True)
        self.trans_prompt_text.insert(tk.END, DEFAULT_TRANSLATION_PROMPT)

        # Action
        self.translate_btn = ttk.Button(parent, text="Translate Selected Files", command=self.start_batch_translation_thread, state=tk.DISABLED)
        self.translate_btn.pack(fill=tk.X, pady=5, padx=10)

        # Output
        log_frame = ttk.LabelFrame(parent, text="Translation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.trans_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.trans_log.pack(fill=tk.BOTH, expand=True)

    def browse_translation_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")])
        if files:
            self.trans_files_var.set(";".join(files))

    def start_batch_translation_thread(self):
        threading.Thread(target=self.run_batch_translation, daemon=True).start()

    def run_batch_translation(self):
        files_str = self.trans_files_var.get()
        if not files_str:
            messagebox.showwarning("Input Error", "Please select files to translate.")
            return

        files = files_str.split(";")
        provider = self.provider_var.get()
        model = self.ai_model_var.get()
        api_key = self.api_key_var.get()
        prompt_template = self.trans_prompt_text.get("1.0", tk.END).strip()

        if not all([provider, model, api_key]):
             messagebox.showwarning("Config Error", "Please configure and validate the AI model first.")
             return

        self.trans_log.delete("1.0", tk.END)
        self.trans_log.insert(tk.END, f"Starting Batch Translation for {len(files)} files...\n\n")

        for i, file_path in enumerate(files):
            if not os.path.exists(file_path):
                self.trans_log.insert(tk.END, f"Skipping invalid path: {file_path}\n")
                continue

            filename = os.path.basename(file_path)
            self.trans_log.insert(tk.END, f"[{i+1}/{len(files)}] Translating: {filename}...")
            self.trans_log.see(tk.END)
            self.update_idletasks()

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                translated_content = qa_generator.translate_and_reorganize(content, provider, model, api_key, prompt_template)
                
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_CN{ext}"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                
                self.trans_log.insert(tk.END, " Done ✔\n")
                self.trans_log.insert(tk.END, f"   -> Saved to: {output_path}\n")
            
            except Exception as e:
                self.trans_log.insert(tk.END, f" FAILED ✖\n   Error: {e}\n")
                import traceback
                traceback.print_exc()
        
        self.trans_log.insert(tk.END, "\nBatch Translation Complete.")
        self.trans_log.see(tk.END)

    # =========================================
    # Shared/Generation Methods
    # =========================================
    def _create_domain_treeview(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.domain_tree = ttk.Treeview(tree_frame, height=10, columns=("id",), displaycolumns=())
        self.domain_tree.heading("#0", text="Exam Outline (Click to Select)", anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.domain_tree.yview)
        self.domain_tree.configure(yscrollcommand=scrollbar.set)
        
        self.domain_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.domain_tree.bind("<Button-1>", self.toggle_selection)

        outline = self.content_orchestrator.get_outline()
        
        for section_name, section_data in outline.items():
            sec_id = self.domain_tree.insert("", "end", text=f"☐ {section_data['header']}", values=(section_data['id'],), open=True)
            for domain_name, domain_data in section_data.get('domains', {}).items():
                dom_id = self.domain_tree.insert(sec_id, "end", text=f"☐ {domain_data['header']}", values=(domain_data['id'],), open=False)
                for subdomain_name, subdomain_data in domain_data.get('subdomains', {}).items():
                    sub_id = self.domain_tree.insert(dom_id, "end", text=f"☐ {subdomain_data['header']}", values=(subdomain_data['id'],), open=False)
                    for task in subdomain_data.get('tasks', []):
                         try:
                             task_num = task.split('.')[0].strip()
                             task_id = f"{subdomain_data['id']}.{task_num}"
                             self.domain_tree.insert(sub_id, "end", text=f"☐ {task}", values=(task_id,))
                         except:
                             self.domain_tree.insert(sub_id, "end", text=f"☐ {task}", values=(subdomain_data['id'],))
        return tree_frame

    def _create_chapter_listbox(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        ttk.Button(btn_frame, text="Select All", command=self.select_all_chapters).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(btn_frame, text="Unselect All", command=self.unselect_all_chapters).pack(side=tk.LEFT, padx=5, expand=True)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.chapter_tree = ttk.Treeview(tree_frame, height=10, columns=("id",), displaycolumns=(), show="tree")
        self.chapter_tree.heading("#0", text="Chapters (Click to Select)", anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.chapter_tree.yview)
        self.chapter_tree.configure(yscrollcommand=scrollbar.set)
        
        self.chapter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapter_tree.bind("<Button-1>", self.toggle_selection)

        chapters = self.content_orchestrator.get_all_chapter_titles()
        for chap in chapters:
            self.chapter_tree.insert("", "end", text=f"☐ {chap}", values=(chap,))
        
        return tree_frame

    def select_all_chapters(self):
        for item in self.chapter_tree.get_children():
             text = self.chapter_tree.item(item, "text")
             if text.startswith("☐ "):
                 self.chapter_tree.item(item, text="☑ " + text[2:])

    def unselect_all_chapters(self):
        for item in self.chapter_tree.get_children():
             text = self.chapter_tree.item(item, "text")
             if text.startswith("☑ "):
                 self.chapter_tree.item(item, text="☐ " + text[2:])

    def toggle_selection(self, event):
        tree = event.widget
        element = tree.identify_element(event.x, event.y)
        if "indicator" in element: return

        item_id = tree.identify_row(event.y)
        if not item_id: return
            
        current_text = tree.item(item_id, "text")
        is_currently_checked = current_text.startswith("☑ ")
        target_check_state = not is_currently_checked
        
        def set_recursive_state(iid, check):
            text = tree.item(iid, "text")
            clean_text = text[2:] if text.startswith("☐ ") or text.startswith("☑ ") else text
            new_text = ("☑ " if check else "☐ ") + clean_text
            tree.item(iid, text=new_text)
            for child in tree.get_children(iid):
                set_recursive_state(child, check)

        set_recursive_state(item_id, target_check_state)

    def on_provider_select(self, event=None):
        provider = self.provider_var.get()
        self.api_key_var.set(self.config_manager.get(f"{provider.upper()}_API_KEY", ""))
        self.validation_status_label.config(text="")
        self.ai_model_menu.set('')
        self.ai_model_menu.config(state="disabled")
        self.generate_qa_button.config(state="disabled")
        self.translate_btn.config(state="disabled")
    
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
            self.translate_btn.config(state="normal")
        else:
            self.validation_status_label.config(text="Invalid ✖", foreground="red")
            self.ai_model_menu.set('')
            self.ai_model_menu.config(state="disabled")
            self.generate_qa_button.config(state="disabled")
            self.translate_btn.config(state="disabled")

    def on_model_select(self, event=None):
        provider = self.provider_var.get()
        model_name = self.ai_model_var.get()
        self.config_manager.set(f"LAST_USED_{provider.upper()}_MODEL", model_name)
        self.config_manager.save()

    def on_generation_mode_select(self, event=None):
        for widget in self.dynamic_options_frame.winfo_children():
            widget.destroy()
        
        mode = self.generation_mode_var.get()
        if mode == "Targeted Practice (Outline)":
            self._create_domain_treeview(self.dynamic_options_frame)
        elif mode == "Practice by Chapter":
            self._create_chapter_listbox(self.dynamic_options_frame)

    def start_qa_generation_thread(self):
        threading.Thread(target=self.start_qa_generation, daemon=True).start()

    def start_qa_generation(self):
        api_key = self.api_key_var.get()
        model_name = self.ai_model_var.get()
        provider = self.provider_var.get()
        cognitive_level = self.cognitive_level_var.get()
        mode = self.generation_mode_var.get()

        if not all([api_key, model_name, provider]):
            messagebox.showerror("Error", "Configuration is incomplete.")
            return

        selected_items = []

        if mode == "Targeted Practice (Outline)":
            def walk_tree(item_id):
                text = self.domain_tree.item(item_id, "text")
                values = self.domain_tree.item(item_id, "values")
                if text.startswith("☑ ") and values:
                    selected_items.append({
                        "id": values[0],
                        "text": text[2:],
                        "node_id": item_id,
                        "type": "topic"
                    })
                for child in self.domain_tree.get_children(item_id):
                    walk_tree(child)
            for child in self.domain_tree.get_children(""):
                walk_tree(child)

        elif mode == "Practice by Chapter":
            for item_id in self.chapter_tree.get_children():
                text = self.chapter_tree.item(item_id, "text")
                values = self.chapter_tree.item(item_id, "values")
                if text.startswith("☑ "):
                    chap_title = values[0]
                    import re
                    match = re.match(r'(Chapter\s+\d+)', chap_title)
                    short_id = match.group(1).replace(' ', '_') if match else chap_title[:20].replace(' ', '_')
                    selected_items.append({
                        "id": chap_title,
                        "text": chap_title,
                        "node_id": short_id,
                        "type": "chapter"
                    })

        if not selected_items:
             messagebox.showwarning("Selection Error", "Please select at least one item.")
             return
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Starting Generation for {len(selected_items)} items...\n")
        self.output_text.insert(tk.END, f"Cognitive Level: {cognitive_level}\n")
        
        try:
            for item in selected_items:
                node_id = item["node_id"]
                item_text = item["text"]
                full_topic_content = ""
                section_header = f"\n========================================\nITEM: {item_text}\n========================================\n"
                self.output_text.insert(tk.END, section_header)
                self.output_text.see(tk.END)
                full_topic_content += section_header

                if item.get("type") == "chapter":
                    context = self.content_orchestrator.get_context_for_chapters([item["id"]])
                else:
                    context = self.content_orchestrator.get_context_for_node(item["id"])

                key_terms = context.get('key_terms', [])
                text_content = context.get('text_content', '')
                examples = context.get('example_questions', [])
                
                if not text_content:
                    self.output_text.insert(tk.END, "Error: No content found for this item.\n")
                    continue

                self.output_text.insert(tk.END, f"Found {len(key_terms)} Key Terms.\n")
                if not key_terms: key_terms = ["General Concepts"]

                batch_size = 5
                for i in range(0, len(key_terms), batch_size):
                    batch_terms = key_terms[i:i+batch_size]
                    self.output_text.insert(tk.END, f"  > Processing Batch {i//batch_size + 1}...")
                    self.output_text.update()
                    
                    prompt = qa_generator.generate_batch_prompt(batch_terms, text_content, examples, cognitive_level)
                    response = qa_generator.generate_qa_with_ai(provider, model_name, api_key, prompt)
                    
                    batch_output = f"\n--- Batch Results ({', '.join(batch_terms)}) ---\n{response}\n"
                    self.output_text.insert(tk.END, " Done.\n")
                    full_topic_content += batch_output
                
                self._save_generated_qa(full_topic_content, node_id)
                self.output_text.see(tk.END)

            self.output_text.insert(tk.END, "\nAll Tasks Complete.\n")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.output_text.insert(tk.END, f"\nCritical Error: {e}\n")

    def _save_generated_qa(self, content, topic_id):
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'generated_qa')
        os.makedirs(save_dir, exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"Topic_{topic_id}_{date_str}.md"
        file_path = os.path.join(save_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
            self.output_text.insert(tk.END, f"\n>>> Report saved: {filename}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Failed to save report: {e}\n")

if __name__ == '__main__':
    pass