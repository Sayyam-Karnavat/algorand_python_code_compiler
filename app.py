import streamlit as st
from streamlit_ace import st_ace
import os
import io
from contextlib import redirect_stdout
import requests

# Function to list all Python files in the directory (excluding app.py & deploy.py)
def list_files():
    return [f for f in os.listdir() if f != "app.py" and f != "deploy.py" and f!= "server.py" and f.endswith(".py")]

# Function to create a new file
def create_file(file_name):
    if file_name and not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("")  # Create an empty file

# Function to delete a file
def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)

# Function to read file content
def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

# Function to write file content
def write_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)

# Function to execute Python code
def run_code(code):
    try:
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code, {})
        return f.getvalue()
    except Exception as e:
        return str(e)

# Function to compile using algokit and deploy the compiled contract
def deploy_code(file_path):
    response = requests.post("http://127.0.0.1:9999/deploy", json={"file_path": file_path})
    if response.status_code == 200:
        return response.json().get("deploy_result", "Deployment completed")
    else:
        return response.json().get("error", "Deployment failed")

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

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Algorand Python Deployment")

# Sidebar - File Explorer & Create File Section
st.sidebar.header("Files in Directory")

# Button to show the file creation input field
if st.sidebar.button("Create New File"):
    st.session_state.show_create_file = True

# Show the file creation field if the button was clicked
if st.session_state.show_create_file:
    new_file_name = st.sidebar.text_input("Enter filename (e.g., script.py)")
    if st.sidebar.button("Save File"):
        if new_file_name:
            create_file(new_file_name)
            st.success(f"File '{new_file_name}' created successfully!")
            st.session_state.show_create_file = False  # Hide input field after saving
            st.rerun()  # Refresh the app to update file list

# Show all files in the directory
files = list_files()

for file in files:
    col1, col2 = st.sidebar.columns([3, 1])  # Sidebar layout for file listing & delete button
    with col1:
        if st.button(file, key=f"open_{file}"):
            if file not in st.session_state.open_files:
                st.session_state.open_files[file] = read_file(file)
            st.session_state.active_file = file  # Set active file
    with col2:
        if st.button("🗑️", key=f"delete_{file}"):  # Delete button
            delete_file(file)
            if file in st.session_state.open_files:
                del st.session_state.open_files[file]
            if st.session_state.active_file == file:
                st.session_state.active_file = None
            st.success(f"Deleted {file}")
            st.rerun()  # Refresh file list after deletion

# Display open files as tabs with close buttons
if st.session_state.open_files:
    tab_labels = list(st.session_state.open_files.keys())
    cols = st.columns(len(tab_labels) + 1)

    for i, file in enumerate(tab_labels):
        with cols[i]:
            if st.button(f"✖ {file}", key=f"close_{file}"):
                del st.session_state.open_files[file]
                if st.session_state.active_file == file:
                    st.session_state.active_file = next(iter(st.session_state.open_files), None)

    # Show active file content in VSCode-like Ace Editor
    if st.session_state.active_file:
        edited_code = st_ace(
            value=st.session_state.open_files[st.session_state.active_file],
            language="python" if st.session_state.active_file.endswith(".py") else "json",
            theme="monokai",
            height=400,
            font_size=14,
            show_gutter=True,
            wrap=True
        )

        # Update session state when content changes
        if edited_code != st.session_state.open_files[st.session_state.active_file]:
            st.session_state.open_files[st.session_state.active_file] = edited_code

        # Buttons for Save, Run, and Deploy
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Save"):
                write_file(st.session_state.active_file, st.session_state.open_files[st.session_state.active_file])
                st.success(f"Saved {st.session_state.active_file}")

        with col2:
            if st.button("Run Code"):
                st.session_state.output = run_code(st.session_state.open_files[st.session_state.active_file])

        with col3:
            if st.button("Deploy"):
                st.session_state.deploy_output = deploy_code(st.session_state.active_file)

        # Output Section - Terminal Output
        st.subheader("Terminal Output:")
        st.text_area("Output", st.session_state.output or st.session_state.deploy_output, height=250)
