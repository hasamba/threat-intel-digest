"""Fetch tweets from security researchers and organizations"""
import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterFetcher:
    """
    Fetches tweets from security accounts using multiple methods:
    1. Nitter RSS feeds (free, no API key needed)
    2. Twitter API v2 (optional, requires API key)
    3. RSS Bridge (free alternative)
    """

    def __init__(self, max_tweets_per_user: int = 5):
        self.max_tweets = max_tweets_per_user
        # List of public Nitter instances (fallback if one is down)
        self.nitter_instances = [
            'https://nitter.net',
            'https://nitter.poast.org',
            'https://nitter.privacydev.net',
            'https://nitter.1d4.us',
        ]

    def fetch_user_tweets_nitter(self, username: str, instance_url: Optional[str] = None) -> List[Dict]:
        """
        Fetch tweets from a user using Nitter RSS feed (free, no API key)

        Args:
            username: Twitter username (without @)
            instance_url: Specific Nitter instance to use (optional)

        Returns:
            List of tweet dictionaries
        """
        instances = [instance_url] if instance_url else self.nitter_instances

        for instance in instances:
            try:
                # Nitter RSS feed URL format: {instance}/{username}/rss
                feed_url = f"{instance}/{username}/rss"

                logger.info(f"Fetching tweets from @{username} via {instance}")
                feed = feedparser.parse(feed_url)

                if not feed.entries:
                    logger.warning(f"No tweets found for @{username} at {instance}")
                    continue

                tweets = []
                for entry in feed.entries[:self.max_tweets]:
                    # Parse published date
                    published = None
                    if hasattr(entry, 'published_parsed'):
                        published = datetime(*entry.published_parsed[:6])

                    tweet = {
                        'title': entry.get('title', f"Tweet from @{username}"),
                        'content': entry.get('description', entry.get('summary', '')),
                        'link': entry.get('link', ''),
                        'published': published.isoformat() if published else None,
                        'source': f"@{username}",
                        'source_type': 'twitter',
                        'author': username
                    }
                    tweets.append(tweet)

                logger.info(f"Fetched {len(tweets)} tweets from @{username}")
                return tweets

            except Exception as e:
                logger.warning(f"Failed to fetch from {instance} for @{username}: {str(e)}")
                continue

        logger.error(f"All Nitter instances failed for @{username}")
        return []

    def fetch_list_tweets_nitter(self, list_owner: str, list_name: str, instance_url: Optional[str] = None) -> List[Dict]:
        """
        Fetch tweets from a Twitter list using Nitter

        Args:
            list_owner: Username of the list owner
            list_name: Name of the list
            instance_url: Specific Nitter instance to use (optional)

        Returns:
            List of tweet dictionaries
        """
        instances = [instance_url] if instance_url else self.nitter_instances

        for instance in instances:
            try:
                # Nitter list RSS feed URL format: {instance}/{owner}/lists/{list}/rss
                feed_url = f"{instance}/{list_owner}/lists/{list_name}/rss"

                logger.info(f"Fetching tweets from list @{list_owner}/{list_name} via {instance}")
                feed = feedparser.parse(feed_url)

                if not feed.entries:
                    logger.warning(f"No tweets found for list @{list_owner}/{list_name} at {instance}")
                    continue

                tweets = []
                for entry in feed.entries[:self.max_tweets * 3]:  # Lists typically have more content
                    # Parse published date
                    published = None
                    if hasattr(entry, 'published_parsed'):
                        published = datetime(*entry.published_parsed[:6])

                    # Extract author from title or link
                    author = entry.get('author', 'Unknown')

                    tweet = {
                        'title': entry.get('title', f"Tweet from list {list_name}"),
                        'content': entry.get('description', entry.get('summary', '')),
                        'link': entry.get('link', ''),
                        'published': published.isoformat() if published else None,
                        'source': f"List: {list_owner}/{list_name}",
                        'source_type': 'twitter_list',
                        'author': author
                    }
                    tweets.append(tweet)

                logger.info(f"Fetched {len(tweets)} tweets from list @{list_owner}/{list_name}")
                return tweets

            except Exception as e:
                logger.warning(f"Failed to fetch list from {instance}: {str(e)}")
                continue

        logger.error(f"All Nitter instances failed for list @{list_owner}/{list_name}")
        return []

    def fetch_multiple_users(self, usernames: List[str]) -> List[Dict]:
        """
        Fetch tweets from multiple users

        Args:
            usernames: List of Twitter usernames

        Returns:
            Combined list of tweets from all users
        """
        all_tweets = []

        for username in usernames:
            tweets = self.fetch_user_tweets_nitter(username)
            all_tweets.extend(tweets)

        logger.info(f"Fetched total of {len(all_tweets)} tweets from {len(usernames)} users")
        return all_tweets

    def fetch_twitter_api_v2(self, username: str, bearer_token: str) -> List[Dict]:
        """
        Fetch tweets using Twitter API v2 (requires API key)

        Args:
            username: Twitter username
            bearer_token: Twitter API Bearer Token

        Returns:
            List of tweet dictionaries
        """
        try:
            # First, get user ID
            user_url = f"https://api.twitter.com/2/users/by/username/{username}"
            headers = {'Authorization': f'Bearer {bearer_token}'}

            user_response = requests.get(user_url, headers=headers)
            user_response.raise_for_status()
            user_id = user_response.json()['data']['id']

            # Get user's tweets
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(self.max_tweets, 10),
                'tweet.fields': 'created_at,text,public_metrics',
                'exclude': 'retweets,replies'
            }

            tweets_response = requests.get(tweets_url, headers=headers, params=params)
            tweets_response.raise_for_status()

            tweets = []
            for tweet_data in tweets_response.json().get('data', []):
                tweet = {
                    'title': f"Tweet from @{username}",
                    'content': tweet_data.get('text', ''),
                    'link': f"https://twitter.com/{username}/status/{tweet_data['id']}",
                    'published': tweet_data.get('created_at'),
                    'source': f"@{username}",
                    'source_type': 'twitter',
                    'author': username
                }
                tweets.append(tweet)

            logger.info(f"Fetched {len(tweets)} tweets from @{username} via Twitter API")
            return tweets

        except Exception as e:
            logger.error(f"Twitter API v2 error for @{username}: {str(e)}")
            return []

    def format_tweets_for_digest(self, tweets: List[Dict]) -> str:
        """Format tweets into readable text"""
        if not tweets:
            return "No tweets fetched."

        formatted = "# Twitter/X Security Updates\n\n"
        for idx, tweet in enumerate(tweets, 1):
            formatted += f"## Tweet {idx} - {tweet['source']}\n"
            formatted += f"**Published:** {tweet.get('published', 'Unknown')}\n"
            formatted += f"**Content:** {tweet.get('content', tweet.get('title', ''))}\n"
            formatted += f"**Link:** {tweet['link']}\n\n"
            formatted += "---\n\n"

        return formatted
