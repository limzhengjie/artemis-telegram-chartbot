import json
import urllib.parse
from typing import List
from artemisbot.utils.asset_mappings import get_asset_by_id, get_asset_by_symbol

def build_chart_url(metric: str, tickers: List[str], asset_type: str, time_period: str, granularity: str, is_percentage: bool = False) -> str:
    """
    Build a chart URL for the Artemis Analytics platform.
    
    Args:
        metric: The metric to chart (e.g., 'price', 'volume', 'tvl')
        tickers: List of asset tickers to include
        asset_type: The type of asset (e.g., 'chain', 'application')
        time_period: The time period for the chart (e.g., '1w', '1m', '1y')
        granularity: The granularity of the data (e.g., '1d', '1w', '1m')
        is_percentage: Whether to display as percentages
        
    Returns:
        The complete chart URL
    """
    # Map time period to Artemis time period ID
    period_map = {
        "1w": "WEEKLY",
        "mtd": "MONTH_TO_DATE",
        "1m": "MONTHLY",
        "3m": "THREE_MONTHS",
        "6m": "SIX_MONTHS",
        "ytd": "YEAR_TO_DATE",
        "1y": "ONE_YEAR",
        "all": "MAX"
    }
    
    # Map granularity to Artemis granularity ID
    granularity_map = {
        "1d": "DAY",
        "1w": "WEEK",
        "1m": "MONTH"
    }
    
    # Map metric to Artemis metric ID
    metric_map = {
        "price": "PRICE",
        "volume": "VOLUME",
        "tvl": "TVL",
        "fees": "FEES",
        "revenue": "REVENUE",
        "mc": "MC",
        "txns": "TXNS",
        "daa": "DAA",
        "dau": "DAU",
        "fdmc": "FDMC",
        "borrows": "BORROWS",
        "deposits": "DEPOSITS"
    }
    
    # Get the Artemis time period ID
    artemis_period = period_map.get(time_period.lower())
    if not artemis_period:
        raise ValueError(f"Invalid time period: {time_period}")
    
    # Get the Artemis granularity ID
    artemis_granularity = granularity_map.get(granularity.lower())
    if not artemis_granularity:
        raise ValueError(f"Invalid granularity: {granularity}")
    
    # Get the Artemis metric ID
    artemis_metric = metric_map.get(metric.lower())
    if not artemis_metric:
        raise ValueError(f"Invalid metric: {metric}")
    
    # Get asset names for display
    asset_names = []
    for ticker in tickers:
        asset_info = get_asset_by_id(ticker) or get_asset_by_symbol(ticker)
        if not asset_info:
            raise ValueError(f"Unknown asset: {ticker}")
        asset_names.append(asset_info.get("name", ticker.capitalize()))
    
    # Create a readable title
    metric_display = {
        "price": "Price",
        "volume": "Volume",
        "tvl": "TVL",
        "fees": "Fees",
        "revenue": "Revenue",
        "mc": "Market Cap",
        "txns": "Transactions",
        "daa": "Daily Active Addresses",
        "dau": "Daily Active Users",
        "fdmc": "Fully Diluted Market Cap"
    }.get(metric, metric.capitalize())
    
    time_period_display = {
        "1w": "1 Week",
        "mtd": "Month to Date",
        "1m": "1 Month",
        "3m": "3 Months",
        "6m": "6 Months",
        "ytd": "Year to Date",
        "1y": "1 Year",
        "all": "All Time"
    }.get(time_period, time_period)
    
    granularity_display = {
        "1d": "Daily",
        "1w": "Weekly",
        "1m": "Monthly"
    }.get(granularity, granularity)
    
    title = f"{metric_display} - {'/'.join(asset_names)} ({time_period_display}, {granularity_display})"
    if is_percentage:
        title += " (%)"
    
    # Build the chart configuration
    chart_config = {
        "title": title,
        "description": "",
        "period": artemis_period,
        "previewUrl": "",
        "granularity": artemis_granularity,
        "smaPeriod": "0",
        "series": []
    }
    
    # Add assets to series
    for ticker in tickers:
        asset_info = get_asset_by_id(ticker) or get_asset_by_symbol(ticker)
        if not asset_info:
            raise ValueError(f"Unknown asset: {ticker}")
            
        # Use the asset type from the asset info if available, otherwise use the provided type
        asset_type_to_use = asset_info.get("type", asset_type).upper()
        
        series_item = {
            "asset": {
                "group": asset_type_to_use,
                "artemisId": asset_info["id"],
                "name": asset_info.get("name", ticker.capitalize()),
                "symbol": asset_info.get("symbol", ticker.lower()),
                "iconUrl": ""
            },
            "metric": {
                "artemisId": artemis_metric
            },
            "setting": {
                "type": "LINE",
                "display": "TIMELINE",
                "scale": "LINEAR",
                "units": "PERCENTAGE" if is_percentage else "RAW",
                "visible": True,
                "showInLegend": True,
                "color": "#8A88FF",
                "yAxis": 0
            }
        }
        chart_config["series"].append(series_item)
    
    # Encode the configuration as a URL-safe JSON string
    encoded_config = urllib.parse.quote(json.dumps(chart_config))
    url = f"https://app.artemisanalytics.com/chart-builder/{encoded_config}"
    
    return url
