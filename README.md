# CSCS Q&A Generator

This application uses AI to generate Certified Strength and Conditioning Specialist (CSCS) exam practice questions based on the official NSCA textbook chapters. It allows users to select specific topics from the exam outline, choose a cognitive level (Recall, Application, Analysis), and generate relevant multiple-choice questions to aid in their study process.

## Features

-   **AI-Powered Q&A:** Leverages generative AI (Gemini, OpenAI, Qwen, or Claude) to create high-quality, context-aware practice questions.
-   **Targeted Studying:** Select specific domains, sub-domains, and tasks directly from the CSCS exam outline.
-   **Cognitive Level Selection:** Tailor the difficulty and style of questions by choosing between Recall, Application, and Analysis cognitive levels.
-   **Editable Prompts:** View and edit the prompt before it's sent to the AI to fine-tune the generated questions.
-   **Data-Driven:** Uses processed text from the official textbook PDFs and metadata from study guides to ensure questions are relevant and accurate.
-   **Simple GUI:** An easy-to-use graphical interface built with Tkinter.

## Project Structure

The project is organized for clarity and scalability:

```
nsca-cscs/
├── cscs_qa_generator/   # Main application source code
│   ├── processed_chapters/ # JSON files generated from PDFs
│   ├── __init__.py
│   ├── ai_models.py
│   ├── app.py              # Main application entry point
│   ├── config.json         # Stores API keys and settings
│   ├── config_manager.py
│   ├── content_orchestrator.py # Maps topics to content
│   ├── gui.py              # The Tkinter GUI
│   ├── metadata_parser.py  # Parses metadata files
│   └── process_pdfs.py     # Script to process source PDFs
├── data/
│   ├── metadata/           # Exam outlines, study guides, etc.
│   └── pdfs/               # Source textbook chapter PDFs
├── .gitignore
├── README.md
├── requirements.txt
└── run_app.bat             # Simple script to run the application
```

## Setup and Installation

### Prerequisites

-   Python 3.10+
-   An API key for either Google Gemini, OpenAI, Qwen, or Claude.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd nsca-cscs
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

### 1. Place Your Data

-   Place all the chapter PDF files into the `data/pdfs/` directory.
-   Ensure the metadata files (`ExamContentOutline.md`, `study_guide.md`, etc.) are in the `data/metadata/` directory.

### 2. Process the PDFs

Before running the main application for the first time, you must process the PDFs into a format the application can use. Run the following command from the root directory:

```bash
python -m cscs_qa_generator.process_pdfs
```

This will read the PDFs, extract the text, and save the content as structured `.json` files in the `cscs_qa_generator/processed_chapters/` directory. You only need to do this once, unless you change the source PDFs.

### 3. Launch the Application

Run the application using the provided batch script:

```bash
run_app.bat
```

Alternatively, you can run it directly from the command line:

```bash
python -m cscs_qa_generator.app
```

## Usage

1.  **Select AI Provider:** Choose between Gemini, OpenAI, Qwen, and Claude from the dropdown menu.
2.  **Enter API Key:** Input your API key for the selected provider.
3.  **Validate Key:** Click "Validate Key". This will verify the key and fetch the available AI models. The buttons below will become active upon successful validation.
4.  **Select Model:** Choose a specific AI model from the dropdown.
5.  **Select Exam Topic:** Navigate the tree to select the precise topic you want to generate a question for.
6.  **Select Cognitive Level:** Choose the desired cognitive level for the question.
7.  **Generate Prompt:** Click "Generate Prompt". The application will gather the relevant content and create a detailed prompt in the "Prompt" text box.
8.  **(Optional) Edit Prompt:** You can now edit the generated prompt directly in the text box to refine it.
9.  **Send to AI:** Click "Send to AI". The application will send the prompt to the selected AI model and display the generated Q&A in the "Generated Q&A" box.
