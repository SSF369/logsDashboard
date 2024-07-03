from flask import Flask, render_template, jsonify
import sqlite3
import re

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect('errors.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            error_details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_error_log(service_name, error_details):
    conn = sqlite3.connect('errors.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO errors (service_name, error_details) VALUES (?, ?)
    ''', (service_name, error_details))
    conn.commit()
    conn.close()

def parse_log_file(file_path):
    logs = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'Service: (\w+).*?Error: (.*)', line)
            if match:
                service_name = match.group(1)
                error_details = match.group(2)
                logs.append({'service_name': service_name, 'error_details': error_details})
    return logs

def count_errors():
    conn = sqlite3.connect('errors.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT service_name, COUNT(*) as error_count FROM errors GROUP BY service_name
    ''')
    error_counts = cursor.fetchall()
    conn.close()
    return error_counts

@app.route('/')
def dashboard():
    error_counts = count_errors()
    return render_template('dashboard.html', error_counts=error_counts)

@app.route('/logs/<service_name>')
def service_logs(service_name):
    conn = sqlite3.connect('errors.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT error_details FROM errors WHERE service_name = ?
    ''', (service_name,))
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

if __name__ == '__main__':
    create_db()
    logs = parse_log_file('logs/example.log')
    for log in logs:
        store_error_log(log['service_name'], log['error_details'])
    app.run(debug=True)
