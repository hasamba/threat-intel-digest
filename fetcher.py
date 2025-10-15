"""Fetch threat intelligence articles from various sources"""
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatIntelFetcher:
    """Fetches threat intelligence articles from RSS feeds and web sources"""

    def __init__(self, sources: List[Dict], max_articles_per_source: int = 5,
                 twitter_accounts: Optional[List[str]] = None,
                 twitter_lists: Optional[List[str]] = None,
                 max_tweets_per_user: int = 3,
                 twitter_enabled: bool = True):
        self.sources = sources
        self.max_articles = max_articles_per_source
        self.twitter_accounts = twitter_accounts or []
        self.twitter_lists = twitter_lists or []
        self.max_tweets = max_tweets_per_user
        self.twitter_enabled = twitter_enabled

    def fetch_rss_feed(self, url: str, source_name: str) -> List[Dict]:
        """Fetch articles from an RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []

            # Get articles from the last 24 hours
            cutoff_date = datetime.now() - timedelta(days=1)

            for entry in feed.entries[:self.max_articles]:
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed'):
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    published = datetime(*entry.updated_parsed[:6])

                # Extract article data
                article = {
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': published.isoformat() if published else None,
                    'source': source_name
                }

                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from {source_name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source_name}: {str(e)}")
            return []

    def fetch_twitter_content(self) -> List[Dict]:
        """Fetch tweets from configured Twitter accounts and lists"""
        if not self.twitter_enabled:
            logger.info("Twitter/X fetching is disabled")
            return []

        try:
            from twitter_fetcher import TwitterFetcher
            twitter = TwitterFetcher(max_tweets_per_user=self.max_tweets)

            all_tweets = []

            # Fetch from individual accounts
            if self.twitter_accounts:
                logger.info(f"Fetching from {len(self.twitter_accounts)} Twitter accounts")
                tweets = twitter.fetch_multiple_users(self.twitter_accounts)
                all_tweets.extend(tweets)

            # Fetch from lists
            if self.twitter_lists:
                for list_spec in self.twitter_lists:
                    if '/' in list_spec:
                        owner, list_name = list_spec.split('/', 1)
                        tweets = twitter.fetch_list_tweets_nitter(owner, list_name)
                        all_tweets.extend(tweets)

            logger.info(f"Total tweets fetched: {len(all_tweets)}")
            return all_tweets

        except Exception as e:
            logger.error(f"Error fetching Twitter content: {str(e)}")
            return []

    def fetch_all_sources(self) -> List[Dict]:
        """Fetch articles from all configured sources including Twitter"""
        all_articles = []

        # Fetch RSS feeds
        for source in self.sources:
            if source['type'] == 'rss':
                articles = self.fetch_rss_feed(source['url'], source['name'])
                all_articles.extend(articles)

        # Fetch Twitter content
        tweets = self.fetch_twitter_content()
        all_articles.extend(tweets)

        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles

    def get_articles_summary(self, articles: List[Dict]) -> str:
        """Create a text summary of all articles for LLM processing"""
        summary_text = "# Threat Intelligence Articles\n\n"

        for idx, article in enumerate(articles, 1):
            summary_text += f"## Article {idx}: {article['title']}\n"
            summary_text += f"**Source:** {article['source']}\n"
            summary_text += f"**Link:** {article['link']}\n"
            summary_text += f"**Published:** {article['published']}\n\n"
            summary_text += f"**Summary:** {article['summary']}\n\n"
            summary_text += "---\n\n"

        return summary_text
