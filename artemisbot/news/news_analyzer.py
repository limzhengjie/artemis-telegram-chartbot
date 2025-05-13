import os
import openai
import logging
from datetime import datetime, timedelta

class NewsAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def get_market_news(self, asset_id: str = None) -> str:
        """
        Get a summary of today's market news, optionally filtered by asset.
        
        Args:
            asset_id: Optional asset identifier (symbol or artemis_id)
            
        Returns:
            str: A concise summary of market news
        """
        try:
            # Construct the prompt based on whether an asset was specified
            if asset_id:
                prompt = f"""Analyze today's market news and provide a concise summary focusing on {asset_id.upper()}. 
                Include key price movements, significant events, and market sentiment. 
                Keep the response under 500 characters and focus on the most impactful news."""
            else:
                prompt = """Analyze today's crypto market news and provide a concise summary of the overall market conditions.
                Include key price movements, significant events, and market sentiment.
                Keep the response under 500 characters and focus on the most impactful news."""
            
            # Get response from ChatGPT
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst providing concise, factual summaries of market news."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Extract and return the summary
            summary = response.choices[0].message.content.strip()
            logging.info("Successfully generated market news summary")
            return summary
            
        except Exception as e:
            logging.error(f"Error generating market news summary: {str(e)}")
            raise Exception("Failed to generate market news summary. Please try again later.") 