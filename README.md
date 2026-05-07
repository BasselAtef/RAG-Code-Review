# RAG-Code-Review
A high-performance Python code review tool that leverages RAG (Retrieval-Augmented Generation) to enforce custom project rules. It uses Ollama (local) or Groq (cloud) to analyze code against a knowledge base of Markdown-based documentation, providing a visual, line-by-line highlighted report of violations directly in a Gradio-based web interface.


# 🔍 AI-Powered Code Reviewer
An automated code review tool that combines RAG (Retrieval-Augmented Generation) with a visual UI to enforce custom project standards. Whether using a local LLM for privacy or a cloud-based LLM for speed, this tool provides a line-by-line highlighted report of code violations.

## 🚀 Quick Start Guide
Follow these steps to get the application running on your local machine.

## 1. Install Dependencies
Ensure you have Python 3.9+ installed. Clone the repository, navigate to the folder, and install the required packages:

`pip install -r requirements.txt`

## 2. Configure your LLM (Optional)
By default, the project is configured to use qwen3.5:4b via Ollama. If you wish to use a different local model:

##Open app.py.

Locate the `OLLAMA_MODEL` variable in the Configuration section.

Change it to your preferred model (e.g., llama3, mistral).

Note: Ensure you have the model pulled in Ollama first: ollama pull <model_name>.

## 3. Get a Groq API Key
For lightning-fast cloud inference, this tool supports Groq.

Go to the Groq Cloud Console.

Create a free-tier API key.

You will enter this key directly into the web interface when selecting the Groq (Cloud) backend.

## 4. Launch the Application
Start the Gradio server by running the main script:

`python app.py`

## 5. Access the UI
Once the terminal indicates the server is live, open your browser and go to:
`http://localhost:7860` in your browser.

## 6. Perform a Review
Follow the on-screen instructions:

### Select Backend: Choose between your local Ollama instance or Groq Cloud.

### Input Code: Upload a .py file or paste your code snippet.

### Run Review: Click the button and wait for the AI to analyze your code against the rules stored in your ./rules directory.

## 🛠️ Project Structure
app.py: The main application logic and Gradio UI.

./rules: Directory containing Markdown (.md) files of your project standards.

chroma_db: (Auto-generated) Local vector database for RAG.

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

## Pro-Tip:
If you add new rules to your .md files, the application will automatically re-index them on the next startup, ensuring your AI "Senior Engineer" is always up to date with the latest project requirements!
