import streamlit as st
from streamlit_ace import st_ace
import uuid
import io
import base64
import sys
import json
import zipfile
import tempfile
import os
from datetime import datetime
import re

# Set page config as the first Streamlit command
st.set_page_config(
    layout="wide", 
    page_title="Advanced Python IDE", 
    page_icon="🐍",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern glassmorphism theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar .sidebar-content {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 0 12px 12px 0;
    }
    
    .stButton>button {
        background: rgba(59, 130, 246, 0.8);
        color: #ffffff;
        border-radius: 8px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 8px 16px;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: 500;
        backdrop-filter: blur(5px);
    }
    
    .stButton>button:hover {
        background: rgba(59, 130, 246, 1);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    .stTextInput>div>input, .stSelectbox>div>div {
        background: rgba(30, 41, 59, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }
    
    .file-tab {
        background: rgba(30, 41, 59, 0.8);
        color: #e2e8f0;
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        display: inline-block;
        font-weight: 500;
    }
    
    .file-tab.active {
        background: rgba(59, 130, 246, 0.8);
        border-bottom: 3px solid #3b82f6;
        color: #ffffff;
    }
    
    .file-tab:hover {
        background: rgba(71, 85, 105, 0.8);
        transform: translateY(-1px);
    }
    
    .terminal {
        background: rgba(15, 23, 42, 0.9);
        padding: 20px;
        border-radius: 12px;
        font-family: 'Fira Code', monospace;
        color: #e2e8f0;
        height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-all;
        border: 1px solid rgba(148, 163, 184, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .editor-container {
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 0;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }
    
    .action-bar {
        background: rgba(30, 41, 59, 0.8);
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    .status-bar {
        background: rgba(15, 23, 42, 0.9);
        padding: 8px 16px;
        border-radius: 0 0 12px 12px;
        color: #94a3b8;
        font-size: 12px;
        font-family: 'Fira Code', monospace;
        border-top: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .project-header {
        background: rgba(15, 23, 42, 0.8);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .feature-card {
        background: rgba(30, 41, 59, 0.8);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        backdrop-filter: blur(5px);
        margin-bottom: 12px;
    }
    
    .success-message {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #4ade80;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #f87171;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 8px;
        color: #e2e8f0;
        backdrop-filter: blur(5px);
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.8);
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Language configurations
LANGUAGE_CONFIG = {
    "python": {"extension": ".py", "ace_mode": "python", "icon": "🐍"},
    "javascript": {"extension": ".js", "ace_mode": "javascript", "icon": "🟨"},
    "html": {"extension": ".html", "ace_mode": "html", "icon": "🌐"},
    "css": {"extension": ".css", "ace_mode": "css", "icon": "🎨"},
    "json": {"extension": ".json", "ace_mode": "json", "icon": "📄"},
    "markdown": {"extension": ".md", "ace_mode": "markdown", "icon": "📝"},
}

# Project templates
PROJECT_TEMPLATES = {
    "Empty Project": {},
    "Flask Web App": {
        "app.py": """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
""",
        "templates/index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Flask App</title>
</head>
<body>
    <h1>Welcome to Flask!</h1>
</body>
</html>
""",
        "requirements.txt": "Flask==2.3.2\n"
    },
    "Data Analysis": {
        "analysis.py": """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load and analyze data
def load_data(filename):
    return pd.read_csv(filename)

def basic_stats(df):
    return df.describe()

if __name__ == '__main__':
    print("Data Analysis Template")
""",
        "requirements.txt": "pandas==2.0.3\nnumpy==1.24.3\nmatplotlib==3.7.1\n"
    }
}

# Initialize enhanced session state
def initialize_session_state():
    defaults = {
        "file_system": {"welcome.py": "# Welcome to Advanced Python IDE\nprint('Hello, World!')\nprint('Start coding!')"},
        "open_files": {},
        "active_file": None,
        "show_create_file": False,
        "output": "",
        "terminal_history": [],
        "find_replace_open": False,
        "current_language": "python",
        "project_name": "My Project",
        "code_snippets": {
            "for_loop": "for i in range(10):\n    print(i)",
            "function": "def function_name(param):\n    return param",
            "class": "class ClassName:\n    def __init__(self):\n        pass",
            "try_except": "try:\n    # code here\n    pass\nexcept Exception as e:\n    print(f'Error: {e}')"
        },
        "settings": {
            "theme": "dracula",
            "font_size": 14,
            "show_minimap": True,
            "auto_save": True
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Enhanced file operations
def create_file(file_name, language="python"):
    if file_name and file_name not in st.session_state.file_system:
        extension = LANGUAGE_CONFIG.get(language, {}).get("extension", ".txt")
        if not file_name.endswith(extension):
            file_name += extension
        st.session_state.file_system[file_name] = ""
        return file_name
    return None

def delete_file(file_name):
    if file_name in st.session_state.file_system:
        del st.session_state.file_system[file_name]
        if file_name in st.session_state.open_files:
            del st.session_state.open_files[file_name]
        if st.session_state.active_file == file_name:
            st.session_state.active_file = next(iter(st.session_state.open_files), None)
        return True
    return False

def create_project_from_template(template_name):
    if template_name in PROJECT_TEMPLATES:
        template_files = PROJECT_TEMPLATES[template_name]
        for file_path, content in template_files.items():
            st.session_state.file_system[file_path] = content
        return True
    return False

def export_project_as_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, content in st.session_state.file_system.items():
            zip_file.writestr(file_name, content)
    zip_buffer.seek(0)
    return zip_buffer

# Enhanced code execution
def run_python_code(code):
    try:
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        # Create a new namespace for execution
        namespace = {'__name__': '__main__'}
        
        # Execute the code
        exec(code, namespace)
        
        # Get outputs
        output = stdout_buffer.getvalue()
        errors = stderr_buffer.getvalue()
        
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        result = ""
        if output:
            result += f"Output:\n{output}\n"
        if errors:
            result += f"Errors:\n{errors}\n"
        
        return result or "Code executed successfully (no output)"
        
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return f"Runtime Error: {str(e)}"

# Find and replace functionality
def find_and_replace(content, find_text, replace_text, case_sensitive=False):
    if not case_sensitive:
        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
        return pattern.sub(replace_text, content)
    else:
        return content.replace(find_text, replace_text)

# UI Components
def render_project_header():
    st.markdown(f"""
    <div class="project-header">
        <h1 style='color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;'>
            🚀 {st.session_state.project_name}
        </h1>
        <p style='color: #94a3b8; margin: 8px 0 0 0; font-size: 14px;'>
            Advanced Python IDE with Multi-language Support
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("### 📁 Project Explorer")
        
        # Project name
        new_project_name = st.text_input("Project Name", value=st.session_state.project_name)
        if new_project_name != st.session_state.project_name:
            st.session_state.project_name = new_project_name
        
        # Quick actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 New File"):
                st.session_state.show_create_file = not st.session_state.show_create_file
        with col2:
            if st.button("📁 Template"):
                st.session_state.show_template_selector = True
        
        # File creation form
        if st.session_state.show_create_file:
            with st.form("create_file_form"):
                new_file_name = st.text_input("File name")
                language = st.selectbox("Language", list(LANGUAGE_CONFIG.keys()))
                if st.form_submit_button("Create"):
                    created_file = create_file(new_file_name, language)
                    if created_file:
                        st.session_state.open_files[created_file] = ""
                        st.session_state.active_file = created_file
                        st.session_state.show_create_file = False
                        st.success(f"Created {created_file}")
                        st.rerun()
                    else:
                        st.error("File already exists or invalid name")
        
        # Template selector
        if st.session_state.get('show_template_selector', False):
            template = st.selectbox("Choose Template", list(PROJECT_TEMPLATES.keys()))
            if st.button("Create from Template"):
                create_project_from_template(template)
                st.session_state.show_template_selector = False
                st.success(f"Created project from {template} template")
                st.rerun()
        
        # File upload
        uploaded_file = st.file_uploader("Upload File", type=['py', 'js', 'html', 'css', 'json', 'md', 'txt'])
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            st.session_state.file_system[uploaded_file.name] = content
            st.success(f"Uploaded {uploaded_file.name}")
        
        st.markdown("---")
        
        # File list
        files = list(st.session_state.file_system.keys())
        if files:
            st.markdown("**Files:**")
            for file in sorted(files):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    # Get file icon based on extension
                    icon = "📄"
                    for lang, config in LANGUAGE_CONFIG.items():
                        if file.endswith(config["extension"]):
                            icon = config["icon"]
                            break
                    
                    if st.button(f"{icon} {file}", key=f"open_{file}", use_container_width=True):
                        if file not in st.session_state.open_files:
                            st.session_state.open_files[file] = st.session_state.file_system[file]
                        st.session_state.active_file = file
                        st.rerun()
                
                with col2:
                    if st.button("📥", key=f"download_{file}", help="Download"):
                        file_content = st.session_state.file_system[file]
                        b64 = base64.b64encode(file_content.encode()).decode()
                        href = f'<a href="data:text/plain;base64,{b64}" download="{file}">⬇️</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                with col3:
                    if st.button("🗑️", key=f"delete_{file}", help="Delete"):
                        delete_file(file)
                        st.rerun()
        
        st.markdown("---")
        
        # Export project
        if st.button("📦 Export Project"):
            zip_buffer = export_project_as_zip()
            st.download_button(
                label="Download ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"{st.session_state.project_name}.zip",
                mime="application/zip"
            )
        
        # Code snippets
        st.markdown("### 🧩 Code Snippets")
        snippet = st.selectbox("Insert snippet", list(st.session_state.code_snippets.keys()))
        if st.button("Insert Snippet"):
            if st.session_state.active_file:
                current_content = st.session_state.open_files.get(st.session_state.active_file, "")
                st.session_state.open_files[st.session_state.active_file] = current_content + "\n" + st.session_state.code_snippets[snippet]
                st.rerun()

def render_main_editor():
    if not st.session_state.open_files:
        st.info("🚀 Welcome to Advanced Python IDE! Create or open a file to start coding.")
        return
    
    # File tabs
    if len(st.session_state.open_files) > 1:
        tabs = st.columns(len(st.session_state.open_files))
        for i, file in enumerate(st.session_state.open_files.keys()):
            with tabs[i]:
                tab_class = "file-tab active" if file == st.session_state.active_file else "file-tab"
                if st.button(f"{file} ✕", key=f"tab_{file}"):
                    del st.session_state.open_files[file]
                    if st.session_state.active_file == file:
                        st.session_state.active_file = next(iter(st.session_state.open_files), None)
                    st.rerun()
    
    if not st.session_state.active_file:
        st.session_state.active_file = next(iter(st.session_state.open_files), None)
    
    if st.session_state.active_file:
        # Action bar
        render_action_bar()
        
        # Find & Replace
        if st.session_state.get('find_replace_open', False):
            render_find_replace()
        
        # Editor
        render_code_editor()
        
        # Terminal
        render_terminal()

def render_action_bar():
    st.markdown('<div class="action-bar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("▶️ Run", key="run_btn", use_container_width=True):
            execute_current_file()
    
    with col2:
        if st.button("🔍 Find", key="find_btn", use_container_width=True):
            st.session_state.find_replace_open = not st.session_state.find_replace_open
    
    with col3:
        if st.button("🎨 Format", key="format_btn", use_container_width=True):
            format_current_file()
    
    with col4:
        if st.button("💾 Save All", key="save_btn", use_container_width=True):
            save_all_files()
    
    with col5:
        if st.button("🗑️ Clear", key="clear_output_btn", use_container_width=True):
            st.session_state.output = ""
            st.session_state.terminal_history = []
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_find_replace():
    with st.expander("🔍 Find & Replace", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            find_text = st.text_input("Find", key="find_text")
        with col2:
            replace_text = st.text_input("Replace", key="replace_text")
        
        col3, col4 = st.columns(2)
        with col3:
            case_sensitive = st.checkbox("Case sensitive")
        with col4:
            if st.button("Replace All"):
                if st.session_state.active_file and find_text:
                    current_content = st.session_state.open_files[st.session_state.active_file]
                    new_content = find_and_replace(current_content, find_text, replace_text, case_sensitive)
                    st.session_state.open_files[st.session_state.active_file] = new_content
                    st.success("Replacement completed")

def render_code_editor():
    st.markdown('<div class="editor-container">', unsafe_allow_html=True)
    
    # Determine language mode
    current_file = st.session_state.active_file
    ace_mode = "python"
    for lang, config in LANGUAGE_CONFIG.items():
        if current_file.endswith(config["extension"]):
            ace_mode = config["ace_mode"]
            break
    
    # Code editor
    edited_code = st_ace(
        value=st.session_state.open_files[st.session_state.active_file],
        language=ace_mode,
        theme=st.session_state.settings["theme"],
        height=500,
        font_size=st.session_state.settings["font_size"],
        show_gutter=True,
        wrap=True,
        auto_update=True,
        keybinding="vscode",
        min_lines=20,
        max_lines=50
    )
    
    # Auto-save functionality
    if edited_code != st.session_state.open_files[st.session_state.active_file]:
        st.session_state.open_files[st.session_state.active_file] = edited_code
        st.session_state.file_system[st.session_state.active_file] = edited_code
        if st.session_state.settings["auto_save"]:
            st.markdown('<div class="success-message">✅ Auto-saved</div>', unsafe_allow_html=True)
    
    # Status bar
    lines = len(edited_code.split('\n')) if edited_code else 0
    chars = len(edited_code) if edited_code else 0
    st.markdown(f'''
    <div class="status-bar">
        📄 {st.session_state.active_file} | Lines: {lines} | Characters: {chars} | Language: {ace_mode.title()}
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_terminal():
    st.markdown("### 💻 Terminal")
    
    # Terminal output
    terminal_content = st.session_state.output
    if st.session_state.terminal_history:
        terminal_content = "\n".join(st.session_state.terminal_history) + "\n" + terminal_content
    
    st.markdown(f'<div class="terminal">{terminal_content}</div>', unsafe_allow_html=True)
    
    # Command input
    command = st.text_input("Command:", key="terminal_command", placeholder="Enter command...")
    if st.button("Execute Command") and command:
        execute_terminal_command(command)

def execute_current_file():
    if st.session_state.active_file and st.session_state.active_file.endswith('.py'):
        code_content = st.session_state.open_files[st.session_state.active_file]
        with st.spinner("🚀 Running code..."):
            result = run_python_code(code_content)
            st.session_state.output = result
            st.session_state.terminal_history.append(f">>> Running {st.session_state.active_file}")
            st.session_state.terminal_history.append(result)
    else:
        st.warning("Can only execute Python files (.py)")

def execute_terminal_command(command):
    st.session_state.terminal_history.append(f"$ {command}")
    
    # Simple command simulation
    if command.startswith("echo "):
        output = command[5:]
    elif command == "ls":
        output = "\n".join(st.session_state.file_system.keys())
    elif command == "pwd":
        output = f"/projects/{st.session_state.project_name}"
    elif command == "clear":
        st.session_state.terminal_history = []
        st.session_state.output = ""
        return
    else:
        output = f"Command '{command}' not recognized. Available: echo, ls, pwd, clear"
    
    st.session_state.terminal_history.append(output)
    st.rerun()

def format_current_file():
    # Simple formatting for Python files
    if st.session_state.active_file and st.session_state.active_file.endswith('.py'):
        try:
            import ast
            code = st.session_state.open_files[st.session_state.active_file]
            # Basic validation
            ast.parse(code)
            st.success("✅ Code is syntactically correct")
        except SyntaxError as e:
            st.error(f"❌ Syntax Error: {e}")
    else:
        st.info("Formatting available for Python files")

def save_all_files():
    for file_name, content in st.session_state.open_files.items():
        st.session_state.file_system[file_name] = content
    st.success("💾 All files saved successfully")

# Main application
def main():
    render_project_header()
    
    # Create layout
    render_sidebar()
    render_main_editor()
    
    # Settings in expander at bottom
    with st.expander("⚙️ Settings"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_theme = st.selectbox("Theme", ["dracula", "monokai", "github", "tomorrow"], 
                                   index=["dracula", "monokai", "github", "tomorrow"].index(st.session_state.settings["theme"]))
            if new_theme != st.session_state.settings["theme"]:
                st.session_state.settings["theme"] = new_theme
        
        with col2:
            new_font_size = st.slider("Font Size", 10, 24, st.session_state.settings["font_size"])
            if new_font_size != st.session_state.settings["font_size"]:
                st.session_state.settings["font_size"] = new_font_size
        
        with col3:
            st.session_state.settings["auto_save"] = st.checkbox("Auto Save", st.session_state.settings["auto_save"])

if __name__ == "__main__":
    main()