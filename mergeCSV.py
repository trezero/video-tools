import csv
import os
import sys

def merge_csv(folder_path):
    # Get all CSV files in the folder
    csv_files = [f for f in sorted(os.listdir(folder_path)) if f.endswith('.csv')]
    
    # Output file
    output_file = "merged_output.csv"

    # Open output file in write mode
    with open(output_file, 'w', newline='') as fileout:
        writer = csv.writer(fileout)

        for file in csv_files:
            with open(os.path.join(folder_path, file), 'r') as infile:
                reader = csv.reader(infile)

                # Skip header for all but the first file
                if csv_files.index(file) != 0:
                    next(reader, None)  

                # Write rows to output file
                for row in reader:
                    writer.writerow(row)

    print(f"Merged CSV created as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mergeCSV.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    merge_csv(folder_path)
