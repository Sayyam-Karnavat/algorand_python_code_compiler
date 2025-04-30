
'''
This is working code of latest implementation of the server 

'''
from flask import Flask, request, jsonify
import io
import traceback
from contextlib import redirect_stdout
from deploy import deploy_app  # Assuming this is your deployment logic
from flask_cors import CORS
import os
import subprocess

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

    try:

        data = request.json
        code = data.get("code")
        file_path = data.get("file_path")  # Optional, for naming purposes

        if not code:
            return jsonify({"error": "No code provided"}), 400


        # Deploy the compiled contract
        deploy_result = deploy_app(smart_contract_code=code)

        
        return jsonify({"message":"Deployment successful", "deploy_result": deploy_result}) , 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    



@app.route("/")
def homepage():
    return "Server is running ..."

