
from flask import Flask, request, jsonify
import subprocess
import os
import io
import traceback
from contextlib import redirect_stdout
from deploy_old import deploy_app  # Assuming this is your deployment logic
from flask_cors import CORS
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

def extract_class_name(code):
    """Extract the first class name from the Python code."""
    for line in code.split('\n'):
        if line.strip().startswith("class "):
            return line.split()[1].split("(")[0]  # Extract class name before '('
    return None

@app.route("/deploy", methods=["POST"])
def deploy_code():
    data = request.json
    code = data.get("code")
    file_path = data.get("file_path")  # Optional, for naming purposes

    if not code:
        return jsonify({"error": "No code provided"}), 400

    temp_dir = None
    temp_file_path = None
    try:
        # Create a temporary directory to store all generated files
        temp_dir = tempfile.mkdtemp()
        
        # Create a temporary file for the Python code
        temp_file_name = os.path.join(temp_dir, "temp_contract.py")
        with open(temp_file_name, "w") as temp_file:
            temp_file.write(code)
        temp_file_path = temp_file_name

        # Compile the contract in the temporary directory
        result = subprocess.run(
            ["algokit", "compile", "py", temp_file_path],
            capture_output=True,
            text=True,
            cwd=temp_dir  # Set the working directory to temp_dir
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Extract the contract class name
        contract_name = extract_class_name(code)
        if not contract_name:
            return jsonify({"error": "Could not extract contract class name"}), 400

        # The JSON file should be in the temp_dir
        json_file = os.path.join(temp_dir, f"{contract_name}.arc32.json")
        if not os.path.exists(json_file):
            return jsonify({"error": f"Compiled file {json_file} not found"}), 500

        # Deploy the compiled contract
        deploy_result = deploy_app(json_file)

        return jsonify({"message": "Deployment successful", "deploy_result": deploy_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the temporary directory and all its contents
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code, {})
        return jsonify({"output": f.getvalue()})
    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0" ,debug=False)