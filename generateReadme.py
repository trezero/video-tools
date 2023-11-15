import os

def is_binary(file_path):
    """
    Check if a file is binary. Simple heuristic: If the file contains a null byte, it's binary.
    """
    try:
        with open(file_path, 'rb') as f:
            for chunk in f:
                if b'\0' in chunk:  # Found null byte
                    return True
            return False
    except Exception as e:
        print(f"Error checking if file is binary: {e}")
        return True

def gather_files_content(directory):
    # Define the files to exclude from gathering content
    excluded_files = {'generateReadme.py', '.gitignore', '.DS_Store', 'README.md', '.*'}
    
    # The output file where the content will be stored
    output_file = 'all_files_content.txt'
    
    with open(output_file, 'w') as outfile:
        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file not in excluded_files:
                    file_path = os.path.join(root, file)
                    # Skip binary files
                    if is_binary(file_path):
                        print(f"Skipping binary file: {file}")
                        continue
                    # Write the file path and its content to the output file
                    outfile.write(f"File: {file_path}\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as infile:
                            outfile.write(infile.read())
                            outfile.write("\n\n")  # Add spacing between files
                    except UnicodeDecodeError as e:
                        print(f"Unicode decode error in file {file}: {e}. Skipping file.")
                    except Exception as e:
                        print(f"Error reading file {file}: {e}. Skipping file.")

    print(f"All contents have been written to {output_file}")

# Run the function for the current directory
if __name__ == '__main__':
    gather_files_content('.')
