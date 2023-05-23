import os

# Set the path to the directory where the text file will be saved
directory_path = r"E:\AI\NeuralGPT\NeuralGPT"

# Set the path to the file containing the content produced by Cognosys
content_file_path = r"path\to\content\file"

# Read the content from the file
with open(content_file_path, "r") as file:
    content = file.read()

# Set the name of the text file
file_name = "cognosys_content.txt"

# Set the path to the text file
file_path = os.path.join(directory_path, file_name)

# Write the content to the text file
with open(file_path, "w") as file:
    file.write(content)