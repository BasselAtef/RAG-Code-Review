import json
import re
import requests
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import gradio as gr
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# --- 1. CONFIGURATION ---
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3.5:4b"
GROQ_MODEL = "llama-3.1-8b-instant"
PERCHESIZE = 2000
 
# --- 2. SETUP EMBEDDINGS ---
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
 
# --- 3. SETUP VECTOR DB & CHUNKING ---
loader = DirectoryLoader("./rules", glob="**/*.md", loader_cls=TextLoader)
docs = loader.load()
if not docs:
    raise ValueError("No .md files found in ./rules — check the directory exists and has content.")
 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=PERCHESIZE, chunk_overlap=50)
documents = text_splitter.split_documents(docs)
 
vector_store = Chroma.from_documents(
    documents=documents,
    collection_name="code_review_rules",
    embedding=embeddings,
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
 
# --- 4. PROMPTS ---
SYSTEM_PROMPT = """You are a Senior Python Engineer. 
You must review the provided code based on the 'Project Rules'.
 
**CRITICAL INSTRUCTIONS FOR OUTPUT**:
1. Do NOT output any introduction, explanation, or reasoning text.
2. Do NOT output markdown code blocks (e.g., ```json).
3. Output **ONLY** the raw JSON object.
4. If you need to think, think internally, but the first visible text must be JSON.
5. Keep the JSON structure exactly as provided below.

**SEVERITY GUIDELINES**:
- **CRITICAL**: Security risks, data loss, or crashes. 
  *EXAMPLES*: Hardcoded API keys/secrets/credentials, SQL injection, OS command injection, logic errors that break core features. **Always mark hardcoded secrets as CRITICAL.**
- **WARNING**: Potential bugs, major PEP 8 violations, or poor resource management.
  *EXAMPLES*: Mutable default arguments, broad 'except:' blocks, unclosed files/connections, line length > 120.
- **INFO**: Minor style improvements or non-critical suggestions.
  *EXAMPLES*: Missing docstrings, minor naming convention slips, small performance optimizations.
 
Your JSON structure must match this schema precisely:
{
    "issues": [
        {
            "severity": "critical" or "warning" or "info",
            "description": "String describing the issue",
            "location": "Line number or specific code block description",
            "fix": "String describing how to fix it"
        }
    ]
}

**CRITICAL FOR LINE NUMBERS**:
1. The provided code has line numbers at the start of every line (e.g., '1: import os').
2. When identifying the "location", you MUST use the exact number shown at the start of that line.
3. Do NOT count lines yourself. Use the visible numbers.
4. Output only the number in the "location" field (e.g., "22").
5. If the issue is throughout the code not a single line, output "Throughout the code".
"""
 
USER_PROMPT_TEMPLATE = """Review the following Python code and the project rules:
 
{context}
{code}
"""
 
# --- 5. RETRIEVE CONTEXT ONCE AT STARTUP ---
retrieved_docs = retriever.invoke("Project Rules")
context = "\n\n".join([str(d.page_content) for d in retrieved_docs])
 
 
# --- 6. PARSE HELPER ---
def parse_json_response(raw_text: str):
    raw_text = re.sub(r'^```json\s*', '', raw_text)
    raw_text = re.sub(r'```$', '', raw_text).strip()
 
    json_match = re.search(r'\{\s*".*\}', raw_text, re.DOTALL)
    if not json_match:
        raise Exception("Could not parse JSON. Response:\n" + raw_text)
 
    clean_json_str = json_match.group()
    try:
        return json.loads(clean_json_str)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON parsing failed: {e}\nRaw: {clean_json_str}")
 
 
# --- 7. OLLAMA BACKEND ---
def run_with_ollama(full_prompt: str):
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "think": False,
            "format": "json",
            "options": {"num_predict": 1024}
        }
    )
    response.raise_for_status()
    return response.json().get("response", "")
 
 
