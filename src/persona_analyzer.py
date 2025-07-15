"""
Persona analyzer module using Gemini LLM to generate user personas.
"""

import os
from typing import Dict, Any, List, Tuple
import logging
import json
from datetime import datetime
from google import genai

from .utils import clean_text, truncate_text, get_sentiment_score

logger = logging.getLogger(__name__)


class PersonaAnalyzer:
    """
    Analyzes Reddit user data to generate comprehensive personas using Gemini LLM.
    """
    
    def __init__(self):
        """Initialize the persona analyzer with Gemini API."""
        try:
            # The client will use GEMINI_API_KEY from the environment
            self.client = genai.Client()
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise
    
    def analyze_user_persona(self, user_data: Dict[str, Any], user_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user data and generate a comprehensive persona.
        
        Args:
            user_data (Dict[str, Any]): Raw user data from Reddit
            user_summary (Dict[str, Any]): User activity summary
            
        Returns:
            Dict[str, Any]: Comprehensive user persona with citations
        """
        logger.info(f"Starting persona analysis for user: {user_data['username']}")
        
        # Prepare data for LLM analysis
        analysis_data = self._prepare_analysis_data(user_data, user_summary)
        
        # Generate persona using Gemini
        persona = self._generate_persona_with_llm(analysis_data)
        
        # Add citations for each characteristic
        persona_with_citations = self._add_citations_to_persona(persona, user_data)
        
        return persona_with_citations
    
    def _prepare_analysis_data(self, user_data: Dict[str, Any], user_summary: Dict[str, Any]) -> str:
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        sample_posts = posts[:20] if posts else []
        sample_comments = comments[:30] if comments else []
        
        posts_text = ""
        for i, post in enumerate(sample_posts):
            title = post.get('title', '')
            selftext = post.get('selftext', '')
            subreddit = post.get('subreddit', '')
            score = post.get('score', 0)
            posts_text += f"Post {i+1} (r/{subreddit}, score: {score}):\n"
            posts_text += f"Title: {title}\n"
            if selftext:
                posts_text += f"Content: {truncate_text(selftext, 300)}\n"
            posts_text += "\n"
        
        comments_text = ""
        for i, comment in enumerate(sample_comments):
            body = comment.get('body', '')
            subreddit = comment.get('subreddit', '')
            score = comment.get('score', 0)
            comments_text += f"Comment {i+1} (r/{subreddit}, score: {score}):\n"
            comments_text += f"{truncate_text(body, 200)}\n\n"
        
        # Calculate average scores safely
        total_post_score = sum(post.get('score', 0) for post in posts)
        total_comment_score = sum(comment.get('score', 0) for comment in comments)
        avg_post_score = total_post_score / len(posts) if posts else 0
        avg_comment_score = total_comment_score / len(comments) if comments else 0
        
        # Get top subreddits
        subreddit_counts = {}
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        for comment in comments:
            subreddit = comment.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        analysis_data = f"""
USER SUMMARY:
- Username: {user_data.get('username', 'Unknown')}
- Account Age: {user_summary.get('account_age_days', 0)} days
- Total Posts: {user_summary.get('total_posts', 0)}
- Total Comments: {user_summary.get('total_comments', 0)}
- Total Karma: {user_summary.get('total_karma', 0)}
- Comment Karma: {user_summary.get('comment_karma', 0)}
- Link Karma: {user_summary.get('link_karma', 0)}
- Average Post Score: {round(avg_post_score, 2)}
- Average Comment Score: {round(avg_comment_score, 2)}
- Top Subreddits: {', '.join([f"{sub[0]} ({sub[1]} posts)" for sub in top_subreddits])}
- Unique Subreddits: {user_summary.get('unique_subreddits', 0)}

SAMPLE POSTS:
{posts_text}

SAMPLE COMMENTS:
{comments_text}
"""
        return analysis_data
    
    def _generate_persona_with_llm(self, analysis_data: str) -> Dict[str, Any]:
        """
        Generate persona using Gemini LLM.
        """
        try:
            prompt = f"""
You are an expert in user behavior analysis and persona creation. Based on the following Reddit user data, create a comprehensive user persona for a single-page document.

Please analyze the user's posts, comments, subreddit activity, and engagement patterns to create a concise persona that includes:

1. **Basic Information**: Age, occupation, location
2. **Personality Traits**: Key personality characteristics (max 4-6 traits)
3. **Reddit Behavior**: How they use Reddit, posting patterns, engagement style
4. **Goals**: What they seem to want or achieve on Reddit
5. **Frustrations**: Potential pain points or challenges they face
6. **Motivations**: For each of the following, output a level ("High", "Medium", or "Low"): Convenience, Wellness, Speed, Preferences. Example: {{"convenience": "High", ...}}
7. **Personality Stats**: For each pair (Introvert/Extrovert, Intuition/Sensing, Feeling/Thinking, Perceiving/Judging), output a value between 0 and 1 (0=fully left, 1=fully right, 0.5=center). Example: {{"introvert_extrovert": 0.7, ...}}

Keep each section concise and focused. Provide specific, actionable insights.

User Data:
{analysis_data}

Please provide the analysis in the following JSON format:
{{
    "occupation": "string",
    "location": "string",
    "personality_traits": ["list of 4-6 key traits"],
    "reddit_behavior": ["list of 4-6 specific behaviors"],
    "goals": ["list of 3-4 goals or motivations"],
    "frustrations": ["list of 3-4 potential frustrations"],
    "summary": "brief 2-3 sentence summary of the user",
    "motivations": {{"convenience": "High", "wellness": "Medium", "speed": "Low", "preferences": "Medium"}},
    "personality_bars": {{"introvert_extrovert": 0.7, "intuition_sensing": 0.5, "feeling_thinking": 0.2, "perceiving_judging": 0.8}}
}}

Respond only with valid JSON.
"""
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            content = response.text.strip()
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                persona = json.loads(content)
                
                # Validate that persona is a dict and has required fields
                if not isinstance(persona, dict):
                    logger.error(f"Persona is not a dict: {type(persona)}")
                    return self._create_fallback_persona()
                
                # Ensure all required fields exist
                required_fields = ['occupation', 'location', 'personality_traits', 'reddit_behavior', 'goals', 'frustrations', 'summary', 'motivations', 'personality_bars']
                for field in required_fields:
                    if field not in persona:
                        persona[field] = self._create_fallback_persona().get(field, None)
                
                logger.info("Successfully generated persona using Gemini LLM")
                return persona
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response content: {content}")
                return self._create_fallback_persona()
        except Exception as e:
            logger.error(f"Error generating persona with Gemini LLM: {e}")
            return self._create_fallback_persona()
    
    def _create_fallback_persona(self) -> Dict[str, Any]:
        return {
            "occupation": "Reddit User",
            "location": "Unknown",
            "personality_traits": ["Active", "Engaged", "Community-oriented"],
            "reddit_behavior": ["Regular poster", "Engages with community", "Shares content"],
            "goals": ["Connect with others", "Share information", "Participate in discussions"],
            "frustrations": ["Limited engagement", "Content visibility", "Community dynamics"],
            "summary": "An active Reddit user who engages regularly with the community through posts and comments."
        }
    
    def _add_citations_to_persona(self, persona: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        # For the new simplified format, we don't need complex citations
        # Just return the persona as is
        return persona 