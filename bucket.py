#!/usr/bin/env python3

import os
import sys
import tempfile
import subprocess
import requests
from pathlib import Path

def load_config():
    """Load API key from .env file"""
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("Error: .env file not found. Please create it with WELL_API_KEY=your_key")
        sys.exit(1)
    
    with open(env_file) as f:
        for line in f:
            if line.startswith('WELL_API_KEY='):
                return line.split('=', 1)[1].strip()
    
    print("Error: WELL_API_KEY not found in .env file")
    sys.exit(1)

def load_art():
    ascii_file = Path(__file__).parent / 'well.txt'

    if not ascii_file.exists():
        print("Error: well.txt art file not found. Please create it")
        sys.exit(1)

    with open(ascii_file, 'r') as f:
        # Read the entire content of the file
        # and store it in a single string variable
        return f.read()       

def get_type_by_choice(choice):
    """Convert choice number to entry type"""
    type_map = {'1': 'task', '2': 'note', '3': 'bookmark'}
    return type_map.get(choice)

def write_entry(base_url, headers, entry_type):
    """Write a new entry"""
    editor = os.getenv('EDITOR', 'nano')
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Open editor
        subprocess.run([editor, temp_path])
        
        # Read content back
        with open(temp_path, 'r') as f:
            content = f.read().strip()
        
        if not content:
            print("No content entered. Cancelled.")
            return
        
        # Post to API
        response = requests.post(
            base_url,
            json={'type': entry_type, 'body': content},
            headers=headers
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
    finally:
        # Clean up temp file
        os.unlink(temp_path)

def write_submenu(base_url, headers):
    """Stay in write submenu loop"""
    while True:
        print("\n=== Put ===")
        choice = input("\n(1) Task, (2) Note, (3) Bookmark, (4) Back: ").strip()
        
        if choice in '123':
            entry_type = get_type_by_choice(choice)
            if entry_type:
                write_entry(base_url, headers, entry_type)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Press 1-4")

def read_entry(base_url, headers, entry_type):
    """Read and optionally edit entries of a specific type"""
    editor = os.getenv('EDITOR', 'nvim')
    
    try:
        # Get original content from API
        response = requests.get(f"{base_url}?type={entry_type}", headers=headers)
        
        if response.status_code != 200:
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        original_content = response.text.strip()
        
        # Create temp file with original content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(original_content)
            temp_path = temp_file.name
        
        try:
            # Open editor for editing
            subprocess.run([editor, temp_path])
            
            # Read new content after editing
            with open(temp_path, 'r') as f:
                new_content = f.read().strip()
            
            # Check if changes were made
            if original_content != new_content:
                print("Changes detected!")
                update_choice = input("Update file on VPS? (y/n): ").strip().lower()
                
                if update_choice == 'y':
                    # Use PUT endpoint to replace entire file
                    put_response = requests.put(
                        base_url,
                        json={'type': entry_type, 'content': new_content},
                        headers=headers
                    )
                    print(f"\nUpdate Status: {put_response.status_code}")
                    print(f"Update Response: {put_response.text}")
                else:
                    print("Changes discarded.")
            else:
                print("No changes made.")
                
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"Error: {e}")

def read_submenu(base_url, headers):
    """Stay in read submenu loop"""
    while True:
        print("\n=== Fetch ===")
        choice = input("\n(1) Task, (2) Note, (3) Bookmark, (4) Back: ").strip()
        
        if choice in '123':
            entry_type = get_type_by_choice(choice)
            if entry_type:
                read_entry(base_url, headers, entry_type)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Press 1-4")

def main():
    """Main program loop"""
    # Load configuration
    api_key = load_config()
    ascii_art = load_art()
    base_url = "https://vulkan.sumeetsaini.com/well"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    while True:
        print("\n=== BUCKET ===\n")
        print(ascii_art)
        choice = input("\n(1) Put Entry, (2) Fetch, (3) Exit: ").strip()
        
        if choice == '1':
            write_submenu(base_url, headers)
        elif choice == '2':
            read_submenu(base_url, headers)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Press 1-3")

if __name__ == "__main__":
    main()
