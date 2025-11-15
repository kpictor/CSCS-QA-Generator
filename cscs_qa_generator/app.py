from . import gui
from . import content_orchestrator
from . import config_manager

def main():
    """Main entry point for the application."""
    co = content_orchestrator.ContentOrchestrator(base_path='cscs_qa_generator')
    cm = config_manager.ConfigManager(config_path='cscs_qa_generator/config.json')
    app = gui.App(content_orchestrator_instance=co, config_manager_instance=cm)
    app.mainloop()

if __name__ == "__main__":
    main()