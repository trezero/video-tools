import os
import re

def clean_filename(filename):
    # Replace special characters with safe characters
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def clean_directory(directory):
    for filename in os.listdir(directory):
        clean_name = clean_filename(filename)
        if clean_name != filename:
            os.rename(os.path.join(directory, filename), os.path.join(directory, clean_name))

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    clean_directory(directory)
