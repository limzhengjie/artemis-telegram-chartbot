from typing import List, Tuple
from artemisbot.utils.asset_mappings import get_asset_by_symbol, get_asset_by_id

def parse_command(command_text: str, is_group: bool = False) -> Tuple[List[str], List[str], str, str, str, bool]:
    """
    Parse command text into its components.
    
    Args:
        command_text: The command text to parse
        is_group: Whether this is a group chat command
        
    Returns:
        Tuple containing:
        - metrics: List of metrics to chart
        - tickers: List of asset tickers
        - asset_type: The type of asset
        - time_period: The time period for the chart
        - granularity: The granularity of the data
        - is_percentage: Whether to display as percentages
        
    Raises:
        ValueError: If the command format is invalid
    """
    # Remove any leading =art if present
    if command_text.startswith('=art'):
        command_text = command_text[4:].strip()
    
    # Split on commas first, then on spaces
    parts = []
    for part in command_text.split(','):
        parts.extend(part.strip().split())
    
    # Helper function to format error messages consistently
    def format_error(message: str) -> str:
        prefix = "=art " if is_group else ""
        return f"{message}\n\nFormat: {prefix}<metric> [vs <metric>] <asset> <time_period> <granularity> [%]\nExample: {prefix}price vs tvl solana 1w 1d"
    
    if len(parts) < 4:
        raise ValueError(format_error("Command must have at least 4 parts: <metric> <asset> <time_period> <granularity>"))
    
    # Parse metrics (handle "vs" syntax)
    metrics = []
    current_index = 0
    
    while current_index < len(parts):
        if parts[current_index].lower() == "vs":
            current_index += 1
            continue
            
        if current_index + 1 < len(parts) and parts[current_index + 1].lower() == "vs":
            metrics.append(parts[current_index].lower())
            current_index += 2
        else:
            metrics.append(parts[current_index].lower())
            current_index += 1
            break
    
    # Get remaining parts
    remaining_parts = parts[current_index:]
    if len(remaining_parts) < 3:
        raise ValueError(format_error("Command must have at least 4 parts: <metric> <asset> <time_period> <granularity>"))
    
    asset = remaining_parts[0].lower()
    time_period = remaining_parts[1].lower()
    granularity = remaining_parts[2].lower()
    is_percentage = len(remaining_parts) > 3 and remaining_parts[3] == "%"
    
    # Validate metrics
    valid_metrics = ["price", "volume", "tvl", "fees", "revenue", "mc", "txns", "daa", "dau", "fdmc"]
    for metric in metrics:
        if metric not in valid_metrics:
            raise ValueError(format_error(f"Invalid metric '{metric}'. Must be one of: {', '.join(valid_metrics)}"))
    
    # Validate time period
    valid_periods = ["1w", "mtd", "1m", "3m", "6m", "ytd", "1y", "all"]
    if time_period not in valid_periods:
        raise ValueError(format_error(f"Invalid time period '{time_period}'. Must be one of: {', '.join(valid_periods)}"))
    
    # Validate granularity
    valid_granularities = ["1d", "1w", "1m"]
    if granularity not in valid_granularities:
        raise ValueError(format_error(f"Invalid granularity '{granularity}'. Must be one of: {', '.join(valid_granularities)}"))
    
    # Try to resolve asset
    asset_info = get_asset_by_symbol(asset) or get_asset_by_id(asset)
    if not asset_info:
        raise ValueError(format_error(f"Asset '{asset}' not found"))
    
    return metrics, [asset_info["id"]], asset_info["type"], time_period, granularity, is_percentage
