import os
import shutil

# Define the directory where the files are located
directory = "/path/to/directory"

# Create a dictionary to store the file extensions and their corresponding subdirectories
file_extensions = {}

# Loop through all the files in the directory
for filename in os.listdir(directory):

    # Get the file extension
    file_extension = os.path.splitext(filename)[1]

    # If the file extension is not in the dictionary, create a new subdirectory for it
    if file_extension not in file_extensions:
        os.mkdir(os.path.join(directory, file_extension[1:]))
        file_extensions[file_extension] = True

    # Move the file to the corresponding subdirectory
    shutil.move(os.path.join(directory, filename), os.path.join(directory, file_extension[1:], filename))