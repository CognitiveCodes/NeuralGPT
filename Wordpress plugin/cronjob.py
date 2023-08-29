import os
import shutil
import datetime

# Set up the paths to the shared databank and the backup directory
shared_databank_path = "e:/repos/database"
backup_dir_path = "e:/repos/database/backup"

# Create the backup directory if it doesn't exist
if not os.path.exists(backup_dir_path):
    os.mkdir(backup_dir_path)

# Set up the backup filename with the current date and time
backup_filename = "shared_databank_backup_{}.zip".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# Create the full path to the backup file
backup_file_path = os.path.join(backup_dir_path, backup_filename)

# Compress the shared databank directory into a zip file
shutil.make_archive(backup_file_path, "zip", shared_databank_path)

# Print a message to confirm that the backup was successful
print("Backup of shared databank created at {}".format(backup_file_path))