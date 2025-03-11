#!/bin/bash

# Script to check if conda and Python 3.10 are installed
# If not, installs Miniconda and Python 3.10
# Designed for Ubuntu 22.04

echo "Checking for conda installation..."

# Check if conda is installed
if command -v conda &> /dev/null; then
    echo "conda is already installed."
    CONDA_INSTALLED=true
else
    echo "conda is not installed."
    CONDA_INSTALLED=false
fi

# Check if Python 3.10 is installed
echo "Checking for Python 3.10 installation..."
if command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is already installed."
    PYTHON_INSTALLED=true
else
    echo "Python 3.10 is not installed."
    PYTHON_INSTALLED=false
fi

# If conda is not installed, install Miniconda
if [ "$CONDA_INSTALLED" = false ]; then
    echo "Installing Miniconda..."
    
    # Install dependencies
    sudo apt-get update
    sudo apt-get install -y wget

    # Download Miniconda installer
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    MINICONDA_INSTALLER="miniconda.sh"
    
    wget $MINICONDA_URL -O $MINICONDA_INSTALLER
    
    # Install Miniconda
    bash $MINICONDA_INSTALLER -b -p $HOME/miniconda
    
    # Clean up installer
    rm $MINICONDA_INSTALLER
    
    # Add conda to path for current session
    export PATH="$HOME/miniconda/bin:$PATH"
    
    # Add conda to path permanently
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
    
    # Initialize conda for bash
    $HOME/miniconda/bin/conda init bash
    
    echo "Miniconda has been installed. Please restart your terminal or run 'source ~/.bashrc' to use conda."
    CONDA_INSTALLED=true
fi

# If Python 3.10 is not installed, install it
if [ "$PYTHON_INSTALLED" = false ]; then
    echo "Installing Python 3.10..."
    
    if [ "$CONDA_INSTALLED" = true ]; then
        # If conda is installed, use it to install Python 3.10
        conda install -y python=3.10
    else
        # If conda is not installed (which shouldn't happen at this point), use apt
        sudo apt-get update
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
    fi
    
    echo "Python 3.10 has been installed."
fi

echo "Verification:"
echo "-------------"
# Verify conda installation
if command -v conda &> /dev/null; then
    echo "conda is installed:"
    conda --version
else
    echo "conda installation failed."
fi

# Verify Python installation
if command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is installed."
    python3.10 --version
elif command -v conda &> /dev/null; then
    echo "Checking conda Python version:"
    conda activate base
    python --version
else
    echo "Python 3.10 installation failed."
fi

echo "Script completed."
