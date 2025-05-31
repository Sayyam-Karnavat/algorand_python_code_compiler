
from flask import Flask, render_template, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)


# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload
UPLOAD_FOLDER = 'uploads'
TEMPLATES_FOLDER = 'code_templates'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)



@app.route('/')
def ide():
    return render_template('ide.html')


@app.route('/ide/<theme>')
def ide_with_theme(theme):
    """Load IDE with specific theme (light/dark)"""
    return render_template('ide.html', theme=theme)


@app.route('/run/blockchain', methods=['POST'])
def run_blockchain_code():
    """Execute blockchain Python code with additional libraries"""
    code = request.json.get('code', '')
    return execute_code(code, 'blockchain')


def execute_code(code, code_type='python'):
    """Common code execution function"""
    if not code.strip():
        return jsonify({
            'output': '',
            'error': 'No code provided',
            'success': False
        })
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Set environment variables for blockchain libraries
        env = os.environ.copy()
        if code_type == 'blockchain':
            env['PYTHONPATH'] = env.get('PYTHONPATH', '') + ':./blockchain_libs'
        
        # Execute with timeout
        result = subprocess.run([sys.executable, temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=30,  # Increased timeout for blockchain
                              env=env)
        
        # Clean up
        os.unlink(temp_file)
        
        return jsonify({
            'output': result.stdout,
            'error': result.stderr,
            'success': result.returncode == 0,
            'execution_time': datetime.now().isoformat()
        })
        
    except subprocess.TimeoutExpired:
        if 'temp_file' in locals():
            os.unlink(temp_file)
        return jsonify({
            'output': '',
            'error': 'Code execution timed out (30 seconds limit)',
            'success': False
        })
    except Exception as e:
        if 'temp_file' in locals():
            os.unlink(temp_file)
        return jsonify({
            'output': '',
            'error': f'Execution error: {str(e)}',
            'success': False
        })



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