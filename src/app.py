from .ui import gui
from .core import content_orchestrator
from .utils import config_manager

def main():
    """Main entry point for the application."""
    co = content_orchestrator.ContentOrchestrator()
    cm = config_manager.ConfigManager(config_path='config.json')
    app = gui.App(content_orchestrator_instance=co, config_manager_instance=cm)
    app.mainloop()

if __name__ == "__main__":
    main()