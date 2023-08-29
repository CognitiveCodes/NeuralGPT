import os
import time
import shutil
import sqlite3

# Define the local data storage directory
local_dir = "e:/ai"

# Define the universal database location
db_file = "E:/xampp/htdocs/wordpress/wp-content/plugins/neuralgpt-chatbot/universal.db"

# Define the synchronization interval (in seconds)
sync_interval = 3600

universal_storage_dir = "E:/AI/NeuralGPT/NeuralGPT"

def connect_to_database():
    # Connect to the universal database
    conn = sqlite3.connect(db_file)
    return conn

def synchronize_data():
    # Connect to the universal database
    conn = connect_to_database()
    c = conn.cursor()

    # Get a list of files in the local data storage directory
    local_files = os.listdir(local_dir)

    # Get a list of files in the universal database
    c.execute("SELECT filename FROM files")
    db_files = c.fetchall()

    # Compare the two lists and update the database as needed
    for filename in local_files:
        if filename not in db_files:
            # Add the file to the database
            c.execute("INSERT INTO files (filename) VALUES (?)", (filename,))
            conn.commit()

            # Copy the file to the universal storage location
            shutil.copy(os.path.join(local_dir, filename), os.path.join(universal_storage_dir, filename))
        else:
            # Check if the file has been modified
            local_mtime = os.path.getmtime(os.path.join(local_dir, filename))
            c.execute("SELECT mtime FROM files WHERE filename=?", (filename,))
            db_mtime = c.fetchone()[0]

            if local_mtime > db_mtime:
                # Update the file in the database
                c.execute("UPDATE files SET mtime=? WHERE filename=?", (local_mtime, filename))
                conn.commit()

                # Copy the file to the universal storage location
                shutil.copy(os.path.join(local_dir, filename), os.path.join(universal_storage_dir, filename))

    # Close the database connection
    conn.close()

