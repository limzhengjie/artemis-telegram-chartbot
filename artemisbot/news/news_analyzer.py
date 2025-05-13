import os
import logging
from openai import AsyncOpenAI
from typing import Optional, List
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY')
CRYPTOPANIC_API_URL = 'https://cryptopanic.com/api/v1/posts/?public=true'

class NewsAnalyzer:
    def __init__(self):
        """Initialize the NewsAnalyzer with OpenAI client and CryptoPanic API key."""
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cryptopanic_api_key = os.getenv('CRYPTOPANIC_API_KEY')
        if not self.cryptopanic_api_key:
            logger.error("CRYPTOPANIC_API_KEY not set in environment.")
    
    async def fetch_today_news(self, asset: Optional[str] = None) -> List[str]:
        """
        Fetch today's crypto news headlines from CryptoPanic.
        Optionally filter by asset (symbol).
        Returns a list of headlines.
        """
        if not self.cryptopanic_api_key:
            logger.error("CRYPTOPANIC_API_KEY not set in environment.")
            return []
        params = {
            'auth_token': self.cryptopanic_api_key,
            'filter': 'hot',
            'public': 'true',
        }
        if asset:
            params['currencies'] = asset.lower()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(CRYPTOPANIC_API_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                today = datetime.utcnow().date()
                headlines = []
                for post in data.get('results', []):
                    published = post.get('published_at', '')
                    if published:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00')).date()
                        if pub_date == today:
                            headlines.append(post.get('title', ''))
                logger.info(f"API Key: {self.cryptopanic_api_key}")
                logger.info(f"CryptoPanic API response: {data}")
                return headlines[:10]  # Limit to 10 headlines
            except Exception as e:
                logger.error(f"Error fetching news from CryptoPanic: {e}")
                return []

    async def get_market_news(self, asset: Optional[str] = None) -> str:
        """
        Get a summary of today's market news, optionally filtered by asset.
        """
        headlines = await self.fetch_today_news(asset)
        if not headlines:
            return "No fresh news found for today."
        prompt = (
            f"Summarize the following crypto news headlines from today ({datetime.utcnow().date()}):\n"
            + '\n'.join(f"- {h}" for h in headlines)
            + "\nFocus on price movements, significant events, and market sentiment. Keep it under 850 characters."
        )
        try:
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