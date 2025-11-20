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

---

## 📂 Project Structure

*   `src/`: Source code.
    *   `ui/`: GUI implementation (Tkinter).
    *   `core/`: Core logic for prompt generation, orchestration, and translation.
    *   `api/`: Interfaces for different AI providers.
    *   `data_processing/`: Scripts to parse PDFs and metadata.
*   `data/`: Contains PDF source files and metadata mappings.
*   `generated_qa/`: Default output folder for generated questions.
*   `requirements.txt`: Python dependencies.

## 📄 License
[MIT License](LICENSE)