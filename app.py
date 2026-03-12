from flask import Flask, request, jsonify, Response
import subprocess
import threading
import time
import re
import os

app = Flask(__name__)

# In-memory scan jobs
scan_jobs = {}

@app.route('/')
def index():
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>🧠 Brainiac Scanner v12.0</title>
    <meta name="viewport" content="width=device-width">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:#0a0a1a;color:#fff;font-family:monospace;line-height:1.4;padding:1rem;max-width:1200px;margin:0 auto;}
        h1{color:#00ff88;text-align:center;font-size:2rem;margin-bottom:1rem;}
        .panel{background:#1a1a2e;padding:1.5rem;border-radius:8px;margin:1rem 0;border-left:4px solid #00ff88;}
        textarea{width:100%;height:100px;background:#0f0f1f;color:#fff;border:1px solid #00ff88;border-radius:4px;padding:0.8rem;font-family:monospace;font-size:14px;}
        button{background:#00ff88;color:#000;border:none;padding:0.8rem 1.5rem;border-radius:4px;font-family:monospace;font-weight:bold;cursor:pointer;margin:0.5rem;transition:all 0.2s;}
        button:hover,button:disabled{background:#00cc66;}
        button:disabled{cursor:not-allowed;opacity:0.6;}
        #progress{width:100%;height:8px;background:#0f0f1f;border-radius:4px;overflow:hidden;margin:1rem 0;display:none;}
        #progress div{height:100%;background:linear-gradient(90deg,#00ff88,#ffaa00);width:0%;transition:width 0.3s;}
        pre{background:#0f0f1f;padding:1rem;border-radius:4px;height:300px;overflow:auto;font-size:12px;white-space:pre-wrap;}
        .status{padding:0.4rem 0.8rem;border-radius:20px;font-size:12px;font-weight:bold;display:inline-block;margin:0.5rem;}
        .running{background:#ffaa00;color:#000;}
        .done{background:#00ff88;}
        .error{background:#ff4444;}
    </style>
</head>
<body>
    <h1>🧠 BRAINIAC v12.0 - Enterprise Cloud Scanner</h1>
    <div class="panel">
        <h2>🎯 Enter Targets</h2>
        <textarea id="targets">scanme.nmap.org</textarea>
        <div>
            <button onclick="startScan('quick')">⚡ Quick</button>
            <button onclick="startScan('fast')">🚀 Fast</button>
            <button onclick="startScan('full')">🔥 Full</button>
        </div>
        <div id="progress"><div id="bar"></div></div>
        <div id="status"></div>
    </div>
    <div class="panel">
        <h2>📡 Live Output</h2>
        <pre id="output">Ready to shrink worlds... 👾</pre>
    </div>

    <script>
    let currentJob = null;
    const btns = document.querySelectorAll('button');
    
    async function startScan(type) {
        const targets = document.getElementById('targets').value.trim();
        if(!targets) return alert('Enter targets!');
        
        // Disable buttons
        btns.forEach(b => b.disabled = true);
        document.getElementById('status').innerHTML = '<span class="status running">🚀 SCANNING...</span>';
        document.getElementById('progress').style.display = 'block';
        document.getElementById('output').textContent = `Starting ${type} nmap scan on ${targets}\\n`;
        
        try {
            const res = await fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({targets, scan_type: type})
            });
            const data = await res.json();
            currentJob = data.job_id;
            pollResults();
        } catch(e) {
            document.getElementById('output').textContent += `\\n❌ Network error: ${e}`;
            btns.forEach(b => b.disabled = false);
        }
    }
    
    async function pollResults() {
        if(!currentJob) return;
        try {
            const res = await fetch(`/api/results/${currentJob}`);
            const data = await res.json();
            
            document.getElementById('bar').style.width = data.progress + '%';
            
            if(data.status === 'running') {
                const lines = data.output.slice(-25);
                document.getElementById('output').textContent = lines.join('\\n');
                setTimeout(pollResults, 1000);
            } else {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('output').textContent = data.output.join('\\n');
                
                let statusClass = data.status === 'error' ? 'error' : 'done';
                document.getElementById('status').innerHTML = `<span class="status ${statusClass}">✅ ${data.status.toUpperCase()}</span>`;
                
                btns.forEach(b => b.disabled = false);
                currentJob = null;
            }
        } catch(e) {
            setTimeout(pollResults, 2000);
        }
    }
    </script>
</body>
</html>
    '''
    return Response(html, mimetype='text/html')

@app.route('/api/scan', methods=['POST'])
def scan():
    data = request.json
    target = data['target']
    profile = data['profile']
    
    # Render.com compatible: TCP connect + unprivileged
    base_flags = ['--unprivileged', '-T4', '-Pn']  # No raw sockets, skip host discovery
    
    if profile == 'quick':
        cmd = ['nmap'] + base_flags + ['-F', target]
    elif profile == 'standard':
        cmd = ['nmap'] + base_flags + ['-sV', '--top-ports', '1000', target]
    elif profile == 'full':
        cmd = ['nmap'] + base_flags + ['-sV', '-O', '-A', target]
    elif profile == 'brutal':
        cmd = ['nmap'] + base_flags + ['-sV', '-O', '-A', '--script=vuln', target]
    
    # Rest of function unchanged...
        }
        
        def run_nmap():
            try:
                # Simple, reliable nmap commands
                cmds = {
                    'quick': f'nmap -T4 -F {targets}',
                    'fast': f'nmap -sV -T4 --top-ports 1000 {targets}',
                    'full': f'nmap -sC -sV -O -p- {targets}'
                }
                
                cmd = cmds.get(scan_type, cmds['fast'])
                print(f"Executing: {cmd}")  # Logs
                
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True,
                    bufsize=1, universal_newlines=True
                )
                
                while True:
                    line = proc.stdout.readline()
                    if line == '' and proc.poll() is not None:
                        break
                    if line:
                        scan_jobs[job_id]['output'].append(line.strip())
                        scan_jobs[job_id]['progress'] = min(95, scan_jobs[job_id]['progress'] + 1)
                
                scan_jobs[job_id]['status'] = 'completed'
                scan_jobs[job_id]['progress'] = 100
                
            except Exception as e:
                scan_jobs[job_id]['status'] = 'error'
                scan_jobs[job_id]['output'].append(f"ERROR: {str(e)}")
        
        threading.Thread(target=run_nmap, daemon=True).start()
        return jsonify({'job_id': job_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<job_id>')
def get_results(job_id):
    job = scan_jobs.get(job_id, {'status': 'not_found', 'output': ['Job not found']})
    return jsonify(job)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'jobs': len(scan_jobs)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
