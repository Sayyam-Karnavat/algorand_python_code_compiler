import streamlit as st
from streamlit_ace import st_ace
import os
import io
import subprocess
from contextlib import redirect_stdout

# Function to list all Python, JSON, and TEAL files in the directory (excluding app.py)
def list_files():
    return [f for f in os.listdir() if f != "app.py" and (f.endswith(".py") or f.endswith(".json") or f.endswith(".teal"))]

# Function to create a new file in the working directory
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

# Function to compile using algokit
def compile_code(file_path):
    try:
        result = subprocess.run(["algokit", "compile", "py", file_path], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

# Initialize session state
if "open_files" not in st.session_state:
    st.session_state.open_files = {}

if "active_file" not in st.session_state:
    st.session_state.active_file = None

if "show_create_file" not in st.session_state:
    st.session_state.show_create_file = False

if "output" not in st.session_state:
    st.session_state.output = ""

if "compile_output" not in st.session_state:
    st.session_state.compile_output = ""

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Algorand Python Compiler")

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

        # Buttons for Save, Run, and Compile
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Save"):
                write_file(st.session_state.active_file, st.session_state.open_files[st.session_state.active_file])
                st.success(f"Saved {st.session_state.active_file}")

        with col2:
            if st.button("Run Code"):
                st.session_state.output = run_code(st.session_state.open_files[st.session_state.active_file])

        with col3:
            if st.button("Compile"):
                st.session_state.compile_output = compile_code(st.session_state.active_file)

        # Output Section - Terminal Output
        st.subheader("Terminal Output:")
        st.text_area("Output", st.session_state.output or st.session_state.compile_output, height=250)
