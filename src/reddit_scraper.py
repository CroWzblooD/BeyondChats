"""
Reddit scraper module for fetching user posts and comments.
"""

import os
import praw
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time

from .utils import clean_text, extract_username_from_url

logger = logging.getLogger(__name__)


class RedditScraper:
    """
    Reddit scraper for fetching user posts and comments.
    """
    
    def __init__(self):
        """Initialize Reddit scraper with API credentials."""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'RedditPersonaAnalyzer/1.0')
            )
            logger.info("Reddit API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            raise
    
    def fetch_user_data(self, username: str) -> Dict[str, Any]:
        """
        Fetch comprehensive user data from Reddit.
        
        Args:
            username (str): Reddit username
            
        Returns:
            Dict[str, Any]: User data including posts, comments, and profile info
        """
        try:
            logger.info(f"Fetching data for user: {username}")
            
            # Get user object
            user = self.reddit.redditor(username)
            
            # Get basic profile info
            profile_info = {
                'name': user.name,
                'created_utc': user.created_utc,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'total_karma': user.comment_karma + user.link_karma,
                'profile_img': None,
                'profile_color': None
            }
            
            # Try to get profile image
            try:
                if hasattr(user, 'icon_img') and user.icon_img:
                    profile_info['profile_img'] = user.icon_img
                if hasattr(user, 'subreddit') and user.subreddit:
                    if hasattr(user.subreddit, 'icon_img') and user.subreddit.icon_img:
                        profile_info['profile_img'] = user.subreddit.icon_img
                    if hasattr(user.subreddit, 'primary_color') and user.subreddit.primary_color:
                        profile_info['profile_color'] = user.subreddit.primary_color
            except Exception as e:
                logger.warning(f"Could not fetch profile image for {username}: {e}")
            
            # Fetch posts
            logger.info(f"Fetching posts for {username}")
            posts = []
            try:
                for submission in user.submissions.new(limit=50):
                    posts.append({
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'created_utc': submission.created_utc,
                        'num_comments': submission.num_comments,
                        'url': submission.url,
                        'permalink': submission.permalink
                    })
            except Exception as e:
                logger.warning(f"Error fetching posts for {username}: {e}")
            
            # Fetch comments
            logger.info(f"Fetching comments for {username}")
            comments = []
            try:
                for comment in user.comments.new(limit=100):
                    comments.append({
                        'body': comment.body,
                        'subreddit': comment.subreddit.display_name,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'permalink': comment.permalink,
                        'parent_id': comment.parent_id
                    })
            except Exception as e:
                logger.warning(f"Error fetching comments for {username}: {e}")
            
            user_data = {
                'profile_info': profile_info,
                'posts': posts,
                'comments': comments
            }
            
            logger.info(f"Successfully fetched data for {username}: {len(posts)} posts, {len(comments)} comments")
            return user_data
            
        except Exception as e:
            logger.error(f"Error fetching user data for {username}: {e}")
            raise 