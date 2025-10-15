# Twitter/X Integration Guide

The Threat Intelligence Digest now includes Twitter/X integration to fetch real-time security updates from researchers and organizations.

## How It Works

The application uses **Nitter** (free Twitter frontend) by default to fetch tweets via RSS feeds. This means:
- ✅ No Twitter API key required
- ✅ Completely free
- ✅ No rate limits
- ✅ Works out of the box

## Quick Start

Twitter integration is **enabled by default** with a curated list of security accounts. Just run the app and it will automatically include tweets in your digest!

## Configuration

### 1. Enable/Disable Twitter

In your `.env` file:
```bash
# Enable Twitter fetching (default: True)
TWITTER_ENABLED=True

# Disable Twitter fetching
TWITTER_ENABLED=False
```

### 2. Customize Twitter Accounts

Edit [config.py](config.py) to modify the `TWITTER_SECURITY_ACCOUNTS` list:

```python
TWITTER_SECURITY_ACCOUNTS = [
    'vxunderground',        # Your favorite accounts
    'malwrhunterteam',
    'briankrebs',
    'troyhunt',
    # Add more...
]
```

### 3. Add Twitter Lists

Twitter lists aggregate tweets from multiple accounts. Edit `TWITTER_SECURITY_LISTS` in [config.py](config.py):

```python
TWITTER_SECURITY_LISTS = [
    'cybersecboardrm/cybersecurity-experts',  # Format: username/listname
    'NASA/astronauts',
    # Add more...
]
```

## Pre-Configured Security Accounts

The app comes with these security accounts pre-configured:

| Account | Focus |
|---------|-------|
| @vxunderground | Malware research and collection |
| @malwrhunterteam | Malware hunting |
| @briankrebs | Investigative journalism |
| @schneier | Cryptography and security |
| @troyhunt | Data breaches, Have I Been Pwned |
| @SwiftOnSecurity | Security awareness |
| @GossiTheDog | Cybersecurity research |
| @cyb3rops | Threat detection (Florian Roth) |
| @CISAgov | Official CISA alerts |
| @NSACyber | NSA Cybersecurity |

**See [config.py:73-88](config.py#L73-L88) for the complete list**

## Advanced: Using Twitter API (Optional)

If you prefer to use the official Twitter API instead of Nitter:

### 1. Get Twitter API Access

1. Go to https://developer.twitter.com/
2. Apply for API access (Free tier available)
3. Create a new app
4. Get your Bearer Token

### 2. Configure API Token

Add to your `.env` file:
```bash
TWITTER_API_BEARER_TOKEN=your_bearer_token_here
```

### 3. Update Code

The [twitter_fetcher.py](twitter_fetcher.py) already includes `fetch_twitter_api_v2()` method. You can modify the fetcher to use this method when a token is available.

## Troubleshooting

### No tweets fetched

**Possible causes:**
1. Nitter instances might be down temporarily
   - The app automatically tries multiple Nitter instances
   - Wait a few minutes and try again

2. Twitter accounts might be private or suspended
   - Check if the account exists on Twitter
   - Remove problematic accounts from config

3. Twitter integration is disabled
   - Check `TWITTER_ENABLED=True` in .env

### Slow fetching

- Reduce the number of accounts in `TWITTER_SECURITY_ACCOUNTS`
- Reduce `MAX_TWEETS_PER_USER` in [config.py](config.py)
- Remove Twitter lists (they fetch more content)

### Rate limiting

Nitter has no rate limits, but if using Twitter API:
- Free tier: 1,500 tweets per month
- Reduce number of accounts or tweets per user

## How to Find Good Security Twitter Lists

1. Go to Twitter and search for security-related lists
2. Look for lists maintained by:
   - Security companies
   - Security conferences (DEF CON, Black Hat, etc.)
   - Security researchers
3. The URL format is: `https://twitter.com/{owner}/lists/{list-name}`
4. Add to config as: `'{owner}/{list-name}'`

## Example Lists to Add

```python
TWITTER_SECURITY_LISTS = [
    'cybersecboardrm/cybersecurity-experts',
    'defcon/speakers',
    'sans_isc/infosec-handlers',
]
```

## Nitter Instances

The app uses these public Nitter instances (automatically tries all if one fails):
- https://nitter.net
- https://nitter.poast.org
- https://nitter.privacydev.net
- https://nitter.1d4.us

You can add more instances in [twitter_fetcher.py:18-23](twitter_fetcher.py#L18-L23)

## Data Format

Tweets are fetched with the following information:
- Tweet content/text
- Author username
- Published date
- Link to original tweet
- Source (individual account or list)

This data is then included in the AI summarization along with RSS articles.

## Privacy

When using Nitter (default):
- Your IP address is not shared with Twitter
- No cookies or tracking
- Completely anonymous fetching

## Performance

**Typical fetch times:**
- 15 accounts × 3 tweets each = ~5-10 seconds
- Using Nitter is faster than RSS feeds in many cases
- No API authentication overhead

## Customize Tweet Count

In [config.py](config.py):
```python
MAX_TWEETS_PER_USER = 3  # Tweets per account (default: 3)
```

Lower = faster fetching, higher = more comprehensive digest

## Integration with AI Summarization

Tweets are automatically included in the AI analysis:
- Grouped with other threat intelligence sources
- Analyzed for threats, trends, and recommendations
- Displayed in the digest UI alongside RSS articles

## Need Help?

1. Check the logs for detailed error messages
2. Verify accounts exist and are public
3. Try disabling Twitter temporarily to isolate issues
4. Check if Nitter instances are accessible from your network

## Future Enhancements

Potential improvements:
- Automatic account discovery based on keywords
- Tweet sentiment analysis
- Thread detection and consolidation
- Image/media extraction from tweets
- Retweet and quote tweet handling
