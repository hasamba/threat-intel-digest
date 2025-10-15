"""LLM-based summarization of threat intelligence articles"""
import anthropic
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatIntelSummarizer:
    """Summarizes threat intelligence articles using Claude AI"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def summarize_articles(self, articles: List[Dict]) -> Dict:
        """
        Summarize multiple threat intelligence articles into a daily digest

        Returns a structured digest with:
        - Executive summary
        - Critical threats
        - Trending topics
        - Detailed summaries by category
        """

        if not articles:
            return {
                'executive_summary': 'No new threat intelligence articles found today.',
                'critical_threats': [],
                'trending_topics': [],
                'category_summaries': {},
                'article_count': 0
            }

        # Prepare articles text for the LLM
        articles_text = self._format_articles_for_llm(articles)

        # Create the prompt for summarization
        prompt = f"""You are a cybersecurity analyst creating a daily threat intelligence digest.
Analyze the following threat intelligence articles and create a comprehensive summary.

{articles_text}

Please provide a structured summary in the following JSON format:
{{
    "executive_summary": "A 2-3 paragraph executive summary of the most important security threats and trends",
    "critical_threats": [
        {{
            "title": "Threat name",
            "severity": "Critical/High/Medium",
            "description": "Brief description",
            "affected_systems": "Systems or software affected",
            "recommendation": "Key action items"
        }}
    ],
    "trending_topics": ["Topic 1", "Topic 2", "Topic 3"],
    "categories": {{
        "Malware & Ransomware": "Summary of malware-related news",
        "Vulnerabilities & Exploits": "Summary of vulnerability disclosures",
        "Data Breaches": "Summary of data breach incidents",
        "Threat Actors": "Summary of threat actor activity",
        "Security Tools & Defenses": "Summary of defensive security news"
    }},
    "key_recommendations": [
        "Action item 1",
        "Action item 2"
    ]
}}

Focus on actionable intelligence and prioritize information that security teams need to know."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            summary_text = response.content[0].text

            # Parse the JSON response
            import json
            summary_data = json.loads(summary_text)
            summary_data['article_count'] = len(articles)
            summary_data['articles'] = articles

            logger.info("Successfully generated threat intelligence digest")
            return summary_data

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'executive_summary': f'Error generating summary: {str(e)}',
                'critical_threats': [],
                'trending_topics': [],
                'categories': {},
                'article_count': len(articles),
                'articles': articles
            }

    def _format_articles_for_llm(self, articles: List[Dict]) -> str:
        """Format articles into a readable text format for the LLM"""
        formatted = ""

        for idx, article in enumerate(articles, 1):
            formatted += f"\n{'='*80}\n"
            formatted += f"ARTICLE {idx}\n"
            formatted += f"{'='*80}\n"
            formatted += f"Title: {article['title']}\n"
            formatted += f"Source: {article['source']}\n"
            formatted += f"Link: {article['link']}\n"
            formatted += f"Published: {article.get('published', 'Unknown')}\n"
            formatted += f"\nContent:\n{article.get('summary', 'No summary available')}\n"

        return formatted
