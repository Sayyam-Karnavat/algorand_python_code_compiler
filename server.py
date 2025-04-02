from flask import Flask, request, jsonify
import subprocess
import os
from deploy import deploy_app

app = Flask(__name__)

def extract_class_name(file_path):
    """Extract the first class name from the Python file to determine the contract name."""
    with open(file_path, "r") as f:
        for line in f:
            if line.strip().startswith("class "):
                return line.split()[1].split("(")[0]  # Extract the class name before '('
    return None

@app.route("/deploy", methods=["POST"])
def deploy_code():
    data = request.json
    file_path = data.get("file_path")

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 400

    try:
        # Compile the contract
        result = subprocess.run(["algokit", "compile", "py", file_path], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Extract the contract class name to determine JSON filename
        contract_name = extract_class_name(file_path)
        if not contract_name:
            return jsonify({"error": "Could not extract contract class name"}), 400

        json_file = f"{contract_name}.arc32.json"

        # Deploy the compiled contract
        deploy_result = deploy_app(json_file)

        return jsonify({"message": "Deployment successful", "deploy_result": deploy_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False , port=9999)