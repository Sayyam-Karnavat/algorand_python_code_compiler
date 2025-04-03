import streamlit as st
from streamlit_ace import st_ace
import os
import requests

# Function to list Python files (excluding app.py and server.py)
def list_files():
    return [f for f in os.listdir() if f not in ("app.py", "server.py", "deploy.py") and f.endswith(".py")]

# Function to create a new file
def create_file(file_name):
    if file_name and not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("")  

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

# Function to send a request to run Python code on the backend
def run_code_backend(code):
    response = requests.post("http://127.0.0.1:5000/run", json={"code": code})
    if response.status_code == 200:
        return response.json().get("output", "Execution completed")
    else:
        return response.json().get("error", "Execution failed")

# Function to send deploy request to Flask server
def deploy_code(file_path):
    response = requests.post("http://127.0.0.1:5000/deploy", json={"file_path": file_path})
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
st.title("Algorand Smart Contract Editor")

# Sidebar - File Explorer & Create File Section
st.sidebar.header("Files in Directory")

# Button to create a new file
if st.sidebar.button("Create New File"):
    st.session_state.show_create_file = True

# Show the file creation field
if st.session_state.show_create_file:
    new_file_name = st.sidebar.text_input("Enter filename (e.g., contract.py)")
    if st.sidebar.button("Save File"):
        if new_file_name:
            create_file(new_file_name)
            st.success(f"File '{new_file_name}' created successfully!")
            st.session_state.show_create_file = False  
            st.rerun()  

# Show all files in the directory
files = list_files()

for file in files:
    col1, col2 = st.sidebar.columns([3, 1])  
    with col1:
        if st.button(file, key=f"open_{file}"):
            if file not in st.session_state.open_files:
                st.session_state.open_files[file] = read_file(file)
            st.session_state.active_file = file  

    with col2:
        if st.button("🗑️", key=f"delete_{file}"):  
            delete_file(file)
            if file in st.session_state.open_files:
                del st.session_state.open_files[file]
            if st.session_state.active_file == file:
                st.session_state.active_file = None
            st.success(f"Deleted {file}")
            st.rerun()

# Display open files
if st.session_state.open_files:
    tab_labels = list(st.session_state.open_files.keys())
    cols = st.columns(len(tab_labels) + 1)

    for i, file in enumerate(tab_labels):
        with cols[i]:
            if st.button(f"✖ {file}", key=f"close_{file}"):
                del st.session_state.open_files[file]
                if st.session_state.active_file == file:
                    st.session_state.active_file = next(iter(st.session_state.open_files), None)

    # Show active file content
    if st.session_state.active_file:
        edited_code = st_ace(
            value=st.session_state.open_files[st.session_state.active_file],
            language="python",
            theme="monokai",
            height=400,
            font_size=14,
            show_gutter=True,
            wrap=True
        )

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
                code_content = st.session_state.open_files[st.session_state.active_file]
                st.session_state.output = run_code_backend(code_content)

        with col3:
            if st.button("Deploy"):
                st.session_state.deploy_output = deploy_code(st.session_state.active_file)

        # Output Section
        st.subheader("Terminal Output:")
        st.text_area("Output", st.session_state.output or st.session_state.deploy_output, height=250)
