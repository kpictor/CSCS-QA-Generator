# CSCS Q&A Generator

This application helps generate high-quality multiple-choice questions and answers based on the CSCS study guide content, leveraging AI models.

## Project Structure

- `cscs_qa_generator/app.py`: Main entry point for the application.
- `cscs_qa_generator/gui.py`: Contains the graphical user interface (GUI) built with `tkinter`.
- `cscs_qa_generator/data_manager.py`: Handles loading and parsing of study materials (PDFs, `Match analysis.md`).
- `cscs_qa_generator/qa_generator.py`: Contains the logic for generating AI prompts and, eventually, interacting with AI models.
- `cscs_qa_generator/processed_chapters/`: Directory to store processed text content from PDF chapters in JSON format.
- `requirements.txt`: Lists Python dependencies.

## Setup

1.  **Clone the repository (if applicable) or navigate to the project directory:**

    ```bash
    cd C:\Users\Dicrix\Desktop\nsca-cscs
    ```

2.  **Install Python dependencies:**

    ```bash
    pip install -r cscs_qa_generator/requirements.txt
    ```

    *Note: If `PyMuPDF` installation fails, try `pip install PyMuPDF` to get the latest compatible version.*

3.  **Process PDF chapters:** Run the PDF processing script to extract and structure content from the PDF files. Ensure all chapter PDFs and `ExamContentOutline.pdf` are in the root directory.

    ```bash
    python cscs_qa_generator/process_pdfs.py
    ```

    This will create JSON files in the `cscs_qa_generator/processed_chapters/` directory.

## How to Run

To start the GUI application, run:

```bash
python -m cscs_qa_generator.app
```

## Features (Planned)

-   Select exam domain and cognitive level.
-   Generate AI prompts based on relevant study content.
-   Integrate with OpenAI and Gemini models for Q&A generation.
-   Display generated questions and answers in the GUI.

## Configuration (Planned)

API keys for AI models will be stored in `cscs_qa_generator/config.py` (or environment variables).
