import subprocess
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BPFCoBrain Dashboard</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #00ff66; padding: 20px; }
        input { background: #333; color: #fff; border: 1px solid #00ff66; padding: 10px; width: 300px; }
        button { background: #00ff66; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        pre { background: #111; padding: 15px; border: 1px solid #333; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>BPFCoBrain Dashboard</h1>
    <div>
        <input type="text" id="query" placeholder="Enter query (e.g. capitec)">
        <button onclick="runSearch()">Search</button>
    </div>
    <h3>Search Results:</h3>
    <pre id="output">System ready. Enter query above.</pre>

    <script>
        async function runSearch() {
            const q = document.getElementById('query').value;
            document.getElementById('output').innerText = 'Searching...';
            const res = await fetch('/search?q=' + encodeURIComponent(q));
            const data = await res.json();
            document.getElementById('output').innerText = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No query provided"})
    try:
        res = subprocess.run(
            ["python", "query_cli.py", query, "--format", "json"],
            capture_output=True,
            text=True,
            cwd=r"C:\BPFCo\BPFCoBrain"
        )
        return res.stdout if res.stdout else jsonify({"status": "no results", "stderr": res.stderr})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

