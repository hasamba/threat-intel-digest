"""Configuration for Threat Digest Summarizer"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# OpenRouter Model Selection
# Popular options:
# - anthropic/claude-3.5-sonnet (Best quality, more expensive)
# - anthropic/claude-3-haiku (Faster, cheaper)
# - openai/gpt-4-turbo (Alternative to Claude)
# - openai/gpt-3.5-turbo (Cheapest option)
# - meta-llama/llama-3.1-70b-instruct (Free tier available)
# - google/gemini-pro (Good balance)
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

# Flask Configuration
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Digest Schedule
DIGEST_SCHEDULE_HOUR = int(os.getenv('DIGEST_SCHEDULE_HOUR', 8))
DIGEST_SCHEDULE_MINUTE = int(os.getenv('DIGEST_SCHEDULE_MINUTE', 0))

# Threat Intelligence Sources
THREAT_INTEL_SOURCES = [
    {
        'name': 'Krebs on Security',
        'url': 'https://krebsonsecurity.com/feed/',
        'type': 'rss'
    },
    {
        'name': 'Schneier on Security',
        'url': 'https://www.schneier.com/feed/atom/',
        'type': 'rss'
    },
    {
        'name': 'The Hacker News',
        'url': 'https://feeds.feedburner.com/TheHackersNews',
        'type': 'rss'
    },
    {
        'name': 'Bleeping Computer',
        'url': 'https://www.bleepingcomputer.com/feed/',
        'type': 'rss'
    },
    {
        'name': 'Dark Reading',
        'url': 'https://www.darkreading.com/rss.xml',
        'type': 'rss'
    },
    {
        'name': 'Threatpost',
        'url': 'https://threatpost.com/feed/',
        'type': 'rss'
    },
    {
        'name': 'CISA Alerts',
        'url': 'https://www.cisa.gov/cybersecurity-advisories/all.xml',
        'type': 'rss'
    }
]

# Twitter/X Configuration (Optional - leave empty to use Nitter for free)
# NOTE: Disabled by default because Nitter instances are often down
# Set TWITTER_ENABLED=True in .env to enable
TWITTER_API_BEARER_TOKEN = os.getenv('TWITTER_API_BEARER_TOKEN', '')
TWITTER_ENABLED = os.getenv('TWITTER_ENABLED', 'False').lower() == 'true'

# Twitter/X Security Accounts to Follow
# These are prominent security researchers and organizations
TWITTER_SECURITY_ACCOUNTS = [
    'TheCyberVibes',        # Cyber threat intelligence
    'vxunderground',        # Malware research and collection
    'malwrhunterteam',      # Malware hunting team
    'campuscodi',           # Security researcher
    'briankrebs',           # Krebs on Security
    'schneier',             # Bruce Schneier
    'troyhunt',             # Have I Been Pwned creator
    'SwiftOnSecurity',      # Security awareness
    'gentilkiwi',           # Mimikatz creator
    'GossiTheDog',          # Cybersecurity researcher
    'cyb3rops',             # Florian Roth - Threat detection
    'jonnyablanc',          # Threat intelligence
    'malware_traffic',      # Malware traffic analysis
    'CISAgov',              # CISA official
    'NSACyber',             # NSA Cybersecurity
]

# Twitter Lists to Follow (owner/list-name)
# Example: 'NASA/astronauts' would be https://twitter.com/NASA/lists/astronauts
TWITTER_SECURITY_LISTS = [
    # Add your favorite security Twitter lists here
    # Format: 'username/listname'
    # Example: 'cybersecboardrm/cybersecurity-experts'
]

# Storage
DIGEST_STORAGE_PATH = 'data/digests/'
MAX_ARTICLES_PER_SOURCE = 5
MAX_TWEETS_PER_USER = 3
