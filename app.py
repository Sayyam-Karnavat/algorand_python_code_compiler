import streamlit as st
from streamlit_ace import st_ace
import io
import sys
from contextlib import redirect_stdout

# Function to run the Python code and capture output
def run_code(code):
    try:
        # Capture output in a string
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code)
        return f.getvalue()
    except Exception as e:
        return str(e)

# Streamlit Interface
st.title('Python Code Compiler')

# Create an Ace code editor for Python code
code_input = st_ace(
    language='python',               # Specify the language (Python in this case)
    theme='monokai',                  # Choose a theme
    height=400,                       # Set the height of the editor
    font_size=14,                     # Set the font size
    show_gutter=True,                 # Show line numbers
    wrap=True,                        # Enable word wrapping
    placeholder="Write your Python code here...",  # Placeholder text
)

# Button to run the code
if st.button('Run Code'):
    if code_input:
        # Execute the code
        output = run_code(code_input)
        st.subheader("Output:")
        st.code(output, language='python')
    else:
        st.warning("Please write some Python code to run.")
