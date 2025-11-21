# CSCS Q&A Generator & Translator

A comprehensive tool designed for **Strength and Conditioning (CSCS)** candidates and educators. This application leverages advanced AI models (Gemini, OpenAI, Claude, Qwen) to generate high-quality, exam-style practice questions and translate educational content into Simplified Chinese.

## 🚀 Features

### 1. 📝 Smart Q&A Generation
Generate exam-quality multiple-choice questions tailored to specific needs.

*   **Targeted Practice (Outline):** Select specific domains, subdomains, or tasks directly from the CSCS Exam Content Outline. The AI uses the official exam structure to create relevant questions.
*   **Practice by Chapter:** Choose one or multiple chapters from the *Essentials of Strength Training and Conditioning* textbook. The tool pulls key terms and context from your selected chapters.
*   **Cognitive Levels:** Customize the difficulty and style of questions:
    *   **Recall:** Basic definitions and facts.
    *   **Application:** Applying knowledge to specific scenarios (calculations, "if/then" situations).
    *   **Analysis:** Complex decision-making and evaluating competing factors.
*   **Batch Generation:** Automatically generates questions for batches of key terms to ensure broad coverage.

### 2. 🌏 Content Translation
A dedicated tool for translating CSCS study materials into **Simplified Chinese (简体中文)** while preserving professional formatting.

*   **Batch Processing:** Select multiple Markdown files at once.
*   **Terminology Precision:** Ensures accurate translation of specific sports science terminology (e.g., "Hypertrophy" -> "肌肥大", "Work-to-rest ratio" -> "功/休比").
*   **Auto-Formatting:** Reorganizes Q&A content into a clean, readable layout suitable for study guides.

### 3. 🤖 Multi-Model AI Support
Choose your preferred AI provider. The application supports:
*   **Google Gemini** (Recommended for speed and cost)
*   **OpenAI (GPT-4/3.5)**
*   **Anthropic Claude**
*   **Alibaba Qwen**

### 4. 🎴 Anki Flashcard Export
Convert translated Chinese Q&A files into Anki-compatible flashcards for spaced repetition learning.

*   **Dedicated Window:** Separate, clean interface for flashcard conversion
*   **Batch Conversion:** Process multiple `*_CN.md` files at once
*   **Smart Parsing:** Automatically extracts questions, options, answers, and explanations
*   **Anki-Ready Format:** Generates tab-delimited TXT files with proper HTML formatting
*   **Auto-Tagging:** Tags flashcards based on filename for easy organization in Anki

---

## 🛠️ Installation

### Prerequisites
*   **Python 3.8+** must be installed on your system.
*   An API Key for your chosen AI provider (e.g., a Google Gemini API Key).

### Setup
1.  **Clone the Repository** (or download the source code):
    ```bash
    git clone https://github.com/yourusername/CSCS-QA-Generator.git
    cd CSCS-QA-Generator
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 💻 Usage

### Running the Application
Double-click the **`run_app.bat`** file (Windows) or run the following command in your terminal:

```bash
python -m src.app
```

### Configuration
1.  **API Provider:** On the top "Global Configuration" bar, select your AI Provider (e.g., "Gemini").
2.  **API Key:** Paste your API Key into the box and click **"Validate Key"**.
    *   *Note:* The key is saved locally in `config.json` so you don't need to re-enter it every time.
3.  **Model:** Once validated, select the specific model you wish to use (e.g., `gemini-1.5-flash` or `gpt-4`).

### Generating Questions (Tab 1)
1.  **Select Mode:**
    *   *Targeted Practice (Outline):* Browse the Exam Outline tree and check (☑) the specific topics you want to study.
    *   *Practice by Chapter:* Select one or more chapters from the list. Use "Select All" for a comprehensive exam.
2.  **Select Cognitive Level:** Choose "Recall", "Application", or "Analysis".
3.  **Generate:** Click **"Generate Q&A"**. The AI will process your selection and output questions in the text window.
4.  **Save:** The results are automatically saved as Markdown files in the `generated_qa/` folder.

### Translating Files (Tab 2)
1.  **Select Files:** Click **"Browse Files..."** and select the Markdown (`.md`) files you want to translate.
2.  **Review Prompt:** (Optional) You can edit the "Translation Prompt" to change the style or specific instructions.
3.  **Translate:** Click **"Translate Selected Files"**.
4.  **Output:** Translated files are saved in the same directory as the original files with a `_CN` suffix (e.g., `Topic_1_CN.md`).

### Exporting to Anki Flashcards (Tab 3)
1.  **Go to Tab:** Click the **"Anki Flashcard Export"** tab (third tab in the application).
2.  **Select Files:** Click **"Browse Files..."** and select your translated Chinese files (`*_CN.md`).
3.  **Convert:** Click **"Convert to Anki Flashcards"**. The conversion log will show progress.
4.  **Import to Anki:** 
    *   Open Anki desktop application
    *   Go to **File → Import**
    *   Select the generated `*_anki.txt` file(s)
    *   Verify settings (Type: Basic, HTML enabled) and click Import
5.  **Study:** Review your flashcards in Anki!

**Flashcard Format:**
- **Front:** Key term + Question with all options
- **Back:** Correct answer + Detailed explanation

---

## 📂 Project Structure

```
CSCS-QA-Generator/
├── src/                    # Source code
│   ├── api/               # AI provider interfaces (Gemini, OpenAI, Claude, Qwen)
│   ├── core/              # Core logic (QA generation, content orchestration)
│   ├── data_processing/   # Metadata parsers and PDF processors
│   ├── ui/                # GUI implementation (Tkinter)
│   │   ├── gui.py         # Main application window
│   │   └── anki_window.py # Anki flashcard export window
│   ├── utils/             # Configuration and converter utilities
│   │   ├── config_manager.py
│   │   └── anki_converter.py  # Markdown to Anki conversion logic
│   └── app.py             # Main application entry point
├── data/
│   ├── metadata/          # Exam outline and key term mappings (JSON/MD)
│   └── pdfs/              # PDF source files (gitignored)
├── generated_qa/          # Output folder for generated Q&A (gitignored)
├── requirements.txt       # Python dependencies
├── run_app.bat            # Quick launch script (Windows)
├── README.md              # This file
└── LICENSE                # MIT License
```

### Key Files
- **`data/metadata/id_to_chapters_map.json`**: Maps outline IDs to textbook chapters
- **`data/metadata/key_term_to_outline.json`**: Maps outline tasks to key terms
- **`data/metadata/ExamContentOutline.md`**: CSCS exam structure and weighting
- **`data/metadata/study_guide.md`**: Chapter summaries and key terms

## 📄 License
[MIT License](LICENSE)