# --- 8. GROQ BACKEND ---
def run_with_groq(full_prompt: str, api_key: str):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1024,
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
 
 
# --- 9. CORE REVIEW FUNCTION ---
def run_code_review(code: str, backend: str, groq_api_key: str):
    # Create a version of the code with line numbers clearly visible for the AI
    numbered_code = "\n".join([f"{i+1}: {line}" for i, line in enumerate(code.splitlines())])
 
    # Update your prompt to use this numbered version
    full_prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(
        context=context, 
        code=numbered_code
    )
 
    if backend == "☁️ Groq (Cloud)":
        if not groq_api_key or not groq_api_key.strip():
            raise Exception("Please enter your Groq API key.")
        raw_text = run_with_groq(full_prompt, groq_api_key.strip())
    else:
        raw_text = run_with_ollama(full_prompt)
 
    return parse_json_response(raw_text)
 
 
# --- 9.5 VISUAL HIGHLIGHTER ---
def generate_visual_review(code, issues):
    highlight_lines = {} # Maps line number to severity
    code_lines = code.splitlines()

    for issue in issues:
        location_raw = str(issue.get("location", ""))
        severity = issue.get("severity", "info").lower()
        
        affected_lines = []
        # Fallback to the AI's reported line number
        nums = [int(n) for n in re.findall(r'\d+', location_raw)]
        if len(nums) == 2:  # It's a range like 22-25
            for n in range(nums[0], nums[1] + 1):
                if 1 <= n <= len(code_lines):
                    affected_lines.append(n)
        elif len(nums) == 1: # It's a single line
            if 1 <= nums[0] <= len(code_lines):
                affected_lines.append(nums[0])
        
        for line_num in affected_lines:
            # Keep the highest severity if multiple issues on one line
            current_sev = highlight_lines.get(line_num, "info")
            sev_priority = {"critical": 3, "warning": 2, "info": 1}
            if sev_priority.get(severity, 1) > sev_priority.get(current_sev, 1):
                highlight_lines[line_num] = severity
            elif line_num not in highlight_lines:
                highlight_lines[line_num] = severity

    # Setup Pygments formatter with line numbers and highlighting
    formatter = HtmlFormatter(
        linenos=True,
        hl_lines=list(highlight_lines.keys()),
        style="monokai",
        nowrap=False
    )
    
    css = formatter.get_style_defs('.highlight')
    clean_code = code.replace('\\n', '\n')
    highlighted_code = highlight(clean_code, PythonLexer(), formatter)
    
    html_output = f"""
    <style>
        {css}
        .highlight-container {{
            max-height: 800px;
            overflow: auto;
            border-radius: 10px;
            border: 1px solid #444;
            background-color: #272822;
            padding: 0px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }}

        .highlighttable {{
            width: 100% !important;
            border-collapse: collapse;
            table-layout: fixed;
        }}

        .linenos {{
            width: 50px !important;
            padding: 10px 5px !important;
            color: #888;
            text-align: right;
            border-right: 1px solid #444;
            user-select: none;
            background-color: #23241f;
        }}

        .code {{
            padding: 10px 15px !important;
            width: auto;
            text-align: left;
        }}

        .highlight pre {{
            margin: 0;
            white-space: pre-wrap !important; 
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            font-family: 'Fira Code', 'Consolas', monospace !important;
        }}

        .hll {{ 
            background-color: rgba(255, 255, 0, 0.2) !important; 
            display: block;
            width: 100%;
            margin-left: -15px;
            padding-left: 15px;
            border-left: 4px solid #ffcc00 !important;
        }}
    </style>
    <div class="highlight-container">
        {highlighted_code}
    </div>
    """
    return html_output
 
 
