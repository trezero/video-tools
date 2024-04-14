import csv
import re
import sys
from datetime import datetime

def clean_contact_info(contact_row, headers):
    """
    Clean a contact's information and return a dict with Outlook-compatible headers.
    :param contact_row: A list of fields for the contact.
    :param headers: A list of headers to use in the Outlook CSV.
    :return: A dict with cleaned contact information.
    """
    contact_info = {}
    for header in headers:
        contact_info[header] = ''

    # Assuming contact_row follows a certain structure, update the dictionary
    # accordingly. This will vary depending on the structure of your CSV.
    # The following is a generic example and should be tailored to your data:
    contact_info['First Name'] = re.sub(r'[^\x00-\x7F]+',' ', contact_row[0]).strip()
    contact_info['Last Name'] = re.sub(r'[^\x00-\x7F]+',' ', contact_row[1]).strip()
    contact_info['E-mail Address'] = contact_row[2]  # Assuming 3rd column is the email
    # Add more fields as per your CSV structure

    return contact_info

def clean_and_format_csv(input_csv, output_csv, headers):
    """
    Clean and format CSV data for Outlook import.
    :param input_csv: Path to the input CSV file.
    :param output_csv: Path to the output CSV file.
    :param headers: The headers for the Outlook CSV format.
    """
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        contacts = [clean_contact_info(row, headers) for row in reader]

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(contacts)

    print(f"Cleaned and formatted CSV saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleanContacts.py path_to_your_input.csv")
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    output_csv_path = f"{input_csv_path.rsplit('.', 1)[0]}-Clean-{timestamp}.csv"

    # Define the headers as required by Outlook
    outlook_headers = [
        'First Name', 'Middle Name', 'Last Name', 'Title', 'Suffix',
        'Nickname', 'E-mail Address', 'E-mail 2 Address', 'E-mail 3 Address',
        'Home Phone', 'Business Phone', 'Business Phone 2', 'Mobile Phone',
        'Company', 'Home Street', 'Home City', 'Home State',
        'Home Postal Code', 'Home Country/Region', 'Web Page',
        'Birthday', 'Anniversary', 'Notes'
    ]

    clean_and_format_csv(input_csv_path, output_csv_path, outlook_headers)
