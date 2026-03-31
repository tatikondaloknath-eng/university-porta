from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import json
import os

app = Flask(__name__, static_folder='.')

# --- STEP 1: DATABASE CONFIGURATION ---
# Replace these values with the credentials from your MySQL provider (e.g., Aiven or Railway)
db_config = {
    'host': 'your-mysql-host.com',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'defaultdb',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- STEP 2: TABLE SETUP ---
def setup_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Creates the table to store your university/hostel JSON data if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_table (
                id INT PRIMARY KEY,
                json_data LONGTEXT
            )
        """)
        # Ensure at least one row exists to prevent "Not Found" errors on first load
        cursor.execute("INSERT IGNORE INTO student_table (id, json_data) VALUES (1, '[]')")
        conn.commit()
        cursor.close()
        conn.close()
        print("Database setup complete.")
    except Exception as e:
        print(f"Error setting up database: {e}")

# Run the setup when the script starts
setup_database()

# --- STEP 3: ROUTES ---

@app.route('/')
def index():
    # Serves your main HTML file
    return send_from_directory('.', 'index.html.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Retrieves the stored JSON string for ID 1
        cursor.execute("SELECT json_data FROM student_table WHERE id = 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return jsonify(json.loads(result[0]))
        return jsonify([])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data', methods=['POST'])
def save_data():
    try:
        # Convert the incoming JSON object to a string for MySQL storage
        data = json.dumps(request.json)
        conn = get_db_connection()
        cursor = conn.cursor()
        # REPLACING the old data with the new updated list
        cursor.execute("UPDATE student_table SET json_data = %s WHERE id = 1", (data,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Saved to MySQL Cloud!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- STEP 4: RENDER DEPLOYMENT CONFIG ---
if __name__ == '__main__':
    # Render assigns a dynamic port; this line ensures the app listens correctly
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
