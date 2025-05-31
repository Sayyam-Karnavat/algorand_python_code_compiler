
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


@app.route('/files/save', methods=['POST'])
def save_file():
    """Save code to server"""
    data = request.json
    filename = data.get('filename', 'untitled.py')
    content = data.get('content', '')
    
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': f'File {filename} saved successfully',
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/files/load/<filename>')
def load_file(filename):
    """Load file from server"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/files/list')
def list_files():
    """List all saved files"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.py'):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/files/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete file from server"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        os.remove(filepath)
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/files/download/<filename>')
def download_file(filename):
    """Download file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/packages/install', methods=['POST'])
def install_package():
    """Install Python package (for blockchain libraries)"""
    package_name = request.json.get('package', '')
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                              capture_output=True, text=True, timeout=300)
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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