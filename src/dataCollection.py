''' doc string 
This is the main module for the election69 application.
first :
download the data from the given url in list_source.txt
second:
save the data in json file in the data folder
'''

import json
import os
import requests
from pathlib import Path
from urllib.parse import urlparse

def download_json_files():
    """
    Download JSON files from URLs listed in list_source.txt
    and save them to the data folder.
    """
    # Get the project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    # Define paths
    source_file = current_dir / "list_source.txt"
    data_folder = project_root / "data"
    
    # Ensure data folder exists
    data_folder.mkdir(exist_ok=True)
    
    # Read URLs from list_source.txt
    if not source_file.exists():
        print(f"Error: {source_file} not found")
        return
    
    with open(source_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("No URLs found in list_source.txt")
        return
    
    # Download each file
    for idx, url in enumerate(urls, 1):
        try:
            print(f"Downloading from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON to validate
            data = response.json()
            
            # Generate filename from URL or use index
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or not filename.endswith('.json'):
                filename = f"data_{idx}.json"
            
            # Save to data folder
            output_path = data_folder / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved to {output_path}")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error downloading {url}: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON from {url}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error processing {url}: {e}")

if __name__ == "__main__":
    download_json_files()
