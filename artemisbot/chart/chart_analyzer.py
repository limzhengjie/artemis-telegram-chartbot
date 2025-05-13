import os
import sys
import openai
from typing import Optional
import logging
from datetime import datetime
import base64

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from artemisbot.chart.url_builder import build_chart_url
from artemisbot.chart.screenshot import take_screenshot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_chart_summary(image_path: str) -> Optional[str]:
    """
    Generate a summary of the chart using OpenAI's API.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        A summary of the chart or None if generation fails
    """
    try:
        # Get current date for context
        today = datetime.now().strftime("%B %d, %Y")
        
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create a prompt for the chart analysis
        prompt = "Analyze this chart and provide a concise summary and macro impact analysis. Keep the response under 800 characters."
        
        # Call OpenAI API with the image
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        
        # Extract and return the summary
        summary = response.choices[0].message.content
        logger.info("Successfully generated chart summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating chart summary: {str(e)}")
        return None

def generate_chart_summary_from_bytes(image_bytes: bytes) -> Optional[str]:
    """
    Generate a summary of the chart using OpenAI's API, from in-memory image bytes.
    Args:
        image_bytes: PNG image bytes
    Returns:
        A summary of the chart or None if generation fails
    """
    try:
        today = datetime.now().strftime("%B %d, %Y")
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        prompt = "Analyze this chart and provide a concise summary and macro impact analysis. Keep the response under 800 characters."
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        
        summary = response.choices[0].message.content
        logger.info("Successfully generated chart summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating chart summary from bytes: {str(e)}")
        return None 