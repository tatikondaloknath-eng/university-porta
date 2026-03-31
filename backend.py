from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')
DB_FILE = "database.json"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return jsonify(json.load(file))
    return jsonify([])

@app.route('/api/data', methods=['POST'])
def save_data():
    try:
        data = request.json
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        return jsonify({"status": "success", "message": "Saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))