#!/usr/bin/env python3
"""
Script to fetch asset mappings from the Artemis API and update the artemis_mappings.json file.
"""

import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from artemis import Artemis

# Load environment variables
load_dotenv()

# Configuration
ARTEMIS_API_KEY = os.getenv("ARTEMIS_API_KEY")
MAPPINGS_FILE = "config/artemis_mappings.json"

def fetch_assets() -> List[Dict]:
    """Fetch all assets from the Artemis API."""
    client = Artemis(api_key=ARTEMIS_API_KEY)
    response = client.asset.list()
    
    if isinstance(response, dict) and 'assets' in response:
        return response['assets']
    return []

def build_mappings(assets: List[Dict]) -> Dict:
    """Build mappings from the assets data."""
    mappings = {
        "artemis_id_to_symbols": {},
        "symbol_to_artemis_id": {},
        "artemis_id_to_type": {},
        "symbol_to_type": {}
    }
    
    for asset in assets:
        if not isinstance(asset, dict):
            continue
            
        artemis_id = asset.get("artemis_id")
        symbol = asset.get("symbol", "").lower()
        
        # Get asset type from metadata.about.asset, default to "application" if not "chain"
        metadata = asset.get("metadata", {}) or {}
        about = metadata.get("about", {}) or {}
        asset_type = "chain" if about.get("asset") == "chain" else "application"
        
        if not artemis_id or not symbol:
            continue
            
        # Add to artemis_id_to_symbols
        mappings["artemis_id_to_symbols"][artemis_id] = [symbol]
        
        # Add to symbol_to_artemis_id
        mappings["symbol_to_artemis_id"][symbol] = artemis_id
        
        # Add to artemis_id_to_type
        mappings["artemis_id_to_type"][artemis_id] = asset_type
        
        # Add to symbol_to_type
        mappings["symbol_to_type"][symbol] = asset_type
    
    return mappings

def update_mappings_file(mappings: Dict) -> None:
    """Update the mappings file with the new data."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(MAPPINGS_FILE), exist_ok=True)
    
    # Write mappings to file
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=2)

def main():
    """Main function to update mappings."""
    print("Fetching assets from Artemis API...")
    try:
        assets = fetch_assets()
        print(f"Found {len(assets)} assets")
        
        if assets:
            print("\nFirst asset example:")
            print(json.dumps(assets[0], indent=2))
        
        print("\nBuilding mappings...")
        mappings = build_mappings(assets)
        
        print("Updating mappings file...")
        update_mappings_file(mappings)
        
        print("Done! Mappings have been updated.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 