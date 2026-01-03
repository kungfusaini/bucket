#!/usr/bin/env python3

import os
import sys
import tempfile
import subprocess
import requests
import json
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

def get_categories(base_url, headers):
    """Get categories and subcategories from API"""
    try:
        response = requests.get(f"{base_url}/categories", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('categories', {})
        else:
            print(f"Error getting categories: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        print(f"Error getting categories: {e}")
        return {}

def add_category(base_url, headers, category):
    """Add new category"""
    try:
        response = requests.post(
            f"{base_url}/categories",
            json={'category': category},
            headers=headers
        )
        if response.status_code != 201:
            print(f"Server response: {response.status_code} - {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error adding category: {e}")
        return False

def add_subcategory(base_url, headers, category, subcategory):
    """Add new subcategory"""
    try:
        response = requests.post(
            f"{base_url}/categories",
            json={'category': category, 'subcategory': subcategory},
            headers=headers
        )
        if response.status_code != 201:
            print(f"Server response: {response.status_code} - {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error adding subcategory: {e}")
        return False

def get_date_input():
    """Get date input from user"""
    while True:
        choice = input("Date: (1) Today, (2) Custom date [1]: ").strip() or '1'
        
        if choice == '1':
            from datetime import date
            return date.today().isoformat()
        elif choice == '2':
            while True:
                date_input = input("Enter date (YYYY-MM-DD): ").strip()
                if len(date_input) == 10 and date_input[4] == '-' and date_input[7] == '-':
                    try:
                        year, month, day = map(int, date_input.split('-'))
                        from datetime import date
                        date(year, month, day)  # Validate date
                        return date_input
                    except ValueError:
                        print("Invalid date. Please use YYYY-MM-DD format.")
                else:
                    print("Invalid format. Please use YYYY-MM-DD.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_name_input():
    """Get name input from user"""
    while True:
        name = input("Name: ").strip()
        if name:
            return name
        else:
            print("Name is required.")

def get_amount_input():
    """Get amount input from user"""
    while True:
        amount_input = input("Amount: ").strip()
        try:
            amount = float(amount_input)
            if amount > 0:
                return round(amount, 2)
            else:
                print("Amount must be positive.")
        except ValueError:
            print("Invalid amount. Please enter a number.")

def select_category(categories, base_url, headers):
    """Select category from list or add new"""
    if not categories:
        # No categories exist, must create one
        print("No categories exist yet.")
        while True:
            category = input("Enter new category name: ").strip()
            if category:
                if add_category(base_url, headers, category):
                    print(f"Category '{category}' added successfully.")
                    return category, select_subcategory(category, [], base_url, headers)
                else:
                    print("Failed to add category. Please try again.")
            else:
                print("Category name is required.")
    
    while True:
        print("\nCategories:")
        category_list = list(categories.keys())
        for i, cat in enumerate(category_list, 1):
            print(f"  ({i}) {cat}")
        print(f"  ({len(category_list) + 1}) Add New Category")
        
        choice = input(f"Select category [1-{len(category_list) + 1}]: ").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(category_list):
                selected_category = category_list[choice_num - 1]
                subcategory = select_subcategory(selected_category, categories[selected_category], base_url, headers)
                return selected_category, subcategory
            elif choice_num == len(category_list) + 1:
                # Add new category
                while True:
                    new_category = input("Enter new category name: ").strip()
                    if new_category:
                        if add_category(base_url, headers, new_category):
                            print(f"Category '{new_category}' added successfully.")
                            categories[new_category] = []  # Update local cache
                            subcategory = select_subcategory(new_category, [], base_url, headers)
                            return new_category, subcategory
                        else:
                            print("Failed to add category. Please try again.")
                    else:
                        print("Category name is required.")
            else:
                print(f"Invalid choice. Please enter 1-{len(category_list) + 1}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def select_subcategory(category, subcategories, base_url, headers):
    """Select subcategory from list or add new"""
    if not subcategories:
        # No subcategories exist, must create one
        print(f"No subcategories exist for '{category}'. Let's create one.")
        while True:
            subcategory = input("Enter new subcategory name: ").strip()
            if subcategory:
                if add_subcategory(base_url, headers, category, subcategory):
                    print(f"Subcategory '{subcategory}' added successfully.")
                    return subcategory
                else:
                    print("Failed to add subcategory. Please try again.")
            else:
                print("Subcategory name is required.")
    
    while True:
        print(f"\nSubcategories for {category}:")
        for i, sub in enumerate(subcategories, 1):
            print(f"  ({i}) {sub}")
        print(f"  ({len(subcategories) + 1}) Add New Subcategory")
        
        choice = input(f"Select subcategory [1-{len(subcategories) + 1}]: ").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(subcategories):
                return subcategories[choice_num - 1]
            elif choice_num == len(subcategories) + 1:
                # Add new subcategory
                while True:
                    new_subcategory = input("Enter new subcategory name: ").strip()
                    if new_subcategory:
                        if add_subcategory(base_url, headers, category, new_subcategory):
                            print(f"Subcategory '{new_subcategory}' added successfully.")
                            return new_subcategory
                        else:
                            print("Failed to add subcategory. Please try again.")
                    else:
                        print("Subcategory name is required.")
            else:
                print(f"Invalid choice. Please enter 1-{len(subcategories) + 1}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_payment_method():
    """Get payment method from user"""
    while True:
        choice = input("Payment Method: (1) Credit, (2) Debit [1]: ").strip() or '1'
        if choice == '1':
            return 'credit'
        elif choice == '2':
            return 'debit'
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_notes():
    """Get optional notes from user"""
    notes = input("Notes [optional]: ").strip()
    return notes

def spend_entry(base_url, headers):
    """Add a new financial entry"""
    try:
        print("\n=== Spend Entry ===")
        
        # Get all inputs
        date = get_date_input()
        name = get_name_input()
        amount = get_amount_input()
        
        # Get categories
        categories = get_categories(base_url, headers)
        category, subcategory = select_category(categories, base_url, headers)
        
        payment_method = get_payment_method()
        notes = get_notes()
        
        # Create entry
        entry_data = {
            'date': date,
            'name': name,
            'amount': amount,
            'category': category,
            'subcategory': subcategory,
            'payment_method': payment_method,
            'notes': notes
        }
        
        # Send to API
        response = requests.post(
            f"{base_url}/spend",
            json=entry_data,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ Entry added successfully!")
            print(f"Preview: {result.get('preview', 'N/A')}")
        else:
            print(f"\nError adding entry: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

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

def write_submenu(well_base_url, vault_base_url, headers):
    """Stay in write submenu loop"""
    while True:
        print("\n=== Put ===")
        choice = input("\n(1) Task, (2) Note, (3) Bookmark, (4) Spend, (5) Back: ").strip()
        
        if choice in '123':
            entry_type = get_type_by_choice(choice)
            if entry_type:
                write_entry(well_base_url, headers, entry_type)
        elif choice == '4':
            spend_entry(vault_base_url, headers)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Press 1-5")

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

def edit_transactions(vault_base_url, headers):
    """Edit all transactions using external editor"""
    editor = os.getenv('EDITOR', 'nvim')
    
    try:
        # Get original content from API
        response = requests.get(f"{vault_base_url}/data", headers=headers)
        
        if response.status_code != 200:
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        original_content = response.text.strip()
        
        # Create temp file with original CSV content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
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
                update_choice = input("Update transaction data on VPS? (y/n): ").strip().lower()
                
                if update_choice == 'y':
                    # Use PUT endpoint to replace entire file
                    put_response = requests.put(
                        f"{vault_base_url}/data",
                        json={'content': new_content},
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
        print(f"Error editing transactions: {e}")

def edit_categories(vault_base_url, headers):
    """Edit all categories using external editor"""
    editor = os.getenv('EDITOR', 'nvim')
    
    try:
        # Get original content from API
        response = requests.get(f"{vault_base_url}/categories", headers=headers)
        
        if response.status_code != 200:
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        original_content = json.dumps(response.json(), indent=2)
        
        # Create temp file with original JSON content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
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
                update_choice = input("Update categories on VPS? (y/n): ").strip().lower()
                
                if update_choice == 'y':
                    # Use PUT endpoint to replace entire file
                    put_response = requests.put(
                        f"{vault_base_url}/categories",
                        json={'content': new_content},
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
        print(f"Error editing categories: {e}")

def financial_data_submenu(vault_base_url, headers):
    """Financial data submenu loop"""
    while True:
        print("\n=== Financial Data ===")
        choice = input("\n(1) Transactions, (2) Categories, (3) Back: ").strip()
        
        if choice == '1':
            edit_transactions(vault_base_url, headers)
        elif choice == '2':
            edit_categories(vault_base_url, headers)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Press 1-3")

def read_submenu(well_base_url, vault_base_url, headers):
    """Stay in read submenu loop"""
    while True:
        print("\n=== Fetch ===")
        choice = input("\n(1) Task, (2) Note, (3) Bookmark, (4) Finances, (5) Back: ").strip()
        
        if choice in '123':
            entry_type = get_type_by_choice(choice)
            if entry_type:
                read_entry(well_base_url, headers, entry_type)
        elif choice == '4':
            financial_data_submenu(vault_base_url, headers)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Press 1-5")

def main():
    """Main program loop"""
    # Load configuration
    api_key = load_config()
    ascii_art = load_art()
    vault_base_url = "https://vulkan.sumeetsaini.com/vault"
    well_base_url = "https://vulkan.sumeetsaini.com/well"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    while True:
        print("\n=== BUCKET ===\n")
        print(ascii_art)
        choice = input("\n(1) Put Entry, (2) Fetch, (3) Exit: ").strip()
        
        if choice == '1':
            write_submenu(well_base_url, vault_base_url, headers)
        elif choice == '2':
            read_submenu(well_base_url, vault_base_url, headers)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Press 1-3")

if __name__ == "__main__":
    main()
