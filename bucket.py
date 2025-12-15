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
        print("\n=== Write Entry ===")
        print("1. Task")
        print("2. Note")
        print("3. Bookmark") 
        print("4. Back to Main Menu")
        
        choice = input("Choose (1-4): ").strip()
        
        if choice in '123':
            entry_type = get_type_by_choice(choice)
            if entry_type:
                write_entry(base_url, headers, entry_type)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Press 1-4")

def read_entry(base_url, headers, entry_type):
    """Read entries of a specific type"""
    editor = os.getenv('EDITOR', 'nvim')
    
    try:
        # Get from API
        response = requests.get(f"{base_url}?type={entry_type}", headers=headers)
        
        if response.status_code != 200:
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        content = response.text
        
        # Create temp file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Open editor
            subprocess.run([editor, temp_path])
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"Error: {e}")

def read_submenu(base_url, headers):
    """Stay in read submenu loop"""
    while True:
        print("\n=== Read Entry ===")
        print("1. Task")
        print("2. Note")
        print("3. Bookmark")
        print("4. Back to Main Menu")
        
        choice = input("Choose (1-4): ").strip()
        
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
    base_url = "https://vulkan.sumeetsaini.com/well"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    while True:
        print("\n=== Well API ===")
        print("1. Write Entry")
        print("2. Read Entry")
        print("3. Exit")
        
        choice = input("Choose (1-3): ").strip()
        
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
