#!/usr/bin/env python3
"""
Reddit User Persona Analyzer

Main script for analyzing Reddit user profiles and generating comprehensive personas.
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.reddit_scraper import RedditScraper
from src.persona_analyzer import PersonaAnalyzer
from src.output_generator import OutputGenerator
from src.utils import extract_username_from_url

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment():
    """Load environment variables from .env file."""
    try:
        load_dotenv()
        logger.info("Environment variables loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")


def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    return True


def get_user_input() -> Optional[str]:
    """
    Get Reddit profile URL from user input.
    
    Returns:
        Optional[str]: Reddit profile URL or None if user wants to exit
    """
    print("\n" + "="*60)
    print("REDDIT USER PERSONA ANALYZER")
    print("="*60)
    print("\nThis tool analyzes Reddit user profiles to generate comprehensive personas.")
    print("Enter a Reddit profile URL to analyze, or 'quit' to exit.")
    print("\nExample URLs:")
    print("  https://www.reddit.com/user/spez/")
    print("  https://www.reddit.com/user/kn0thing/")
    print()
    
    while True:
        try:
            url = input("Enter Reddit profile URL (or 'quit' to exit): ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                return None
            
            if not url:
                print("Please enter a valid URL.")
                continue
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if 'reddit.com' not in url or '/user/' not in url:
                print("Please enter a valid Reddit user profile URL.")
                continue
            
            return url
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            return None
        except Exception as e:
            logger.error(f"Error getting user input: {e}")
            print("An error occurred. Please try again.")


def analyze_user_profile(url: str) -> bool:
    """
    Analyze a Reddit user profile and generate persona.
    
    Args:
        url (str): Reddit profile URL
        
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    try:
        print(f"\nAnalyzing profile: {url}")
        print("This may take a few minutes...")
        
        # Initialize components
        scraper = RedditScraper()
        analyzer = PersonaAnalyzer()
        output_gen = OutputGenerator()
        
        # Extract username for display
        username = extract_username_from_url(url)
        if not username:
            print("Error: Could not extract username from URL")
            return False
        
        print(f"Username: {username}")
        
        # 1. Fetch user data from Reddit
        print("1. Fetching user data from Reddit...")
        try:
            user_data = scraper.fetch_user_data(username)
            profile_info = user_data['profile_info']
            posts = user_data['posts']
            comments = user_data['comments']
        except Exception as e:
            print(f"❌ Error fetching user data: {e}")
            return
        
        # 2. Generate user activity summary
        print("2. Generating user activity summary...")
        user_summary = {
            'username': username,
            'account_age_days': int((datetime.now().timestamp() - profile_info['created_utc']) / 86400),
            'total_posts': len(posts),
            'total_comments': len(comments),
            'total_karma': profile_info['total_karma'],
            'comment_karma': profile_info['comment_karma'],
            'link_karma': profile_info['link_karma'],
            'profile_img': profile_info.get('profile_img'),
            'profile_color': profile_info.get('profile_color'),
            'unique_subreddits': len(set([p['subreddit'] for p in posts] + [c['subreddit'] for c in comments]))
        }
        
        print(f"   Found {len(posts)} posts and {len(comments)} comments")
        print(f"   Account age: {user_summary['account_age_days']} days")
        print(f"   Total karma: {user_summary['total_karma']}")
        
        # 3. Analyze user persona with AI
        print("3. Analyzing user persona with AI...")
        try:
            # Prepare user_data in the format expected by the analyzer
            user_data = {
                'username': username,
                'posts': posts,
                'comments': comments
            }
            persona = analyzer.analyze_user_persona(user_data, user_summary)
        except Exception as e:
            print(f"❌ Error analyzing persona: {e}")
            return
        
        # 4. Generate persona analysis file
        print("4. Generating persona analysis file...")
        try:
            output_file = output_gen.generate_persona_file(username, user_summary, persona)
            print(f"✅ Analysis complete!")
            print(f"📄 Persona file saved: {output_file}")
            
            # Print summary
            print(f"\n📊 Analysis Summary:")
            print(f"   • Username: {username}")
            print(f"   • Posts analyzed: {len(posts)}")
            print(f"   • Comments analyzed: {len(comments)}")
            print(f"   • Subreddits: {user_summary['unique_subreddits']}")
            print(f"   • Account age: {user_summary['account_age_days']} days")
            
        except Exception as e:
            print(f"❌ Error generating output: {e}")
            return
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        print(f"❌ An unexpected error occurred: {e}")
        return False


def main():
    """Main function to run the Reddit persona analyzer."""
    print("Starting Reddit User Persona Analyzer...")
    
    # Load environment variables
    load_environment()
    
    # Validate environment
    if not validate_environment():
        print("\nPlease set up your environment variables:")
        print("1. Copy env_example.txt to .env")
        print("2. Add your Reddit API credentials and Gemini API key")
        print("3. Run the script again")
        return
    
    # Main loop
    while True:
        try:
            # Get user input
            url = get_user_input()
            
            if url is None:
                break
            
            # Analyze the profile
            success = analyze_user_profile(url)
            
            if success:
                print("\n" + "="*60)
                print("Analysis completed successfully!")
                print("Check the generated file for detailed results.")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("Analysis failed. Please try again with a different URL.")
                print("="*60)
            
            # Ask if user wants to analyze another profile
            print("\nWould you like to analyze another profile? (y/n): ", end="")
            try:
                response = input().strip().lower()
                if response not in ['y', 'yes']:
                    print("Goodbye!")
                    break
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main() 