#!/bin/bash

# Path to Miniconda installation; adjust if different
MINICONDA_PATH="$HOME/miniconda3"

# Ensure conda is initialized
source "$MINICONDA_PATH/etc/profile.d/conda.sh"

# List all environments
envs=$(conda env list | awk '{print $1}' | grep -v "^#")

# Loop through each environment and remove it
for env in $envs; do
    if [ "$env" != "base" ]; then
        echo "Removing environment: $env"
        conda remove --name "$env" --all -y
    else
        echo "Skipping base environment."
    fi
done

echo "All environments (except base) have been removed."

