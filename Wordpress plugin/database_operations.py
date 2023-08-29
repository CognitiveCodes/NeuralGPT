# Import necessary libraries
import sqlite3
from flask import Flask, request, jsonify

# Create a Flask app
app = Flask(__name__)

# Connect to the universal database
conn = sqlite3.connect('universal.db')
c = conn.cursor()

# Create a table for the universal database
c.execute('''CREATE TABLE IF NOT EXISTS data
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             user TEXT NOT NULL,
             data TEXT NOT NULL,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

# Define routes for adding, updating, and retrieving data
@app.route('/add_data', methods=['POST'])
def add_data():
    # Get data from request
    user = request.form['user']
    data = request.form['data']
    
    # Insert data into the database
    c.execute("INSERT INTO data (user, data) VALUES (?, ?)", (user, data))
    conn.commit()
    
    # Return success message
    return jsonify({'message': 'Data added successfully!'})

@app.route('/update_data', methods=['PUT'])
def update_data():
    # Get data from request
    id = request.form['id']
    data = request.form['data']
    
    # Update data in the database
    c.execute("UPDATE data SET data = ? WHERE id = ?", (data, id))
    conn.commit()
    
    # Return success message
    return jsonify({'message': 'Data updated successfully!'})

@app.route('/get_data', methods=['GET'])
def get_data():
    # Get data from request
    user = request.args.get('user')
    
    # Retrieve data from the database
    c.execute("SELECT * FROM data WHERE user = ?", (user,))
    data = c.fetchall()
    
    # Return data as JSON
    return jsonify({'data': data})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)