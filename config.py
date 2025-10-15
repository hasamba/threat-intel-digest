"""Configuration for Threat Digest Summarizer"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

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

# Storage
DIGEST_STORAGE_PATH = 'data/digests/'
MAX_ARTICLES_PER_SOURCE = 5
