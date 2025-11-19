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

        # --- Output Area ---
        output_frame = ttk.LabelFrame(main_frame, text="Generation Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Initialize
        self.on_provider_select()
        self.on_generation_mode_select()

    def _create_domain_treeview(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Removed selectmode='extended' as we are implementing manual checkboxes
        self.domain_tree = ttk.Treeview(tree_frame, height=10, columns=("id",), displaycolumns=())
        self.domain_tree.heading("#0", text="Exam Outline (Click to Select)", anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.domain_tree.yview)
        self.domain_tree.configure(yscrollcommand=scrollbar.set)
        
        self.domain_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Click for Checkbox Toggling
        self.domain_tree.bind("<Button-1>", self.toggle_selection)

        outline = self.content_orchestrator.get_outline()
        
        for section_name, section_data in outline.items():
            # Section
            sec_id = self.domain_tree.insert("", "end", text=f"☐ {section_data['header']}", values=(section_data['id'],), open=True)
            
            for domain_name, domain_data in section_data.get('domains', {}).items():
                # Domain
                dom_id = self.domain_tree.insert(sec_id, "end", text=f"☐ {domain_data['header']}", values=(domain_data['id'],), open=False)
                
                for subdomain_name, subdomain_data in domain_data.get('subdomains', {}).items():
                    # Subdomain
                    sub_id = self.domain_tree.insert(dom_id, "end", text=f"☐ {subdomain_data['header']}", values=(subdomain_data['id'],), open=False)
                    
                    # Tasks
                    for task in subdomain_data.get('tasks', []):
                         try:
                             task_num = task.split('.')[0].strip()
                             task_id = f"{subdomain_data['id']}.{task_num}"
                             self.domain_tree.insert(sub_id, "end", text=f"☐ {task}", values=(task_id,))
                         except:
                             self.domain_tree.insert(sub_id, "end", text=f"☐ {task}", values=(subdomain_data['id'],))

        return tree_frame

    def toggle_selection(self, event):
        # Identify specific element clicked (text, image, indicator, etc.)
        element = self.domain_tree.identify_element(event.x, event.y)
        
        # If clicked on the expansion arrow (indicator), do nothing regarding selection
        if "indicator" in element:
            return

        item_id = self.domain_tree.identify_row(event.y)
        if not item_id:
            return
            
        current_text = self.domain_tree.item(item_id, "text")
        
        # Determine target state
        # If currently unchecked (☐), we want to Check (True)
        # If currently checked (☑), we want to Uncheck (False)
        is_currently_checked = current_text.startswith("☑ ")
        target_check_state = not is_currently_checked
        
        def set_recursive_state(iid, check):
            text = self.domain_tree.item(iid, "text")
            
            # Remove existing prefix if present to get clean text
            clean_text = text
            if text.startswith("☐ "):
                clean_text = text[2:]
            elif text.startswith("☑ "):
                clean_text = text[2:]
            
            # Construct new text
            prefix = "☑ " if check else "☐ "
            new_text = prefix + clean_text
            
            self.domain_tree.item(iid, text=new_text)
            
            # Recurse to children
            for child in self.domain_tree.get_children(iid):
                set_recursive_state(child, check)

        # Apply to clicked item and all descendants
        set_recursive_state(item_id, target_check_state)

        def on_provider_select(self, event=None):
            provider = self.provider_var.get()
            self.api_key_var.set(self.config_manager.get(f"{provider.upper()}_API_KEY", ""))
            self.validation_status_label.config(text="")
            self.ai_model_menu.set('')
            self.ai_model_menu.config(state="disabled")
            self.generate_qa_button.config(state="disabled")
    
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

        # Find all Checked Items ("☑")
        # Recursively walk the tree
        selected_items = []
        
        def walk_tree(item_id):
            text = self.domain_tree.item(item_id, "text")
            values = self.domain_tree.item(item_id, "values")
            
            if text.startswith("☑ ") and values:
                # It's selected and has an ID
                selected_items.append({
                    "id": values[0],
                    "text": text[2:], # Remove checkmark
                    "node_id": item_id
                })
            
            for child in self.domain_tree.get_children(item_id):
                walk_tree(child)
        
        for child in self.domain_tree.get_children(""):
            walk_tree(child)

        if not selected_items:
             messagebox.showwarning("Selection Error", "Please check at least one topic (☑).")
             return
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Starting Generation for {len(selected_items)} topics...\n")
        self.output_text.insert(tk.END, f"Cognitive Level: {cognitive_level}\n")
        
        try:
            for item in selected_items:
                node_id = item["id"]
                item_text = item["text"]
                
                full_topic_content = "" # Reset for EACH topic (Individual Files)

                section_header = f"\n{'='*40}\nTOPIC: {item_text} (ID: {node_id})\n{'='*40}\n"
                self.output_text.insert(tk.END, section_header)
                self.output_text.see(tk.END)
                full_topic_content += section_header

                # 1. Retrieve Context
                context = self.content_orchestrator.get_context_for_node(node_id)
                key_terms = context.get('key_terms', [])
                text_content = context.get('text_content', '')
                examples = context.get('example_questions', [])
                
                if not text_content:
                    msg = "Error: No content found for this topic. It might not be mapped to a chapter yet.\n"
                    self.output_text.insert(tk.END, msg)
                    continue

                self.output_text.insert(tk.END, f"Found {len(key_terms)} Key Terms.\n")
                
                if not key_terms:
                    key_terms = ["General Concepts"]

                # 2. Batch Generation
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
                
                # Save Logic (Individual File per Topic)
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
            self.last_saved_path = file_path
            self.output_text.insert(tk.END, f"\n>>> Report saved: {filename}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Failed to save report: {e}\n")

if __name__ == '__main__':
    pass
