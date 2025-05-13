import os
import sys
import logging
from typing import List, Optional, Tuple
from datetime import datetime

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from artemisbot.chart.url_builder import build_chart_url
from artemisbot.chart.screenshot import take_screenshot
from artemisbot.chart.chart_analyzer import generate_chart_summary_from_bytes
from artemisbot.utils.asset_mappings import get_asset_by_id, get_asset_by_symbol

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartGenerator:
    """A class to handle chart generation and analysis."""
    
    def __init__(self):
        """Initialize the ChartGenerator."""
        self.metric_display = {
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
        }
        
        self.time_period_display = {
            "1w": "1 Week",
            "mtd": "Month to Date",
            "1m": "1 Month",
            "3m": "3 Months",
            "6m": "6 Months",
            "ytd": "Year to Date",
            "1y": "1 Year",
            "all": "All Time"
        }
        
        self.granularity_display = {
            "1d": "Daily",
            "1w": "Weekly",
            "1m": "Monthly"
        }
    
    def _get_asset_names(self, tickers: List[str]) -> List[str]:
        """Get display names for assets."""
        asset_names = []
        for ticker in tickers:
            asset_info = get_asset_by_id(ticker) or get_asset_by_symbol(ticker)
            if not asset_info:
                raise ValueError(f"Unknown asset: {ticker}")
            asset_names.append(asset_info.get("name", ticker.capitalize()))
        return asset_names
    
    def _create_title(self, metrics: List[str], asset_names: List[str], 
                     time_period: str, granularity: str, is_percentage: bool) -> str:
        """Create a readable title for the chart."""
        metric_displays = [self.metric_display.get(metric, metric.capitalize()) for metric in metrics]
        title = f"{' vs '.join(metric_displays)} - {'/'.join(asset_names)} "
        title += f"({self.time_period_display.get(time_period, time_period)}, "
        title += f"{self.granularity_display.get(granularity, granularity)})"
        if is_percentage:
            title += " (%)"
        return title
    
    def generate_chart(self, metrics: List[str], tickers: List[str], 
                      asset_type: str, time_period: str, granularity: str, 
                      is_percentage: bool = False) -> Tuple[bytes, str, str]:
        """
        Generate a chart with the given parameters.
        
        Args:
            metrics: List of metrics to chart
            tickers: List of asset tickers
            asset_type: Type of asset (e.g., 'chain', 'application')
            time_period: Time period for the chart
            granularity: Data granularity
            is_percentage: Whether to display as percentages
            
        Returns:
            Tuple containing:
            - chart_image: The chart image as bytes
            - chart_url: The URL to the interactive chart
            - title: The chart title
            
        Raises:
            ValueError: If any parameters are invalid
        """
        try:
            # Get asset names and create title
            asset_names = self._get_asset_names(tickers)
            title = self._create_title(metrics, asset_names, time_period, granularity, is_percentage)
            
            # Build chart URL
            chart_url = build_chart_url(metrics, tickers, asset_type, time_period, granularity, is_percentage)
            
            # Take screenshot
            screenshot_result = take_screenshot(chart_url)
            
            # Handle error responses
            if isinstance(screenshot_result, str) and screenshot_result.startswith("ERROR:"):
                error_code = screenshot_result.split(":")[1]
                if error_code == "AUTH_REQUIRED":
                    raise ValueError("Authentication required. Please contact your administrator for access.")
                elif error_code == "NO_DATA":
                    raise ValueError(f"No data available for {', '.join(asset_names)}. Try different time periods or metrics.")
                elif error_code == "INVALID_PARAMETERS":
                    raise ValueError("Invalid chart parameters. Please check your input.")
                else:
                    raise ValueError(f"Chart generation failed: {error_code}")
            
            # Generate analysis if screenshot is successful
            analysis = None
            if isinstance(screenshot_result, bytes):
                analysis = generate_chart_summary_from_bytes(screenshot_result)
            
            return screenshot_result, chart_url, title, analysis
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            raise 