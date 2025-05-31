
from flask import Flask, render_template, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def ide():
    return render_template('ide.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute Python code
        result = subprocess.run(['python', temp_file], 
                              capture_output=True, text=True, timeout=10)
        
        # Clean up
        os.unlink(temp_file)
        
        return jsonify({
            'output': result.stdout,
            'error': result.stderr,
            'success': result.returncode == 0
        })
    except Exception as e:
        return jsonify({
            'output': '',
            'error': str(e),
            'success': False
        })