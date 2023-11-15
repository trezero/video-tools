import subprocess
import csv

# Function to get the list of repositories from the GitHub CLI
def get_repo_list(org_name):
    # Run the GitHub CLI command and capture the output
    result = subprocess.run(
        ["gh", "repo", "list", org_name, "--limit", "1000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Check for errors
    if result.stderr:
        raise Exception("Error fetching repository list: " + result.stderr)
    
    # Split the output by new lines to get individual repository details
    repo_lines = result.stdout.strip().split('\n')
    
    # Extract the repository names
    repo_names = [line.split('\t')[0].split('/')[-1] for line in repo_lines if line]
    
    return repo_names

# Function to write the repository names into a CSV file with three columns
def write_repos_to_csv(repos, csv_file_path):
    # Calculate the number of rows needed for the CSV
    num_rows = len(repos) // 3 + (1 if len(repos) % 3 else 0)

    # Create the CSV rows
    csv_rows = [repos[i*3:(i+1)*3] for i in range(num_rows)]

    # Ensure each row has 3 columns, filling in with empty strings if necessary
    for row in csv_rows:
        while len(row) < 3:
            row.append("")

    # Write the data to a CSV file
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_rows)

# Replace '[org-name]' with your organization name
org_name = 'workflow-intelligence-nexus'

# Define the CSV file path
csv_file_path = 'win_repos.csv'

# Get the repository list
repo_list = get_repo_list(org_name)

# Write the repository names to a CSV file
write_repos_to_csv(repo_list, csv_file_path)

print(f"The CSV file has been created at {csv_file_path}")
