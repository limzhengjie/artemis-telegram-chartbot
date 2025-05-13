import os
import logging
from openai import AsyncOpenAI
from typing import Optional, List
import httpx
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY')
CRYPTOPANIC_API_URL = 'https://cryptopanic.com/api/v1/posts/?public=true'

# Load artemis_mappings.json
mappings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'artemis_mappings.json')
with open(mappings_path, 'r') as f:
    artemis_mappings = json.load(f)

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
        Returns a list of headlines. If no news for today, returns the most recent news.
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
                headlines_today = []
                headlines_recent = []
                for post in data.get('results', []):
                    published = post.get('published_at', '')
                    if published:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00')).date()
                        if pub_date == today:
                            headlines_today.append(post.get('title', ''))
                        if len(headlines_recent) < 5:
                            headlines_recent.append(post.get('title', ''))
                if headlines_today:
                    return headlines_today[:10]
                else:
                    return headlines_recent[:5]
            except Exception as e:
                logger.error(f"Error fetching news from CryptoPanic: {e}")
                return []

    async def get_market_news(self, asset: Optional[str] = None) -> str:
        """
        Get a summary of today's market news, optionally filtered by asset.
        If asset is provided, check artemis_mappings.json for the asset symbol or artemis_id.
        """
        if asset:
            # Check artemis_mappings.json for the asset symbol or artemis_id
            asset_symbol = artemis_mappings.get(asset.lower(), asset.lower())
            headlines = await self.fetch_today_news(asset_symbol)
        else:
            headlines = await self.fetch_today_news()
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
                max_tokens=850,
                temperature=0.7
            )
            if len(headlines) < 5:
                return "No fresh news found for today. Here is the most recent news:\n" + response.choices[0].message.content.strip()
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating market news summary: {e}")
            return "Failed to generate market news summary. Please try again later." 