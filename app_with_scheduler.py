"""Main Flask application with scheduler for Threat Intelligence Digest"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os
from pathlib import Path
import atexit

from fetcher import ThreatIntelFetcher
from summarizer import ThreatIntelSummarizer
from scheduler import DigestScheduler
import config

app = Flask(__name__)
CORS(app)

# Ensure data directory exists
Path(config.DIGEST_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


def generate_digest():
    """Generate a new threat intelligence digest"""
    try:
        # Fetch articles and tweets
        fetcher = ThreatIntelFetcher(
            config.THREAT_INTEL_SOURCES,
            config.MAX_ARTICLES_PER_SOURCE,
            twitter_accounts=config.TWITTER_SECURITY_ACCOUNTS,
            twitter_lists=config.TWITTER_SECURITY_LISTS,
            max_tweets_per_user=config.MAX_TWEETS_PER_USER,
            twitter_enabled=config.TWITTER_ENABLED
        )
        articles = fetcher.fetch_all_sources()

        if not articles:
            return {
                'error': 'No articles fetched',
                'timestamp': datetime.now().isoformat()
            }

        # Summarize articles
        summarizer = ThreatIntelSummarizer(
            config.OPENROUTER_API_KEY,
            config.OPENROUTER_MODEL
        )
        digest = summarizer.summarize_articles(articles)

        # Add metadata
        digest['timestamp'] = datetime.now().isoformat()
        digest['sources_count'] = len(config.THREAT_INTEL_SOURCES)

        # Save digest
        filename = f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(config.DIGEST_STORAGE_PATH, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(digest, f, indent=2, ensure_ascii=False)

        return digest

    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Initialize scheduler
digest_scheduler = DigestScheduler(
    generate_digest,
    hour=config.DIGEST_SCHEDULE_HOUR,
    minute=config.DIGEST_SCHEDULE_MINUTE
)

# Start scheduler
digest_scheduler.start()

# Ensure scheduler stops when app shuts down
atexit.register(lambda: digest_scheduler.stop())


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def api_generate_digest():
    """API endpoint to generate a new digest"""
    digest = generate_digest()
    return jsonify(digest)


@app.route('/api/latest', methods=['GET'])
def api_get_latest_digest():
    """API endpoint to get the latest digest"""
    try:
        # Get all digest files
        digest_files = sorted(
            Path(config.DIGEST_STORAGE_PATH).glob('digest_*.json'),
            reverse=True
        )

        if not digest_files:
            return jsonify({
                'error': 'No digests found',
                'message': 'Generate a new digest to get started'
            }), 404

        # Read the latest digest
        with open(digest_files[0], 'r', encoding='utf-8') as f:
            digest = json.load(f)

        return jsonify(digest)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def api_get_digest_history():
    """API endpoint to get list of all digests"""
    try:
        digest_files = sorted(
            Path(config.DIGEST_STORAGE_PATH).glob('digest_*.json'),
            reverse=True
        )

        history = []
        for filepath in digest_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                digest = json.load(f)
                history.append({
                    'filename': filepath.name,
                    'timestamp': digest.get('timestamp'),
                    'article_count': digest.get('article_count', 0)
                })

        return jsonify(history)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/digest/<filename>', methods=['GET'])
def api_get_digest_by_filename(filename):
    """API endpoint to get a specific digest by filename"""
    try:
        filepath = os.path.join(config.DIGEST_STORAGE_PATH, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Digest not found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            digest = json.load(f)

        return jsonify(digest)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/status', methods=['GET'])
def api_scheduler_status():
    """API endpoint to get scheduler status"""
    next_run = digest_scheduler.get_next_run_time()
    return jsonify({
        'running': True,
        'next_run': next_run.isoformat() if next_run else None,
        'schedule': f"{config.DIGEST_SCHEDULE_HOUR:02d}:{config.DIGEST_SCHEDULE_MINUTE:02d} daily"
    })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
