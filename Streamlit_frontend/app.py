import streamlit as st
from streamlit_ace import st_ace
import uuid
import io
import base64
import pyodide
import asyncio
import sys

# Set page config as the first Streamlit command
st.set_page_config(layout="wide", page_title="Python IDE", page_icon="🐍")

# Custom CSS for professional dark theme
st.markdown("""
    <style>
    .main {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Inter', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #181825;
        border-right: 1px solid #313244;
    }
    .stButton>button {
        background-color: #585b70;
        color: #cdd6f4;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #45475a;
        transform: translateY(-1px);
    }
    .stTextInput>div>input {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #585b70;
        border-radius: 8px;
    }
    .file-tab {
        background-color: #313244;
        color: #cdd6f4;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .file-tab.active {
        background-color: #1e1e2e;
        border-bottom: 3px solid #89b4fa;
    }
    .file-tab:hover {
        background-color: #45475a;
    }
    .terminal {
        background-color: #181825;
        padding: 16px;
        border-radius: 8px;
        font-family: 'Fira Code', monospace;
        color: #cdd6f4;
        height: 250px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-all;
    }
    .editor-container {
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 8px;
        background-color: #181825;
    }
    .action-bar {
        background-color: #181825;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Simulated file system for Streamlit Cloud
if "file_system" not in st.session_state:
    st.session_state.file_system = {"example.py": "# Sample Python code\nprint('Hello, World!')"}

# Initialize session state
if "open_files" not in st.session_state:
    st.session_state.open_files = {}
if "active_file" not in st.session_state:
    st.session_state.active_file = None
if "show_create_file" not in st.session_state:
    st.session_state.show_create_file = False
if "output" not in st.session_state:
    st.session_state.output = ""

# File operations
def create_file(file_name):
    if file_name and file_name.endswith(".py") and file_name not in st.session_state.file_system:
        st.session_state.file_system[file_name] = ""
        return True
    return False

def delete_file(file_name):
    if file_name in st.session_state.file_system:
        del st.session_state.file_system[file_name]
        return True
    return False

def read_file(file_name):
    return st.session_state.file_system.get(file_name, "")

def write_file(file_name, content):
    st.session_state.file_system[file_name] = content
    return True

# Run Python code using Pyodide
async def run_code(code):
    try:
        # Redirect stdout
        output = io.StringIO()
        sys.stdout = output
        
        # Execute code
        await pyodide.runPythonAsync(code)
        
        # Get output
        result = output.getvalue()
        sys.stdout = sys.__stdout__
        
        return result or "Execution completed"
    except Exception as e:
        sys.stdout = sys.__stdout__
        return f"Error: {str(e)}"

# Streamlit UI
st.markdown("<h1 style='color: #cdd6f4; font-family: Inter, sans-serif;'>Professional Python IDE</h1>", unsafe_allow_html=True)

# Sidebar - File Explorer
with st.sidebar:
    st.markdown("<h3 style='color: #cdd6f4;'>File Explorer</h3>", unsafe_allow_html=True)
    
    if st.button("📄 New File", key="new_file_btn"):
        st.session_state.show_create_file = not st.session_state.show_create_file

    if st.session_state.show_create_file:
        new_file_name = st.text_input("Enter filename (e.g., script.py)", key="new_file_input")
        if st.button("Create File", key="create_file_btn"):
            if create_file(new_file_name):
                st.success(f"File '{new_file_name}' created successfully!")
                st.session_state.open_files[new_file_name] = ""
                st.session_state.active_file = new_file_name
                st.session_state.show_create_file = False
            else:
                st.error("File already exists or invalid name.")

    # File list
    files = list(st.session_state.file_system.keys())
    for file in files:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(file, key=f"open_{file}_{uuid.uuid4()}"):
                if file not in st.session_state.open_files:
                    st.session_state.open_files[file] = read_file(file)
                st.session_state.active_file = file
        with col2:
            if st.button("🗑️", key=f"delete_{file}_{uuid.uuid4()}"):
                if delete_file(file):
                    if file in st.session_state.open_files:
                        del st.session_state.open_files[file]
                    if st.session_state.active_file == file:
                        st.session_state.active_file = next(iter(st.session_state.open_files), None)
                    st.success(f"Deleted {file}")
                    st.rerun()

# Main content
if st.session_state.open_files:
    # File tabs
    tabs = st.columns(len(st.session_state.open_files))
    for i, file in enumerate(st.session_state.open_files.keys()):
        with tabs[i]:
            tab_style = "file-tab active" if file == st.session_state.active_file else "file-tab"
            if st.button(f"{file} ✖", key=f"tab_{file}_{uuid.uuid4()}", help="Close file"):
                del st.session_state.open_files[file]
                if st.session_state.active_file == file:
                    st.session_state.active_file = next(iter(st.session_state.open_files), None)
                st.rerun()
            st.markdown(f"<div class='{tab_style}'>{file}</div>", unsafe_allow_html=True)

    # Editor
    if st.session_state.active_file:
        st.markdown("<div class='editor-container'>", unsafe_allow_html=True)
        edited_code = st_ace(
            value=st.session_state.open_files[st.session_state.active_file],
            language="python",
            theme="dracula",
            height=500,
            font_size=14,
            show_gutter=True,
            wrap=True,
            auto_update=True,
            keybinding="vscode",
            min_lines=20,
            max_lines=50
        )

        # Auto-save
        if edited_code != st.session_state.open_files[st.session_state.active_file]:
            st.session_state.open_files[st.session_state.active_file] = edited_code
            write_file(st.session_state.active_file, edited_code)
            st.success(f"Auto-saved {st.session_state.active_file}", icon="💾")

        st.markdown("</div>", unsafe_allow_html=True)

        # Action bar
        st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Run Code", key="run_btn"):
                st.session_state.output = ""
                code_content = st.session_state.open_files[st.session_state.active_file]
                with st.spinner("Running code..."):
                    # Run code asynchronously
                    st.session_state.output = asyncio.run(run_code(code_content))

        with col2:
            if st.button("Download", key="download_btn"):
                # Create download link
                file_content = st.session_state.open_files[st.session_state.active_file]
                b64 = base64.b64encode(file_content.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64}" download="{st.session_state.active_file}">Download {st.session_state.active_file}</a>'
                st.markdown(href, unsafe_allow_html=True)

        with col3:
            if st.button("Clear Output", key="clear_btn"):
                st.session_state.output = ""

        st.markdown("</div>", unsafe_allow_html=True)

        # Terminal
        st.markdown("<h3 style='color: #cdd6f4;'>Terminal</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='terminal'>{st.session_state.output}</div>", unsafe_allow_html=True)

else:
    st.info("No files open. Create or open a file from the sidebar to start coding.")