"""
Utility functions for Reddit Persona Analyzer.
"""

import re
import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_username_from_url(url: str) -> Optional[str]:
    """
    Extract Reddit username from a Reddit profile URL.
    
    Args:
        url (str): Reddit profile URL
        
    Returns:
        Optional[str]: Username if valid, None otherwise
    """
    try:
        # Handle different URL formats
        url = url.strip()
        
        # Remove trailing slash if present
        if url.endswith('/'):
            url = url[:-1]
            
        # Extract username from URL
        if '/user/' in url:
            username = url.split('/user/')[-1]
        elif '/u/' in url:
            username = url.split('/u/')[-1]
        else:
            # Try to extract from domain
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 2:
                username = path_parts[1]
            else:
                return None
                
        # Clean username
        username = username.strip()
        if username:
            return username
            
    except Exception as e:
        logger.error(f"Error extracting username from URL {url}: {e}")
        return None
    
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text for analysis.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove Reddit markdown links first
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove bold and italic markdown
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold formatting
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic formatting
    
    # Remove extra whitespace again (to fix double spaces after URL removal)
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length while preserving word boundaries.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."


def create_output_filename(username: str) -> str:
    """
    Create a standardized output filename for persona analysis.
    
    Args:
        username (str): Reddit username
        
    Returns:
        str: Output filename
    """
    # Clean username for filename
    clean_username = re.sub(r'[^\w\-_]', '_', username)
    return f"{clean_username}_persona.txt"


def ensure_output_directory(directory: str) -> None:
    """
    Ensure the output directory exists.
    
    Args:
        directory (str): Directory path
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Output directory ensured: {directory}")
    except Exception as e:
        logger.error(f"Error creating output directory {directory}: {e}")


def format_citation(post_data: Dict[str, Any], comment_data: Dict[str, Any] = None) -> str:
    """
    Format a citation for a post or comment.
    
    Args:
        post_data (Dict[str, Any]): Post data
        comment_data (Dict[str, Any], optional): Comment data
        
    Returns:
        str: Formatted citation
    """
    if comment_data:
        return f"Comment in r/{post_data.get('subreddit', 'unknown')}: '{truncate_text(comment_data.get('body', ''), 100)}'"
    else:
        return f"Post in r/{post_data.get('subreddit', 'unknown')}: '{truncate_text(post_data.get('title', ''), 100)}'"


def get_sentiment_score(text: str) -> float:
    """
    Get a simple sentiment score for text.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        float: Sentiment score (-1 to 1)
    """
    if not text:
        return 0.0
    
    # Simple keyword-based sentiment analysis
    positive_words = {'good', 'great', 'awesome', 'love', 'like', 'happy', 'excellent', 'amazing', 'wonderful'}
    negative_words = {'bad', 'terrible', 'hate', 'awful', 'horrible', 'dislike', 'sad', 'angry', 'frustrated'}
    
    words = text.lower().split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    total_words = len(words)
    if total_words == 0:
        return 0.0
    
    return (positive_count - negative_count) / total_words 