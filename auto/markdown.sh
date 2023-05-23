#!/bin/bash

# Set the path to the JSON file
json_file="path/to/json/file.json"

# Set the path to the output Markdown file
markdown_file="E:/AI/NeuralGPT/NeuralGPT/output.md"

# Parse the JSON file and extract the data
data=$(jq -r '.data' $json_file)

# Convert the data to Markdown format
markdown=$(echo $data | pandoc -f html -t markdown)

# Write the Markdown to the output file
echo $markdown > $markdown_file