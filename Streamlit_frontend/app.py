import io
import base64
import sys
import json
import zipfile
import tempfile
import os
from datetime import datetime
import re
import streamlit as st


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


# File operations

def create_project_from_template(template_name):
    if template_name in PROJECT_TEMPLATES:
        template_files = PROJECT_TEMPLATES[template_name]
        for file_path, content in template_files.items():
            st.session_state.file_system[file_path] = content
        return True
    return False


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
