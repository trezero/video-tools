#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def batch_rename(folder_path, base_filename):
    # Convert to Path object for better path handling
    folder = Path(folder_path)
    
    # Verify folder exists and is a directory
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory")
        sys.exit(1)
    
    # Get all files in the directory
    files = [f for f in folder.iterdir() if f.is_file()]
    
    # Sort files to ensure consistent ordering
    files.sort()
    
    # Counter for numbering files
    counter = 1
    
    for file in files:
        # Get the original file extension
        original_extension = file.suffix
        
        # Create new filename with padding (e.g., _001)
        new_filename = f"{base_filename}_{counter:03d}{original_extension}"
        new_filepath = folder / new_filename
        
        try:
            file.rename(new_filepath)
            print(f"Renamed: {file.name} -> {new_filename}")
            counter += 1
        except Exception as e:
            print(f"Error renaming {file.name}: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python batchRename.py <folder_path> <base_filename>")
        print("Example: python batchRename.py ./my_videos video")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    base_filename = sys.argv[2]
    
    batch_rename(folder_path, base_filename)

if __name__ == "__main__":
    main()
