#Extract proxy filenames from iconik search JSON

import json
import csv
import sys

# Check if the user has provided a file path as an argument
if len(sys.argv) < 2:
    print("Usage: python script.py <path_to_json_file>")
    sys.exit(1)

json_file_path = sys.argv[1]

# Load JSON data from the file specified by the user
try:
    with open(json_file_path, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"File not found: {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Invalid JSON in file: {json_file_path}")
    sys.exit(1)

# Filter out the files with '-lowres' in their name
def filter_lowres_files(objects):
    lowres_files = []
    for obj in objects:
        for proxy in obj.get('proxies', []):
            if '-lowres' in proxy.get('name', '').lower():
                lowres_files.append(proxy['name'])
    return lowres_files

# Extract the objects from the data
objects = data.get('objects', [])

# Get the list of '-lowres' files
lowres_files = filter_lowres_files(objects)

# Write the list to a CSV file
csv_filename = 'lowres_files.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile)
    filewriter.writerow(['Filename'])  # Column header
    for filename in lowres_files:
        filewriter.writerow([filename])

print(f"CSV file '{csv_filename}' has been created with {len(lowres_files)} entries.")
