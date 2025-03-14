#!/usr/bin/env python3
"""
genRemoteSSHKey.py - Generate SSH keys for remote systems and update local SSH config

This script connects to a remote Linux system, generates SSH keys, and updates
the local SSH config file to enable passwordless authentication.
Works from both Windows and Linux host systems.
"""

import os
import sys
import subprocess
import getpass
import paramiko
import re
import platform
from pathlib import Path

def get_home_directory():
    """Get the user's home directory."""
    # You can customize this for your specific environment
    return str(Path.home())

def ensure_ssh_directory(home_dir):
    """Ensure .ssh directory exists in home directory."""
    ssh_dir = os.path.join(home_dir, ".ssh")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)
    return ssh_dir

def is_windows():
    """Check if the system is Windows."""
    return platform.system().lower() == 'windows'

def normalize_path_for_platform(path):
    """Normalize path based on the platform."""
    if is_windows():
        # Windows might need backslashes in some contexts
        return path.replace('/', '\\')
    return path

def update_ssh_config(ssh_dir, connection_name, hostname, username, identity_file):
    """Update SSH config file with new connection details."""
    config_file = os.path.join(ssh_dir, "config")
    
    # Normalize identity file path for platform
    platform_identity_file = normalize_path_for_platform(identity_file)
    
    # Create config entry
    config_entry = f"""
Host {connection_name}
    HostName {hostname}
    User {username}
    IdentityFile {platform_identity_file}
"""
    
    # Check if config file exists and if the host is already defined
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            
        # Check if host already exists
        pattern = re.compile(rf"Host\s+{re.escape(connection_name)}\s*\n")
        if pattern.search(content):
            print(f"Host {connection_name} already exists in SSH config. Updating...")
            # Remove existing entry
            pattern = re.compile(rf"Host\s+{re.escape(connection_name)}.*?(?=Host|\Z)", re.DOTALL)
            content = pattern.sub("", content)
        
        # Append new entry
        with open(config_file, 'w') as f:
            f.write(content.rstrip() + config_entry)
    else:
        # Create new config file
        with open(config_file, 'w') as f:
            f.write(config_entry.lstrip())
        
        # Set proper permissions
        try:
            # This might fail on Windows
            os.chmod(config_file, 0o600)
        except:
            print("Note: Could not set file permissions on Windows. Ensure your SSH config file is secured.")
    
    print(f"SSH config updated for {connection_name}")

def generate_remote_key(hostname, username, password, connection_name):
    """Generate SSH key on remote system and retrieve it."""
    try:
        # Connect to remote host
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {hostname} as {username}...")
        client.connect(hostname, username=username, password=password)
        
        # Generate key on remote system
        print("Checking SSH directory on remote system...")
        stdin, stdout, stderr = client.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
        stdout.channel.recv_exit_status()
        
        # Check if key already exists
        stdin, stdout, stderr = client.exec_command("ls ~/.ssh/id_rsa")
        if stdout.channel.recv_exit_status() == 0:
            print("SSH key already exists on remote system.")
            choice = input("Options:\n1. Use existing SSH key\n2. Generate a new key named after connection\n3. Abort operation\nEnter choice (1-3): ")
            
            if choice == '1':
                print("Using existing SSH key...")
                # Get public key
                stdin, stdout, stderr = client.exec_command("cat ~/.ssh/id_rsa.pub")
                remote_public_key = stdout.read().decode().strip()
                
                # Get private key
                stdin, stdout, stderr = client.exec_command("cat ~/.ssh/id_rsa")
                remote_private_key = stdout.read().decode()
                
                client.close()
                return remote_public_key, remote_private_key
            elif choice == '2':
                print(f"Generating new key named after connection: {connection_name}...")
                # Generate new key with connection name
                key_filename = f"id_{connection_name}"
                stdin, stdout, stderr = client.exec_command(f"ssh-keygen -t rsa -N '' -f ~/.ssh/{key_filename}")
                stdout.channel.recv_exit_status()
                
                # Get public key
                stdin, stdout, stderr = client.exec_command(f"cat ~/.ssh/{key_filename}.pub")
                remote_public_key = stdout.read().decode().strip()
                
                # Get private key
                stdin, stdout, stderr = client.exec_command(f"cat ~/.ssh/{key_filename}")
                remote_private_key = stdout.read().decode()
                
                client.close()
                return remote_public_key, remote_private_key, key_filename
            else:
                print("Aborting operation.")
                client.close()
                return None
        else:
            # No existing key found, generate a new one with the connection name
            print(f"Generating new SSH key with name: id_{connection_name}...")
            key_filename = f"id_{connection_name}"
            stdin, stdout, stderr = client.exec_command(f"ssh-keygen -t rsa -N '' -f ~/.ssh/{key_filename}")
            stdout.channel.recv_exit_status()
            
            # Get public key
            stdin, stdout, stderr = client.exec_command(f"cat ~/.ssh/{key_filename}.pub")
            remote_public_key = stdout.read().decode().strip()
            
            # Get private key
            stdin, stdout, stderr = client.exec_command(f"cat ~/.ssh/{key_filename}")
            remote_private_key = stdout.read().decode()
            
            client.close()
            return remote_public_key, remote_private_key, key_filename
    
    except Exception as e:
        print(f"Error connecting to remote system: {e}")
        return None

def save_keys_locally(ssh_dir, connection_name, public_key, private_key, key_filename=None):
    """Save the retrieved keys to local system."""
    # Create identity file path
    if key_filename:
        identity_file = os.path.join(ssh_dir, key_filename)
    else:
        identity_file = os.path.join(ssh_dir, f"id_{connection_name}")
    
    # Save private key
    with open(identity_file, 'w') as f:
        f.write(private_key)
    
    # Set permissions (might fail on Windows)
    try:
        os.chmod(identity_file, 0o600)
    except:
        print("Note: Could not set file permissions on Windows. Ensure your private key file is secured.")
    
    # Save public key
    with open(f"{identity_file}.pub", 'w') as f:
        f.write(public_key)
    
    print(f"Keys saved locally as {identity_file}")
    return identity_file

def main():
    """Main function to run the script."""
    print("=== Remote SSH Key Generator ===")
    print(f"Running on: {platform.system()}")
    
    # Get connection details
    hostname = input("Enter remote IP address: ")
    username = input("Enter remote username: ")
    password = getpass.getpass("Enter remote password: ")
    connection_name = input("Enter connection name (e.g., homeAssistant_Jetson): ")
    
    # Get home directory and ensure .ssh directory exists
    home_dir = get_home_directory()
    ssh_dir = ensure_ssh_directory(home_dir)
    
    # Generate key on remote system
    key_data = generate_remote_key(hostname, username, password, connection_name)
    if not key_data:
        sys.exit(1)
    
    # Check if we have a key filename returned (for new keys)
    if len(key_data) == 3:
        public_key, private_key, key_filename = key_data
        # Save keys locally
        identity_file = save_keys_locally(ssh_dir, connection_name, public_key, private_key, key_filename)
    else:
        public_key, private_key = key_data
        # Save keys locally
        identity_file = save_keys_locally(ssh_dir, connection_name, public_key, private_key)
    
    # Update SSH config
    update_ssh_config(ssh_dir, connection_name, hostname, username, identity_file)
    
    print(f"\nSetup complete! You can now connect using: ssh {connection_name}")

if __name__ == "__main__":
    main()
