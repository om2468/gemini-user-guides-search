"""
GSPP User Guides - Initial Setup Script

Run this ONCE to:
1. Create a File Search store in Gemini
2. Upload and index both PDF user guides

Requirements:
    pip install google-genai python-dotenv

Usage:
    python setup.py
"""

import os
import time
import json
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configuration
PDF_FILES = [
    ("user guides/GSPP Job Planning Application User Guide.pdf", "GSPP Job Planning User Guide"),
    ("user guides/GSPP Sweet Editor User Guide.pdf", "GSPP Sweet Editor User Guide"),
]
STORE_NAME = "GSPP-User-Guides"
CONFIG_FILE = "file_search_config.json"


def get_client():
    """Initialize the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GEMINI_API_KEY in your .env file")
    return genai.Client(api_key=api_key)


def find_existing_store(client, display_name):
    """Check if a store with the given display name already exists."""
    try:
        for store in client.file_search_stores.list():
            if store.display_name == display_name:
                return store
    except Exception as e:
        print(f"Error listing stores: {e}")
    return None


def create_store_and_upload_files(client):
    """Create a File Search store and upload all PDF files."""
    
    # Check for existing store
    print(f"\nChecking for existing store: {STORE_NAME}")
    existing_store = find_existing_store(client, STORE_NAME)
    
    if existing_store:
        print(f"✅ Found existing store: {existing_store.name}")
        response = input("\nDo you want to use the existing store? (y/n): ").strip().lower()
        if response == 'y':
            return existing_store.name
        else:
            print("Deleting existing store...")
            client.file_search_stores.delete(name=existing_store.name, config={'force': True})
            print("Deleted.")
    
    # Create new store
    print(f"\n📦 Creating new File Search store: {STORE_NAME}")
    file_search_store = client.file_search_stores.create(
        config={"display_name": STORE_NAME}
    )
    print(f"✅ Created store: {file_search_store.name}")
    
    # Upload each PDF file
    for file_path, display_name in PDF_FILES:
        print(f"\n📄 Uploading: {display_name}")
        print(f"   File: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ ERROR: File not found!")
            continue
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   Size: {file_size:.1f} MB")
        
        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=file_search_store.name,
            config={"display_name": display_name}
        )
        
        # Wait for the upload and indexing to complete
        print("   Indexing", end="", flush=True)
        while not operation.done:
            time.sleep(3)
            print(".", end="", flush=True)
            operation = client.operations.get(operation)
        print(" ✅ Done!")
    
    return file_search_store.name


def save_config(store_name):
    """Save configuration to file for use by the app."""
    config = {
        "store_name": store_name,
        "store_display_name": STORE_NAME,
        "pdf_files": [
            {"path": path, "display_name": name}
            for path, name in PDF_FILES
        ],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {CONFIG_FILE}")


def main():
    print("=" * 60)
    print("GSPP User Guides - File Search Setup")
    print("=" * 60)
    
    # Check for PDF files
    print("\n📋 Checking PDF files...")
    all_found = True
    for file_path, display_name in PDF_FILES:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   ✅ {display_name} ({size:.1f} MB)")
        else:
            print(f"   ❌ {display_name} - NOT FOUND at {file_path}")
            all_found = False
    
    if not all_found:
        print("\n❌ Some PDF files are missing. Please check the paths.")
        return
    
    # Initialize client
    print("\n🔑 Initializing Gemini client...")
    try:
        client = get_client()
        print("   ✅ Client initialized")
    except ValueError as e:
        print(f"   ❌ {e}")
        return
    
    # Create store and upload files
    store_name = create_store_and_upload_files(client)
    
    # Save configuration
    save_config(store_name)
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print(f"\nStore Name: {store_name}")
    print(f"\nYou can now run the app with:")
    print("   python -m streamlit run app.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
