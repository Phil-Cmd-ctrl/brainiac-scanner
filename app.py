from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import threading
import queue
from brainiac_gui import BrainiacScanner  # Import your GUI logic
import os

app = Flask(__name__)

# Global scan queue
scan_queue = queue.Queue()
scan_results = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.json
    targets = data['targets']
    scan_type = data.get('scan_type', 'standard')
    
    # Queue scan job
    job_id = f"scan_{len(scan_results)}"
    scan_results[job_id] = {'status': 'running', 'output': [], 'progress': 0}
    
    def run_scan():
        try:
            cmd = f"nmap {scan_type} {targets}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    scan_results[job_id]['output'].append(output.strip())
                    scan_results[job_id]['progress'] = min(100, scan_results[job_id]['progress'] + 1)
            
            scan_results[job_id]['status'] = 'completed'
        except Exception as e:
            scan_results[job_id]['status'] = 'error'
            scan_results[job_id]['error'] = str(e)
    
    threading.Thread(target=run_scan, daemon=True).start()
    return jsonify({'job_id': job_id})

@app.route('/api/results/<job_id>')
def get_results(job_id):
    return jsonify(scan_results.get(job_id, {}))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
