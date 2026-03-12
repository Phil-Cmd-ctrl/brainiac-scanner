from flask import Flask, request, jsonify, Response
import subprocess
import json
import threading
import time
from collections import defaultdict

app = Flask(__name__)

# Global scan state
scan_results = {}
current_scan = None

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🧠 Brainiac Scanner</title>
    <style>
        body { background: #000011; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; }
        h1 { text-align: center; color: #ff0040; text-shadow: 0 0 20px #ff0040; animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.7} }
        input[type="text"] { width: 70%; padding: 15px; background: #111; border: 2px solid #00ff41; color: #00ff41; font-size: 16px; }
        button { padding: 15px 25px; margin: 5px; background: #00ff41; color: #000; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #ff0040; color: #fff; }
        #output { background: #000; border: 2px solid #333; height: 500px; overflow-y: scroll; padding: 20px; white-space: pre-wrap; font-size: 14px; margin-top: 20px; }
        .status { text-align: center; color: #ffaa00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 BRAINIAC v12.0 - Shrinking Worlds...</h1>
        <div style="text-align: center;">
            <input type="text" id="target" placeholder="scanme.nmap.org" value="scanme.nmap.org">
            <br><br>
            <button onclick="startScan('quick')">⚡ Quick</button>
            <button onclick="startScan('standard')">🚀 Standard</button>
            <button onclick="startScan('full')">🔥 Full</button>
            <button onclick="startScan('brutal')">💀 Brutal</button>
        </div>
        <div id="status" class="status" style="display:none;">Scanning...</div>
        <div id="output">Ready to shrink worlds... 👾</div>
    </div>

    <script>
        const output = document.getElementById('output');
        function startScan(profile) {
            const target = document.getElementById('target').value;
            document.getElementById('status').style.display = 'block';
            output.innerHTML = 'Launching scan: ' + profile.toUpperCase() + ' on ' + target + '\\n';
            
            fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target, profile: profile})
            }).then(r => r.json()).then(data => {
                document.getElementById('status').style.display = 'none';
            });
            
            // Poll results
            const interval = setInterval(() => {
                fetch('/api/results').then(r => r.json()).then(data => {
                    output.innerHTML = data.output || 'Waiting...';
                    if (data.complete) clearInterval(interval);
                });
            }, 1000);
        }
    </script>
</body>
</html>
'''

@app.route('/api/scan', methods=['POST'])
def scan():
    global current_scan
    data = request.get_json()
    target = data['target']
    profile = data['profile']
    
    # Render-safe nmap commands
    if profile == 'quick':
        cmd = ['nmap', '--unprivileged', '-T4', '-Pn', '-F', target]
    elif profile == 'standard':
        cmd = ['nmap', '--unprivileged', '-T4', '-Pn', '-sV', '--top-ports', '1000', target]
    elif profile == 'full':
        cmd = ['nmap', '--unprivileged', '-T4', '-Pn', '-sV', '-A', target]
    else:  # brutal
        cmd = ['nmap', '--unprivileged', '-T4', '-Pn', '-sV', '--script=vuln', target]
    
    scan_results[target] = {'output': '', 'complete': False, 'profile': profile}
    current_scan = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True, bufsize=1
    )
    
    def stream_output():
        for line in current_scan.stdout:
            scan_results[target]['output'] += line
        scan_results[target]['complete'] = True
    
    threading.Thread(target=stream_output, daemon=True).start()
    return jsonify({'status': 'started', 'target': target})

@app.route('/api/results')
def results():
    # Return latest scan or empty
    for target in scan_results:
        return jsonify(scan_results[target])
    return jsonify({'output': 'No active scans', 'complete': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
