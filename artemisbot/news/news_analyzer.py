import os
import logging
from openai import AsyncOpenAI
from typing import Optional

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        """Initialize the NewsAnalyzer with OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def get_market_news(self, asset: Optional[str] = None) -> str:
        """
        Get a summary of market news, optionally filtered by asset.
        
        Args:
            asset (str, optional): Asset to filter news for (e.g., 'eth', 'btc', 'solana')
            
        Returns:
            str: Summary of market news
        """
        try:
            # Construct the prompt based on whether an asset is specified
            if asset:
                prompt = f"Provide a concise summary of the latest market news specifically about {asset.upper()}. Focus on price movements, significant events, and market sentiment. Keep it under 500 characters."
            else:
                prompt = "Provide a concise summary of the latest market news. Focus on major price movements, significant events, and overall market sentiment. Keep it under 500 characters."
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst providing concise news summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating market news summary: {e}")
            return "Failed to generate market news summary. Please try again later." 