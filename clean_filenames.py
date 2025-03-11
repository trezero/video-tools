import os
import re

def clean_filename(filename):
    # Split filename into name and extension
    name_parts = filename.rsplit('.', 1)
    name = name_parts[0]
    extension = name_parts[1] if len(name_parts) > 1 else ''
    
    # Replace special characters with underscores
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    # Combine name and extension
    if extension:
        return f"{name}.{extension}"
    else:
        return name

def clean_directory(directory):
    for filename in os.listdir(directory):
        clean_name = clean_filename(filename)
        if clean_name != filename:
            os.rename(os.path.join(directory, filename), os.path.join(directory, clean_name))

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    clean_directory(directory)
