import streamlit as st
from streamlit_ace import st_ace
import os
import requests
import uuid
import time

# Custom CSS for modern, Remix-like styling
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
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #45475a;
    }
    .stTextInput>div>input {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #585b70;
        border-radius: 8px;
    }
    .stTextArea textarea {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #585b70;
        border-radius: 8px;
    }
    .file-tab {
        background-color: #313244;
        color: #cdd6f4;
        padding: 8px 16px;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
        cursor: pointer;
    }
    .file-tab.active {
        background-color: #1e1e2e;
        border-bottom: 2px solid #89b4fa;
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
        height: 200px;
        overflow-y: auto;
    }
    .spinner {
        text-align: center;
        color: #89b4fa;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to list Python files (excluding app.py and server.py)
def list_files():
    return [f for f in os.listdir() if f not in ("app.py", "server.py", "deploy.py") and f.endswith(".py")]

# Function to create a new file
def create_file(file_name):
    if file_name and not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("")
        return True
    return False

# Function to delete a file
def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        return True
    return False

# Function to read file content
def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except:
        return ""

# Function to write file content
def write_file(file_path, content):
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    except:
        return False

# Function to send a request to run Python code on the backend
def run_code_backend(code):
    try:
        response = requests.post("http://127.0.0.1:5000/run", json={"code": code}, timeout=10)
        if response.status_code == 200:
            return response.json().get("output", "Execution completed")
        else:
            return response.json().get("error", "Execution failed")
    except requests.RequestException as e:
        return f"Error connecting to backend: {str(e)}"

# Function to send deploy request to Flask server
def deploy_code(file_path):
    try:
        response = requests.post("http://127.0.0.1:5000/deploy", json={"file_path": file_path}, timeout=10)
        if response.status_code == 200:
            return response.json().get("deploy_result", "Deployment completed")
        else:
            return response.json().get("error", "Deployment failed")
    except requests.RequestException as e:
        return f"Error connecting to backend: {str(e)}"

# Initialize session state
if "open_files" not in st.session_state:
    st.session_state.open_files = {}

if "active_file" not in st.session_state:
    st.session_state.active_file = None

if "show_create_file" not in st.session_state:
    st.session_state.show_create_file = False

if "output" not in st.session_state:
    st.session_state.output = ""

if "deploy_output" not in st.session_state:
    st.session_state.deploy_output = ""

if "loading" not in st.session_state:
    st.session_state.loading = False

# Streamlit UI
st.set_page_config(layout="wide", page_title="Algorand Smart Contract IDE", page_icon="⚙️")
st.markdown("<h1 style='color: #cdd6f4; font-family: Inter, sans-serif;'>Algorand Smart Contract IDE</h1>", unsafe_allow_html=True)

# Sidebar - File Explorer & Create File Section
with st.sidebar:
    st.markdown("<h3 style='color: #cdd6f4;'>File Explorer</h3>", unsafe_allow_html=True)
    
    # Toggle for creating new file
    if st.button("📄 New File", key="new_file_btn"):
        st.session_state.show_create_file = not st.session_state.show_create_file

    # File creation input
    if st.session_state.show_create_file:
        new_file_name = st.text_input("Enter filename (e.g., contract.py)", key="new_file_input")
        if st.button("Create File", key="create_file_btn"):
            if new_file_name.endswith(".py"):
                if create_file(new_file_name):
                    st.success(f"File '{new_file_name}' created successfully!")
                    st.session_state.open_files[new_file_name] = ""
                    st.session_state.active_file = new_file_name
                    st.session_state.show_create_file = False
                else:
                    st.error("File already exists or invalid name.")
            else:
                st.error("Filename must end with .py")

    # File list
    files = list_files()
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

# Main content - File tabs and editor
if st.session_state.open_files:
    # File tabs
    tab_cols = st.columns(len(st.segmental_state.open_files) + 1)


    for i, file in enumerate(st.session_state.open_files.keys()):
        with tab_cols[i]:
            tab_style = "file-tab active" if file == st.session_state.active_file else "file-tab"
            if st.button(f"{file} ✖", key=f"tab_{file}_{uuid.uuid4()}", help="Close file"):
                del st.session_state.open_files[file]
                if st.session_state.active_file == file:
                    st.session_state.active_file = next(iter(st.session_state.open_files), None)
                st.rerun()
            st.markdown(f"<div class='{tab_style}'>{file}</div>", unsafe_allow_html=True)

    # Code editor for active file
    if st.session_state.active_file:
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

        # Auto-save on code change
        if edited_code != st.session_state.open_files[st.session_state.active_file]:
            st.session_state.open_files[st.session_state.active_file] = edited_code
            write_file(st.session_state.active_file, edited_code)
            st.success(f"Auto-saved {st.session_state.active_file}", icon="💾")

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Save", key="save_btn"):
                if write_file(st.session_state.active_file, st.session_state.open_files[st.session_state.active_file]):
                    st.success(f"Saved {st.session_state.active_file}", icon="💾")
                else:
                    st.error("Failed to save file.")

        with col2:
            if st.button("Run Code", key="run_btn"):
                st.session_state.loading = True
                st.session_state.output = ""
                code_content = st.session_state.open_files[st.session_state.active_file]
                with st.spinner("Running code..."):
                    time.sleep(0.5)  # Simulate async feel
                    st.session_state.output = run_code_backend(code_content)
                st.session_state.loading = False

        with col3:
            if st.button("Deploy", key="deploy_btn"):
                st.session_state.loading = True
                st.session_state.deploy_output = ""
                with st.spinner("Deploying contract..."):
                    time.sleep(0.5)  # Simulate async feel
                    st.session_state.deploy_output = deploy_code(st.session_state.active_file)
                st.session_state.loading = False

        # Terminal output
        st.markdown("<h3 style='color: #cdd6f4;'>Terminal</h3>", unsafe_allow_html=True)
        output = st.session_state.output or st.session_state.deploy_output
        st.markdown(f"<div class='terminal'>{output}</div>", unsafe_allow_html=True)

else:
    st.info("No files open. Create or open a file from the sidebar to start editing.")