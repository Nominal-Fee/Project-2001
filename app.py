from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'merged_database.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # to return dicts easily
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Return the last modified time of the database to check for updates."""
    try:
        mtime = os.path.getmtime(DB_FILE)
        return jsonify({'mtime': mtime})
    except FileNotFoundError:
        return jsonify({'mtime': 0})

@app.route('/api/data')
def data():
    """Fetch the latest data from the database."""
    try:
        conn = get_db_connection()
        merged_cur = conn.cursor()
        merged_cur.execute('SELECT * FROM merged_data')
        merged_data = [dict(row) for row in merged_cur.fetchall()]

        summary_cur = conn.cursor()
        summary_cur.execute('SELECT * FROM region_summary')
        region_summary = [dict(row) for row in summary_cur.fetchall()]
        
        conn.close()
        
        return jsonify({
            'merged_data': merged_data,
            'region_summary': region_summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
