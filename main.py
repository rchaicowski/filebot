import sys
from pathlib import Path

# Make sure local modules resolve correctly when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from ai.providers import NoAIProvider, OllamaProvider


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FileBot")
    app.setApplicationVersion("0.1.0")

    # Auto-detect AI provider: use Ollama if running, else fall back to NoAI
    ollama = OllamaProvider()
    provider = ollama if ollama.available else NoAIProvider()

    window = MainWindow(ai_provider=provider)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
