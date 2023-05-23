#!/bin/bash

# Set the input CSV file path
input_file="example.csv"

# Set the output Markdown file path
output_file="E:/AI/NeuralGPT/NeuralGPT/table.md"

# Read the CSV file and generate a Markdown table
while read line
do
    # Replace commas with pipes for Markdown table formatting
    row=$(echo $line | sed 's/,/ | /g')

    # Add Markdown table formatting to the row
    if [ -z "$header" ]
    then
        # The first row is the header
        header="$row"
        separator=$(echo "$header" | sed 's/[^|]/-/g')
        table="$header\n$separator"
    else
        # All other rows are data
        table="$table\n$row"
    fi
done < "$input_file"

# Save the Markdown table to the output file
echo -e "$table" > "$output_file"