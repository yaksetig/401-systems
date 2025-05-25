from flask import Flask, request, render_template_string, jsonify
import os
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Circom Security Audit Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { 
            max-width: 1000px;
            margin: 0 auto;
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p { 
            opacity: 0.9; 
            font-size: 1.1rem;
        }
        
        .content { padding: 40px; }
        
        .upload-area { 
            border: 3px dashed #3498db; 
            padding: 50px; 
            text-align: center; 
            margin: 30px 0; 
            border-radius: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
            background: #f8f9fa;
        }
        
        .upload-area:hover { 
            border-color: #2980b9; 
            background: #e3f2fd;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover { 
            border-color: #27ae60; 
            background: #e8f5e8;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        textarea { 
            width: 100%; 
            height: 300px; 
            margin: 20px 0; 
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s ease;
            background: #fafafa;
        }
        
        textarea:focus { 
            border-color: #3498db; 
            outline: none;
            background: white;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
        }
        
        .btn { 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            color: white; 
            padding: 16px 40px; 
            border: none; 
            border-radius: 50px;
            cursor: pointer; 
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: block;
            margin: 30px auto;
            box-shadow: 0 4px 15px rgba(52,152,219,0.3);
        }
        
        .btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(52,152,219,0.4);
        }
        
        .btn:disabled { 
            background: #bdc3c7; 
            cursor: not-allowed; 
            transform: none;
            box-shadow: none;
        }
        
        .result { 
            background: #f8f9fa; 
            padding: 25px; 
            margin: 25px 0; 
            border-left: 5px solid #3498db; 
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .error { 
            border-left-color: #e74c3c; 
            background: linear-gradient(135deg, #fdf2f2, #fce4ec);
        }
        
        .success { 
            border-left-color: #27ae60; 
            background: linear-gradient(135deg, #f0fff4, #e8f5e8);
        }
        
        .warning { 
            border-left-color: #f39c12; 
            background: linear-gradient(135deg, #fff8e1, #ffecb3);
        }
        
        pre { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 20px; 
            border-radius: 10px; 
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
            margin: 15px 0;
        }
        
        .loading { 
            text-align: center; 
            color: #3498db;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .file-info { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 15px 0;
            font-size: 14px;
            border-left: 4px solid #2196f3;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #f0f0f0;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #3498db;
            transform: translateY(-2px);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
        }
        
        .badge-error { background: #ffebee; color: #c62828; }
        .badge-warning { background: #fff3e0; color: #ef6c00; }
        .badge-info { background: #e3f2fd; color: #1565c0; }
        .badge-success { background: #e8f5e8; color: #2e7d32; }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #e0e0e0;
        }
        
        .demo-note {
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Circom Security Audit Tool</h1>
            <p>Advanced static analysis for Circom zero-knowledge circuits</p>
        </div>
        
        <div class="content">
            <div class="demo-note">
                <strong>🚀 Demo Version</strong> - This tool performs enhanced static analysis based on circomspect's methodology
            </div>
            
            <form id="uploadForm">
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".circom" style="display: none;">
                    <div class="upload-icon">📁</div>
                    <div>
                        <strong>Click to upload .circom file</strong><br>
                        <small style="color: #7f8c8d;">or drag & drop here • Supports .circom files</small>
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
                
                <button type="submit" class="btn" id="auditBtn">
                    🔍 Run Security Audit
                </button>
            </form>
            
            <div id="results"></div>
        </div>
        
        <div class="footer">
            <p>Powered by enhanced static analysis • Inspired by <a href="https://github.com/trailofbits/circomspect" target="_blank">circomspect</a></p>
        </div>
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
            fileInfo.innerHTML = `
                <strong>📄 ${file.name}</strong> 
                <span class="badge badge-info">${(file.size/1024).toFixed(1)} KB</span>
                <span class="badge badge-success">Ready for analysis</span>
            `;
            
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
            auditBtn.innerHTML = '⏳ Analyzing...';
            
            results.innerHTML = `
                <div class="result loading">
                    <h3>🔄 Running Static Analysis...</h3>
                    <p>Checking for security vulnerabilities and code quality issues</p>
                </div>
            `;

            try {
                const response = await fetch('/audit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code})
                });
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Network Error</h3>
                        <p>Failed to connect to audit service: ${error.message}</p>
                    </div>
                `;
            } finally {
                auditBtn.disabled = false;
                auditBtn.innerHTML = '🔍 Run Security Audit';
            }
        });
        
        function displayResults(result) {
            if (!result.success) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Analysis Error</h3>
                        <pre>${result.error}</pre>
                    </div>
                `;
                return;
            }
            
            const analysis = result.analysis;
            let html = '';
            
            // Statistics
            html += `
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">${analysis.issues.length}</div>
                        <div class="stat-label">Issues Found</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${analysis.warnings.length}</div>
                        <div class="stat-label">Warnings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${analysis.input_signals.length}</div>
                        <div class="stat-label">Input Signals</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${analysis.output_signals.length}</div>
                        <div class="stat-label">Output Signals</div>
                    </div>
                </div>
            `;
            
            // Issues
            if (analysis.issues.length > 0) {
                html += `
                    <div class="result error">
                        <h3>❌ Critical Issues Found</h3>
                        ${analysis.issues.map(issue => `
                            <div style="margin: 10px 0; padding: 10px; background: rgba(231,76,60,0.1); border-radius: 5px;">
                                <strong>${issue.type}:</strong> ${issue.message}
                                ${issue.line ? `<br><small>Line ${issue.line}</small>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            // Warnings  
            if (analysis.warnings.length > 0) {
                html += `
                    <div class="result warning">
                        <h3>⚠️ Warnings</h3>
                        ${analysis.warnings.map(warning => `
                            <div style="margin: 10px 0; padding: 10px; background: rgba(243,156,18,0.1); border-radius: 5px;">
                                <strong>${warning.type}:</strong> ${warning.message}
                                ${warning.line ? `<br><small>Line ${warning.line}</small>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            // Circuit info
            if (analysis.input_signals.length > 0 || analysis.output_signals.length > 0) {
                html += `
                    <div class="result success">
                        <h3>📊 Circuit Analysis</h3>
                        ${analysis.input_signals.length > 0 ? `
                            <p><strong>Input Signals:</strong> ${analysis.input_signals.map(s => `<span class="badge badge-info">${s}</span>`).join('')}</p>
                        ` : ''}
                        ${analysis.output_signals.length > 0 ? `
                            <p><strong>Output Signals:</strong> ${analysis.output_signals.map(s => `<span class="badge badge-success">${s}</span>`).join('')}</p>
                        ` : ''}
                        ${analysis.components.length > 0 ? `
                            <p><strong>Components:</strong> ${analysis.components.map(c => `<span class="badge badge-info">${c}</span>`).join('')}</p>
                        ` : ''}
                    </div>
                `;
            }
            
            if (analysis.issues.length === 0 && analysis.warnings.length === 0) {
                html += `
                    <div class="result success">
                        <h3>✅ Analysis Complete</h3>
                        <p>No critical security issues detected! Your circuit passed basic static analysis checks.</p>
                        <small>Note: This demo performs enhanced static analysis. For comprehensive security auditing, consider using the full circomspect tool.</small>
                    </div>
                `;
            }
            
            results.innerHTML = html;
        }
    </script>
</body>
</html>
'''

def analyze_circom_code(code):
    """Enhanced Circom analysis based on circomspect methodology"""
    issues = []
    warnings = []
    lines = code.split('\n')
    
    # Check for pragma
    pragma_found = False
    for i, line in enumerate(lines, 1):
        if re.search(r'pragma\s+circom\s+\d+\.\d+\.\d+', line):
            pragma_found = True
            break
    
    if not pragma_found:
        issues.append({
            'type': 'Missing Pragma',
            'message': 'Missing or invalid pragma directive. Should be "pragma circom X.Y.Z;"',
            'line': 1
        })
    
    # Extract signals and components
    input_signals = []
    output_signals = []
    private_signals = []
    components = []
    
    for i, line in enumerate(lines, 1):
        # Find signals
        input_match = re.findall(r'signal\s+input\s+(\w+)', line)
        output_match = re.findall(r'signal\s+output\s+(\w+)', line)
        private_match = re.findall(r'signal\s+private\s+(\w+)', line)
        component_match = re.findall(r'component\s+(\w+)\s*=', line)
        
        input_signals.extend(input_match)
        output_signals.extend(output_match)
        private_signals.extend(private_match)
        components.extend(component_match)
        
        # Check for unconstrained assignments
        if '<--' in line:
            warnings.append({
                'type': 'Unconstrained Assignment',
                'message': 'Found unconstrained assignment operator "<--". Ensure signal is properly constrained elsewhere.',
                'line': i
            })
        
        # Check for division without constraints
        if '/' in line and 'assert' not in line and '//' not in line:
            warnings.append({
                'type': 'Potential Division Issue',
                'message': 'Division found without explicit zero-check constraint. Consider adding assertions.',
                'line': i
            })
        
        # Check for shadowing
        if re.search(r'(var|signal)\s+(\w+)', line):
            var_name = re.search(r'(var|signal)\s+(\w+)', line).group(2)
            if var_name in ['input', 'output', 'signal', 'component', 'template']:
                warnings.append({
                    'type': 'Variable Shadowing',
                    'message': f'Variable "{var_name}" shadows a reserved keyword.',
                    'line': i
                })
        
        # Check for constant conditions
        if_match = re.search(r'if\s*\(\s*(true|false|\d+)\s*\)', line)
        if if_match:
            warnings.append({
                'type': 'Constant Condition',
                'message': f'Condition always evaluates to {if_match.group(1)}. Consider removing or fixing.',
                'line': i
            })
        
        # Check for unsafe Num2Bits usage
        if 'Num2Bits(' in line and not 'Num2Bits_strict(' in line:
            warnings.append({
                'type': 'Unsafe Num2Bits',
                'message': 'Consider using Num2Bits_strict for safer bit conversion.',
                'line': i
            })
        
        # Check for LessThan issues
        if 'LessThan(' in line:
            warnings.append({
                'type': 'LessThan Usage',
                'message': 'Ensure inputs to LessThan are properly constrained to be non-negative.',
                'line': i
            })
    
    # Check overall structure
    if not re.search(r'template\s+\w+', code):
        issues.append({
            'type': 'Missing Template',
            'message': 'No template definition found in the circuit.',
            'line': None
        })
    
    if not input_signals and not output_signals:
        warnings.append({
            'type': 'No I/O Signals',
            'message': 'No input or output signals detected. This may not be a functional circuit.',
            'line': None
        })
    
    # Check for loops without bounds
    for i, line in enumerate(lines, 1):
        if re.search(r'for\s*\(\s*var\s+\w+\s*=\s*\d+\s*;\s*\w+\s*<\s*\w+', line):
            warnings.append({
                'type': 'Loop Bounds',
                'message': 'Loop with variable bounds detected. Ensure bounds are properly constrained.',
                'line': i
            })
    
    # Check complexity (simple heuristic)
    complexity_score = code.count('if ') + code.count('for ') + code.count('while ')
    if complexity_score > 10:
        warnings.append({
            'type': 'High Complexity',
            'message': f'High cyclomatic complexity ({complexity_score}). Consider refactoring into smaller components.',
            'line': None
        })
    
    return {
        'issues': issues,
        'warnings': warnings,
        'input_signals': input_signals,
        'output_signals': output_signals,
        'private_signals': private_signals,
        'components': components,
        'complexity': complexity_score
    }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/audit', methods=['POST'])
def audit():
    try:
        data = request.get_json()
        circom_code = data['code']
        
        # Run our enhanced analysis
        analysis = analyze_circom_code(circom_code)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Analysis error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
