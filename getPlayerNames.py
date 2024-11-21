import os
import json

def collect_player_names(base_folder, script_dir):
    # Set the path for the JSON file in the same directory as the script
    json_file = os.path.join(script_dir, "playerNames.json")

    # List to store player names
    player_names = set()

    # Check if the JSON file already exists
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            existing_names = json.load(f)
            player_names.update(existing_names)
    
    # Add new unique player names from the folder structure
    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if os.path.isdir(folder_path):  # Ensure it is a folder
            player_names.add(folder)
    
    # Save the unique player names back to the JSON file
    with open(json_file, 'w') as f:
        json.dump(sorted(player_names), f, indent=4)
    print(f"playerNames.json updated with {len(player_names)} unique player names.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate or update playerNames.json with unique player names.")
    parser.add_argument('folder', type=str, help="Path to the base folder containing player folders")
    args = parser.parse_args()

    # Get the script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))

    collect_player_names(args.folder, script_dir)
