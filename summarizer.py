"""LLM-based summarization of threat intelligence articles"""
import requests
from typing import List, Dict
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatIntelSummarizer:
    """Summarizes threat intelligence articles using OpenRouter API"""

    def __init__(self, api_key: str, model: str = 'anthropic/claude-3.5-sonnet'):
        self.api_key = api_key
        self.model = model
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'

        # Validate API key
        if not api_key or api_key == 'your_openrouter_api_key_here':
            logger.error("Invalid or missing OpenRouter API key!")
            logger.error("Please set OPENROUTER_API_KEY in your .env file")
            logger.error("Get your free API key from https://openrouter.ai/")

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

IMPORTANT: Respond with ONLY valid JSON. Do not include any explanatory text, markdown code blocks, or formatting - just the raw JSON object.

Provide a structured summary in the following JSON format:
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

Focus on actionable intelligence and prioritize information that security teams need to know. Return ONLY the JSON object, nothing else."""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/threat-intel-digest',
                'X-Title': 'Threat Intelligence Digest Summarizer'
            }

            data = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 4096,
                'temperature': 0.7
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

            # Log the full response for debugging
            logger.info(f"OpenRouter API response status: {response.status_code}")

            # Extract the assistant's response
            if 'choices' not in result or len(result['choices']) == 0:
                logger.error(f"Invalid API response structure: {result}")
                raise ValueError(f"Invalid API response: {result.get('error', 'No choices in response')}")

            summary_text = result['choices'][0]['message']['content']

            if not summary_text or summary_text.strip() == '':
                logger.error("Empty response from AI model")
                logger.error(f"Full API response: {result}")
                raise ValueError("Empty response from AI model")

            logger.info(f"Received response from {self.model}, length: {len(summary_text)} chars")
            logger.info(f"Response starts with: {summary_text[:200]}")

            # Try to extract JSON from response (sometimes AI includes markdown code blocks)
            summary_text = summary_text.strip()

            # Method 1: Remove markdown code blocks
            if '```json' in summary_text:
                logger.info("Extracting JSON from markdown code block (```json)")
                summary_text = summary_text.split('```json')[1].split('```')[0].strip()
            elif '```' in summary_text:
                logger.info("Extracting JSON from markdown code block (```)")
                summary_text = summary_text.split('```')[1].split('```')[0].strip()

            # Method 2: Find JSON object by looking for { }
            if not summary_text.startswith('{'):
                logger.info("JSON doesn't start with {, searching for JSON object...")
                import re
                json_match = re.search(r'\{.*\}', summary_text, re.DOTALL)
                if json_match:
                    summary_text = json_match.group(0)
                    logger.info("Found JSON object in response")
                else:
                    logger.error("No JSON object found in response")

            # Parse the JSON response
            try:
                summary_data = json.loads(summary_text)
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON. Error: {str(e)}")
                logger.error(f"Response preview (first 1000 chars): {summary_text[:1000]}")
                logger.error(f"Response preview (last 500 chars): {summary_text[-500:]}")
                raise

            summary_data['article_count'] = len(articles)
            summary_data['articles'] = articles

            logger.info(f"Successfully generated threat intelligence digest using {self.model}")
            return summary_data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"API error details: {error_detail}")
                except:
                    logger.error(f"API error response: {e.response.text[:500]}")
            return {
                'executive_summary': f'Error generating summary: API request failed - {str(e)}',
                'critical_threats': [],
                'trending_topics': [],
                'categories': {},
                'article_count': len(articles),
                'articles': articles
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Failed to parse AI response as JSON. This might be due to:")
            logger.error(f"1. Invalid API key or insufficient credits")
            logger.error(f"2. Model not available or incorrect model name")
            logger.error(f"3. AI response is not in valid JSON format")
            return {
                'executive_summary': f'Error parsing summary: The AI model did not return valid JSON. Check your API key and model selection.',
                'critical_threats': [],
                'trending_topics': [],
                'categories': {},
                'article_count': len(articles),
                'articles': articles
            }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
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
