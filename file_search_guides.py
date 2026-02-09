"""
Gemini API File Search - GSPP User Guides Query Tool

This script creates a File Search store, uploads the two GSPP user guides,
and provides an interactive query interface to ask questions about the guides.

Requirements:
    pip install google-genai python-dotenv

Usage:
    1. Create a .env file with: GEMINI_API_KEY=your-api-key-here
    2. Run: python file_search_guides.py
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Configuration
PDF_FILES = [
    ("user guides/GSPP Job Planning Application User Guide.pdf", "GSPP Job Planning User Guide"),
    ("user guides/GSPP Sweet Editor User Guide.pdf", "GSPP Sweet Editor User Guide"),
]
STORE_NAME = "GSPP-User-Guides"
MODEL = "gemini-3-flash-preview"


def get_client():
    """Initialize the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable")
    return genai.Client(api_key=api_key)


def find_existing_store(client, display_name):
    """Check if a store with the given display name already exists."""
    try:
        for store in client.file_search_stores.list():
            if store.display_name == display_name:
                print(f"Found existing store: {store.name}")
                return store
    except Exception as e:
        print(f"Error listing stores: {e}")
    return None


def create_store_and_upload_files(client):
    """Create a File Search store and upload all PDF files."""
    # Check for existing store
    existing_store = find_existing_store(client, STORE_NAME)
    if existing_store:
        print(f"\nUsing existing store: {existing_store.name}")
        return existing_store.name
    
    # Create new store
    print(f"\nCreating new File Search store: {STORE_NAME}")
    file_search_store = client.file_search_stores.create(
        config={"display_name": STORE_NAME}
    )
    print(f"Created store: {file_search_store.name}")
    
    # Upload each PDF file
    for file_path, display_name in PDF_FILES:
        print(f"\nUploading: {display_name}")
        print(f"  File: {file_path}")
        
        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=file_search_store.name,
            config={"display_name": display_name}
        )
        
        # Wait for the upload and indexing to complete
        print("  Indexing...", end="", flush=True)
        while not operation.done:
            time.sleep(5)
            print(".", end="", flush=True)
            operation = client.operations.get(operation)
        print(" Done!")
    
    print(f"\nAll files uploaded and indexed successfully!")
    return file_search_store.name


def query_guides(client, store_name, question):
    """Query the user guides with a question."""
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            ]
        )
    )
    return response


def print_response_with_citations(response):
    """Print the response text and any citations."""
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(response.text)
    
    # Print citations if available
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata
        if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
            print("\n" + "-" * 80)
            print("CITATIONS:")
            print("-" * 80)
            for i, chunk in enumerate(metadata.grounding_chunks, 1):
                if hasattr(chunk, 'retrieved_context'):
                    ctx = chunk.retrieved_context
                    title = getattr(ctx, 'title', 'Unknown')
                    print(f"\n[{i}] Source: {title}")
                    if hasattr(chunk, 'text') and chunk.text:
                        # Show a snippet of the cited text
                        snippet = chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                        print(f"    Text: {snippet}")


def interactive_mode(client, store_name):
    """Run an interactive query session."""
    print("\n" + "=" * 80)
    print("GSPP User Guides - Interactive Query Mode")
    print("=" * 80)
    print("Ask questions about the GSPP Job Planning Application or Sweet Editor.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'clear' to clear the screen.")
    print("=" * 80)
    
    while True:
        print()
        question = input("Your question: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break
        
        if question.lower() == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            continue
        
        print("\nSearching guides...")
        try:
            response = query_guides(client, store_name, question)
            print_response_with_citations(response)
        except Exception as e:
            print(f"\nError: {e}")


def main():
    print("=" * 80)
    print("Gemini File Search - GSPP User Guides")
    print("=" * 80)
    
    # Initialize client
    print("\nInitializing Gemini client...")
    client = get_client()
    
    # Create store and upload files (or use existing)
    store_name = create_store_and_upload_files(client)
    
    # Start interactive mode
    interactive_mode(client, store_name)


if __name__ == "__main__":
    main()
