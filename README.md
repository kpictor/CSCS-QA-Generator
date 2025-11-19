# CSCS Q&A Generator

This project is a desktop application designed to help users study for the Certified Strength and Conditioning Specialist (CSCS) exam. It uses AI models to generate questions and answers based on the content of the CSCS textbook.

## Supported AI Providers
- Gemini
- OpenAI
- Qwen
- Claude

## Design Goals

The **CSCS Q&A Generator** is a desktop application designed to be an intelligent study assistant for individuals preparing for the Certified Strength and Conditioning Specialist (CSCS) exam. Its primary goal is to move beyond simple, static question banks by leveraging AI to create dynamic, targeted, and contextually relevant practice questions based on the official NSCA textbook.

The core design is centered around three distinct and powerful generation modes:

1.  **Chapter Review Mode:** This mode allows users to select one or more chapters from the textbook. The application then identifies every official "Key Term" from those chapters and generates a unique question for each one. This ensures a comprehensive review of the fundamental vocabulary and concepts presented in the selected material.

2.  **Targeted Practice Mode:** This is the most focused mode. It presents the user with the official CSCS exam content outline in a navigable tree structure. The user can select any specific topic or task from this outline (e.g., "Apply Knowledge of Bone and Connective Tissue Anatomy and Physiology"). The application then intelligently generates questions from the key terms that are most relevant to that specific outline topic, allowing for highly targeted practice on areas of weakness.

3.  **Exam Simulation Mode:** This mode simulates a real exam experience by generating a user-specified number of questions. Crucially, it adheres to the official exam's proportional weighting, generating the correct percentage of questions from the two major sections: "Scientific Foundations" and "Practical / Applied". This provides a realistic and balanced measure of exam readiness.

Underpinning these modes is a sophisticated backend that parses and maps the relationships between the textbook's content, the study guide's key terms, and the exam's content outline, ensuring that every generated question is both relevant and context-aware.

## Prerequisites

Before running the application, you must have:
1.  **CSCS Textbook PDFs:** You need digital copies of the CSCS textbook chapters.
2.  **API Key:** An API key for one of the supported AI providers (Gemini, OpenAI, Qwen, or Claude).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CSCS-QA-Generator.git
    cd CSCS-QA-Generator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Data Setup:**
    -   Create a folder named `pdfs` inside the `data` directory: `data/pdfs`.
    -   Place your CSCS textbook PDF files into `data/pdfs`.
    -   Run the data processing script to extract content from the PDFs:
        ```bash
        python -m src.data_processing.process_pdfs
        ```
    -   This will generate structured JSON files in `src/processed_chapters`, which the application uses to generate questions.

## Usage

1.  **Run the application:**
    ```bash
    python -m src.app
    ```

2.  **Configure the AI Provider:**
    - Select your desired AI provider (e.g., Gemini, OpenAI) from the dropdown menu.
    - Enter your API key for the selected provider.
    - Click "Validate Key" to confirm the key is correct and to populate the available AI models.

3.  **Generate Q&A:**
    - Select your desired AI model.
    - Choose a "Generation Mode" (Chapter Review, Targeted Practice, or Exam Simulation).
    - Follow the on-screen prompts to select chapters, topics, or the number of questions.
    - Click "Generate Q&A" to start the process.
    - The generated questions and answers will appear in the output text box and will be saved to the `generated_qa` directory.
