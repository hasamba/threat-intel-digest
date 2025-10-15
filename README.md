# Threat Intelligence Digest Summarizer

An AI-powered web application that fetches the latest threat intelligence reports and security blogs, summarizes them using AI (via OpenRouter), and presents a comprehensive daily digest to security professionals.

## Features

- **Automated Fetching**: Pulls articles from multiple trusted threat intelligence sources via RSS feeds
- **AI Summarization**: Uses OpenRouter API to access multiple AI models (Claude, GPT-4, Llama, etc.) for intelligent analysis
- **Flexible Model Selection**: Choose from Claude 3.5, GPT-4, or free models like Llama 3.1
- **Daily Digest**: Automatically generates digests on a scheduled basis
- **Web Interface**: Clean, modern UI for viewing and managing digests
- **Historical Archive**: Stores all previous digests for reference
- **Categorized Intelligence**: Organizes threats by severity and category
- **Actionable Recommendations**: Provides key security recommendations based on current threats

## Threat Intelligence Sources

The application fetches from the following trusted sources:
- Krebs on Security
- Schneier on Security
- The Hacker News
- Bleeping Computer
- Dark Reading
- Threatpost
- CISA Cybersecurity Advisories

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface (Frontend)                 │
│                  HTML/CSS/JavaScript UI                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ REST API
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Flask Backend (app.py)                     │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │    Fetcher     │  │  Summarizer  │  │   Scheduler     │ │
│  │  (fetcher.py)  │  │(summarizer.py│  │ (scheduler.py)  │ │
│  │                │  │              │  │                 │ │
│  │ - RSS feeds    │  │ - OpenRouter │  │ - Daily tasks   │ │
│  │ - Web scraping │  │ - Multi-LLM  │  │ - APScheduler   │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                      │
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Data Storage (data/digests/)                    │
│                    JSON digest files                         │
└──────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (get free credits at https://openrouter.ai/)

### Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

   **Optional**: Choose a specific model (defaults to Claude 3.5 Sonnet):
   ```
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   ```

   **Popular Model Options:**
   - `anthropic/claude-3.5-sonnet` - Best quality (recommended)
   - `anthropic/claude-3-haiku` - Faster and cheaper
   - `openai/gpt-4-turbo` - OpenAI's flagship model
   - `openai/gpt-3.5-turbo` - Cheapest option
   - `meta-llama/llama-3.1-70b-instruct` - Free tier available
   - `google/gemini-pro` - Good balance of quality and cost

   **Get your OpenRouter API key:**
   1. Sign up at https://openrouter.ai/
   2. Get free credits (usually $1-5 for new users)
   3. Copy your API key from the dashboard

3. **Configure Settings** (Optional)

   Edit [config.py](config.py) to customize:
   - Threat intelligence sources
   - Digest schedule time
   - Maximum articles per source
   - Storage location

## Usage

### Running the Application

#### Option 1: Basic Mode (No Scheduler)
```bash
python app.py
```

#### Option 2: With Automated Daily Digest (Recommended)
```bash
python app_with_scheduler.py
```

The application will start on `http://localhost:5000` by default.

### Web Interface

Once running, open your browser to `http://localhost:5000`

**Available Actions:**
- **Generate New Digest**: Fetch and analyze the latest threat intelligence
- **Load Latest Digest**: View the most recent digest
- **View History**: Browse all previous digests

### API Endpoints

The application exposes the following REST API endpoints:

- `GET /` - Web interface
- `POST /api/generate` - Generate a new digest
- `GET /api/latest` - Get the latest digest
- `GET /api/history` - Get list of all digests
- `GET /api/digest/<filename>` - Get specific digest by filename
- `GET /api/scheduler/status` - Get scheduler status (when using app_with_scheduler.py)

### Example API Usage

```bash
# Generate new digest
curl -X POST http://localhost:5000/api/generate

# Get latest digest
curl http://localhost:5000/api/latest

# Get digest history
curl http://localhost:5000/api/history
```

## Digest Output Structure

Each digest includes:

### Executive Summary
A high-level overview of the most important security threats and trends

### Critical Threats
Detailed information about urgent security threats including:
- Threat title and severity (Critical/High/Medium)
- Description
- Affected systems
- Recommended actions

### Trending Topics
Current security topics and themes being discussed

### Category Summaries
Organized summaries by category:
- Malware & Ransomware
- Vulnerabilities & Exploits
- Data Breaches
- Threat Actors
- Security Tools & Defenses

### Key Recommendations
Actionable security recommendations based on current threats

### Source Articles
Links to all original articles for detailed research

## Scheduling

The scheduler ([app_with_scheduler.py](app_with_scheduler.py)) automatically generates digests daily. Default time is 8:00 AM, configurable in [.env](.env.example):

```
DIGEST_SCHEDULE_HOUR=8
DIGEST_SCHEDULE_MINUTE=0
```

## Data Storage

Digests are stored as JSON files in `data/digests/` directory with the naming format:
```
digest_YYYYMMDD_HHMMSS.json
```

This allows for:
- Easy archival and backup
- Historical analysis
- Portable format
- Version control friendly

## Customization

### Adding New Threat Intelligence Sources

Edit [config.py](config.py) and add to `THREAT_INTEL_SOURCES`:

```python
{
    'name': 'Source Name',
    'url': 'https://example.com/feed.xml',
    'type': 'rss'
}
```

### Customizing Summarization

Edit [summarizer.py](summarizer.py) to modify:
- The prompt sent to the AI model
- Summary structure and categories
- Analysis depth
- Output format

Or change the model in `.env`:
```
OPENROUTER_MODEL=openai/gpt-4-turbo  # Switch to GPT-4
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct  # Use free Llama
```

### Changing the UI

Edit [templates/index.html](templates/index.html) to customize:
- Layout and styling
- Color scheme
- Information display
- Interactive features

## Security Considerations

This tool is designed for **defensive security purposes only**:
- Helps security teams stay informed about current threats
- Provides actionable intelligence for defense
- Supports threat hunting and incident response
- Aids in security awareness and training

## Troubleshooting

### Common Issues

**No articles fetched:**
- Check your internet connection
- Verify RSS feed URLs are accessible
- Some sources may be temporarily down

**API errors:**
- Verify your OpenRouter API key is correct in `.env`
- Check you have sufficient credits at https://openrouter.ai/
- Try a different model (some require payment, others are free)
- Check the console logs for detailed error messages

**Scheduler not running:**
- Use `app_with_scheduler.py` instead of `app.py`
- Check the logs for scheduler status
- Verify APScheduler is installed

## File Structure

```
threat-digest-summarizer/
├── app.py                      # Main Flask app (basic)
├── app_with_scheduler.py       # Flask app with scheduler
├── fetcher.py                  # Threat intel fetching logic
├── summarizer.py               # AI summarization logic
├── scheduler.py                # Automated scheduling
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
├── templates/
│   └── index.html            # Web interface
└── data/
    └── digests/              # Stored digest files
```

## Dependencies

- **Flask**: Web framework
- **feedparser**: RSS feed parsing
- **requests**: HTTP requests and OpenRouter API integration
- **beautifulsoup4**: HTML parsing
- **apscheduler**: Task scheduling
- **python-dotenv**: Environment management

## License

This project is designed for defensive security purposes and should be used responsibly and ethically.

## Future Enhancements

Potential improvements:
- Email delivery of daily digests
- Slack/Teams integration
- Custom filtering and tagging
- Threat severity scoring
- Integration with SIEM systems
- Export to PDF/Word formats
- Multi-language support
- Machine learning for trend prediction

## Support

For issues or questions:
1. Check this README
2. Review the logs in the console
3. Verify your configuration in `config.py` and `.env`
4. Test individual components (fetcher, summarizer) separately

## Credits

Powered by:
- OpenRouter for unified AI API access (supporting Claude, GPT-4, Llama, and more)
- Various threat intelligence sources for security news
- Open source Python libraries

## Why OpenRouter?

**OpenRouter Benefits:**
- **Multiple Models**: Access Claude, GPT-4, Llama, Gemini, and many others with one API
- **Free Credits**: New users get free credits to try different models
- **Cost Effective**: Compare prices and choose the best model for your budget
- **No Vendor Lock-in**: Switch between AI providers without code changes
- **Free Models Available**: Use models like Llama 3.1 at no cost

**Pricing Examples (approximate):**
- Claude 3.5 Sonnet: ~$3 per million tokens
- GPT-4 Turbo: ~$10 per million tokens
- GPT-3.5 Turbo: ~$0.50 per million tokens
- Llama 3.1 70B: Often free or very cheap
- Daily digest cost: $0.01 - $0.10 per day depending on model choice
