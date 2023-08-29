import os
import shutil
import datetime
import time

# Define the path to the database file
database_path = 'E:/xampp/htdocs/wordpress/wp-content/plugins/neuralgpt-chatbot/universal.db'

# Define the path to the backup directory
backup_dir = 'e:/ai'

# Define the backup interval in seconds (e.g. 24 hours)
backup_interval = 86400

# Define a function to create a backup of the database
def backup_database():
    # Create a timestamp for the backup file name
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Create the backup file name
    backup_file = 'database_backup_' + timestamp + '.db'
    # Create the full path to the backup file
    backup_path = backup_dir + backup_file
    # Copy the database file to the backup directory
    shutil.copy(database_path, backup_path)

# Define a function to restore the database from a backup
def restore_database(backup_file):
    # Create the full path to the backup file
    backup_path = backup_dir + backup_file
    # Copy the backup file to the database directory
    shutil.copy(backup_path, database_path)

# Define a function to run the backup process at set intervals
def run_backup_process():
    while True:
        # Wait for the backup interval to elapse
        time.sleep(backup_interval)
        # Create a backup of the database
        backup_database()

# Run the backup process in a separate thread
backup_thread = threading.Thread(target=run_backup_process)
backup_thread.start()