# --- 10. GRADIO HANDLER ---
def handle_review(uploaded_file, pasted_code, backend, groq_api_key, progress=gr.Progress()):
    yield "### ⏳ Reviewing your code...\nPlease wait while the AI analyzes your script.", "", "Loading code view..."
    
    progress(0.1, desc="Reading input...")
    code = ""
    if uploaded_file is not None:
        with open(uploaded_file, "r", encoding="utf-8") as f:
            code = f.read()
    elif pasted_code and pasted_code.strip():
        code = pasted_code.strip()
    else:
        yield "⚠️ Please upload a file or paste some code.", "", ""
        return
 
    progress(0.4, desc="Consulting AI Reviewer...")
    try:
        result = run_code_review(code, backend, groq_api_key)
        progress(0.8, desc="Finalizing summary...")
        
        issues = result.get("issues", [])
        lines = []

        if not issues:
            lines.append("## ✅ No issues found.")
        else:
            lines.append(f"## Found {len(issues)} issues:\n")
            for i, issue in enumerate(issues, 1):
                severity = issue.get("severity", "info").upper()
                severity_emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(severity, "⚪")
                
                lines.append(f"## Issue {i}: {severity_emoji} {severity}")
                lines.append(f"### **📍 Location:** {issue.get('location', 'N/A')}")
                lines.append(f"### **⚙️ Description:** {issue.get('description', 'N/A')}")
                lines.append(f"### **🔧 Fix:** {issue.get('fix', 'N/A')}\n")
                lines.append("---")
 
        progress(0.9, desc="Generating visual report...")
        visual_html = generate_visual_review(code, issues)

        progress(1.0, desc="Review complete!")
        yield "\n".join(lines), json.dumps(result, indent=4), visual_html
 
    except Exception as e:
        yield f"❌ Error: {str(e)}", "", ""
 
 
# --- 11. SHOW/HIDE API KEY BOX ---
def toggle_api_key(backend):
    return gr.update(visible=(backend == "☁️ Groq (Cloud)"))
 
 
# --- 12. GRADIO UI ---
with gr.Blocks(
    title="🔍 Code Reviewer",
    theme=gr.themes.Default(
        primary_hue="red",
        neutral_hue="zinc",
    ),
    css="""
    footer { display: none !important; }
    #title { text-align: center; margin-bottom: 8px; }
    #subtitle { text-align: center; color: #64748b; margin-bottom: 24px; }
    #main-col { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
    .gr-markdown p, .gr-markdown li { font-size: 1.1rem !important; line-height: 1.6; }
    .gr-markdown h3 { font-size: 1.3rem !important; }
    label, .gr-button { font-size: 1rem !important; }
    pre, code { font-size: 0.95rem !important; }
"""
) as demo:
 
    gr.Markdown("# 🔍 Code Review Tool", elem_id="title")
    gr.Markdown("Powered by Ollama, Groq", elem_id="subtitle")
 
    with gr.Column(elem_id="main-col"):
        gr.Markdown("## 📋 Instructions")
        instructions = gr.Markdown(
            """
            ### 1. Upload a .py file or paste your code below.
            ### 2. Select the LLM Backend (Ollama or Groq).
            ### 3. Click "▶ Run Review".
            ### 4. Code will be analyzed and issues will be listed with their severity level.\n
            """,
            label="Instructions"
        )
 
        # --- Backend selector ---
        gr.Markdown("## ⚙️ Backend")
        backend = gr.Radio(
            choices=["🖥️ Local (Ollama)", "☁️ Groq (Cloud)"],
            value="🖥️ Local (Ollama)",
            label="Select LLM Backend",
        )
        groq_api_key = gr.Textbox(
            label="Groq API Key",
            placeholder="gsk_...",
            type="password",
            visible=False,
        )
        backend.change(fn=toggle_api_key, inputs=backend, outputs=groq_api_key)
 
        gr.Markdown("## 📂 Input")
        uploaded_file = gr.File(
            label="Upload a .py file",
            file_types=[".py", ".txt"],
            type="filepath"
        )
        gr.Markdown("**or paste your code below:**")
        pasted_code = gr.Code(
            label="Paste Code",
            language="python",
            lines=20,
        )
        submit_btn = gr.Button("▶ Run Review", variant="primary", size="lg")

        gr.Markdown("## 📋 Results")
        formatted_output = gr.Markdown(label="Review Summary")
        
        gr.Markdown("## 🎨 Visual Code Review")
        visual_review_html = gr.HTML(label="Code Highlight")

        with gr.Accordion("Raw JSON Output", open=False):
            raw_output = gr.Code(language="json", label="JSON")

 
    submit_btn.click(
        fn=handle_review,
        inputs=[uploaded_file, pasted_code, backend, groq_api_key],
        outputs=[formatted_output, raw_output, visual_review_html],
    )
 
if __name__ == "__main__":
    demo.launch()