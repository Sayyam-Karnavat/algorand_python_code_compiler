import os
import subprocess
import re

def compile_to_arc56_json(input_dir, output_dir):
    # Ensure input_dir is an absolute path
    input_dir = os.path.abspath(input_dir)
    
    # Read the content of the file
    try:
        with open(input_dir, "r") as f:
            contract_code = f.read()
    except Exception as e:
        return {"error": f"Failed to read input file: {str(e)}"}

    def extract_class_name(code):
        # Look for class definitions that inherit from ARC4Contract
        match = re.search(r'class\s+(\w+)\s*\(\s*ARC4Contract\s*\)', code)
        return match.group(1) if match else None

    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        output_dir = os.path.abspath(output_dir)  # Ensure absolute path

        # Extract the contract class name
        contract_name = extract_class_name(contract_code)
        if not contract_name:
            return {"error": "Could not extract contract class name"}

        # Construct the output file path
        json_file = os.path.join(output_dir, f"{contract_name}.arc56.json")

        # Compile the contract with --output-arc56 flag
        # Pass the input file path explicitly and set output directory
        command = [
            "algokit", "compile", "py", input_dir, "--output-arc56", "--out-dir", output_dir
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            # Remove cwd to let algokit handle paths explicitly
        )

        # Check for command failure
        if result.returncode != 0:
            return {
                "error": f"Compilation failed: {result.stderr}",
                "stdout": result.stdout
            }

        # Check if the JSON file exists
        if not os.path.exists(json_file):
            # Debug: List files in output_dir to see what was generated
            output_files = os.listdir(output_dir)
            return {
                "error": f"Compiled file {json_file} not found",
                "output_dir_contents": output_files,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        # Read the JSON content
        with open(json_file, "r") as f:
            json_content = f.read()

        # Return success with the JSON content
        return {
            "json_content": json_content,
            "json_file_path": json_file,
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}