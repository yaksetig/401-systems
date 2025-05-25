from flask import Flask, request, render_template_string, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Circom Audit Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #f8f9fa;
        }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .upload-area { 
            border: 3px dashed #3498db; 
            padding: 40px; 
            text-align: center; 
            margin: 20px 0; 
            border-radius: 10px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover { border-color: #2980b9; background: #f0f8ff; }
        .upload-area.dragover { border-color: #27ae60; background: #f0fff0; }
        textarea { 
            width: 100%; 
            height: 250px; 
            margin: 15px 0; 
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
            resize: vertical;
        }
        textarea:focus { border-color: #3498db; outline: none; }
        .btn { 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 25px;
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: block;
            margin: 20px auto;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(52,152,219,0.4); }
        .btn:disabled { background: #bdc3c7; cursor: not-allowed; transform: none; }
        .result { 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 20px 0; 
            border-left: 5px solid #3498db; 
            border-radius: 5px;
        }
        .error { border-left-color: #e74c3c; background: #fdf2f2; }
        .success { border-left-color: #27ae60; background: #f0fff4; }
        pre { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            font-size: 13px;
        }
        .loading { text-align: center; color: #3498db; }
        .file-info { 
            background: #e8f4fd; 
            padding: 10px; 
            border-radius: 5px; 
            margin: 10px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Circom Security Audit Tool</h1>
        <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
            Upload your .circom file or paste code to check for security vulnerabilities
        </p>
        
        <form id="uploadForm">
            <div class="upload-area" id="uploadArea">
                <input type="file" id="fileInput" accept=".circom" style="display: none;">
                <div>
                    📁 <strong>Click to upload .circom file</strong><br>
                    <small style="color: #7f8c8d;">or drag & drop here</small>
                </div>
            </div>
            
            <div id="fileInfo" class="file-info" style="display: none;"></div>
            
            <textarea 
                id="codeArea" 
                placeholder="Or paste your Circom code here...

Example:
pragma circom 2.0.0;

template Multiplier2() {
    signal input a;
    signal input b;
    signal output c;
    
    c <== a * b;
}

component main = Multiplier2();"
            ></textarea>
            
            <button type="submit" class="btn" id="auditBtn">🔍 Run Security Audit</button>
        </form>
        
        <div id="results"></div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const codeArea = document.getElementById('codeArea');
        const uploadForm = document.getElementById('uploadForm');
        const uploadArea = document.getElementById('uploadArea');
        const results = document.getElementById('results');
        const auditBtn = document.getElementById('auditBtn');
        const fileInfo = document.getElementById('fileInfo');

        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.endsWith('.circom')) {
                alert('Please upload a .circom file');
                return;
            }
            
            fileInfo.style.display = 'block';
            fileInfo.innerHTML = `📄 <strong>${file.name}</strong> (${(file.size/1024).toFixed(1)} KB)`;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                codeArea.value = e.target.result;
            };
            reader.readAsText(file);
        }

        // Form submission
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = codeArea.value.trim();
            
            if (!code) {
                alert('Please provide Circom code to audit');
                return;
            }

            auditBtn.disabled = true;
            auditBtn.textContent = '⏳ Running audit...';
            results.innerHTML = '<div class="result loading"><h3>🔄 Analyzing your Circom code...</h3><p>This may take a few moments</p></div>';

            try {
                const response = await fetch('/audit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    results.innerHTML = `
                        <div class="result success">
                            <h3>✅ Audit Complete!</h3>
                            <pre>${result.output || 'No security issues found! 🎉'}</pre>
                        </div>
                    `;
                } else {
                    results.innerHTML = `
                        <div class="result error">
                            <h3>❌ Audit Error</h3>
                            <pre>${result.error}</pre>
                        </div>
                    `;
                }
            } catch (error) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Network Error</h3>
                        <p>Failed to connect to audit service: ${error.message}</p>
                    </div>
                `;
            } finally {
                auditBtn.disabled = false;
                auditBtn.textContent = '🔍 Run Security Audit';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/audit', methods=['POST'])
def audit():
    try:
        data = request.get_json()
        circom_code = data['code']
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.circom', delete=False) as f:
            f.write(circom_code)
            temp_path = f.name
        
        # Run circomspect (it should be installed via cargo during Docker build)
        result = subprocess.run(
            ['circomspect', temp_path], 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        os.unlink(temp_path)
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout if result.stdout else "Analysis complete - no issues detected!",
            'error': result.stderr if result.returncode != 0 else None
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Audit timed out after 60 seconds'})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'circomspect not found. Installation may have failed.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
