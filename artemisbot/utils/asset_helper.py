from typing import Dict, Optional
from artemisbot.utils.asset_mappings import get_asset_by_symbol, get_asset_by_id

def clean_asset_params(asset: str, asset_type: str) -> Dict:
    """
    Clean and validate asset parameters.
    
    Args:
        asset: The asset symbol or ID
        asset_type: The type of asset
        
    Returns:
        Dictionary with cleaned asset parameters
        
    Raises:
        ValueError: If the asset is not found
    """
    # Try to get asset info
    asset_info = get_asset_by_symbol(asset) or get_asset_by_id(asset)
    if not asset_info:
        raise ValueError(f"Unknown asset: {asset}")
        
    return {
        "id": asset_info["id"],
        "type": asset_type.lower()
    }
