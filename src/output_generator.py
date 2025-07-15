"""
Output generator module for formatting and saving persona analysis.
"""

import os
from typing import Dict, Any, List
import logging
from datetime import datetime

from .utils import create_output_filename, ensure_output_directory, format_citation
from .pdf_persona_generator import PDFPersonaGenerator

logger = logging.getLogger(__name__)


class OutputGenerator:
    """
    Generates formatted output files for persona analysis.
    """
    
    def __init__(self, output_dir: str = "data/sample_outputs"):
        """
        Initialize output generator.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        ensure_output_directory(output_dir)
        self.pdf_generator = PDFPersonaGenerator(output_dir)
    
    def generate_persona_file(self, username: str, user_summary: Dict[str, Any], 
                             persona: Dict[str, Any]) -> str:
        """
        Generate a comprehensive persona analysis file (both text and PDF).
        
        Args:
            username (str): Reddit username
            user_summary (Dict[str, Any]): User activity summary
            persona (Dict[str, Any]): Generated persona with citations
            
        Returns:
            str: Path to the generated PDF file
        """
        # Defensive check for persona type
        if not isinstance(persona, dict):
            logger.error(f"Persona is not a dict! Actual value: {repr(persona)}")
            # Use fallback persona
            persona = {
                "occupation": "Reddit User",
                "location": "Unknown",
                "personality_traits": ["Active", "Engaged", "Community-oriented"],
                "reddit_behavior": ["Regular poster", "Engages with community", "Shares content"],
                "goals": ["Connect with others", "Share information", "Participate in discussions"],
                "frustrations": ["Limited engagement", "Content visibility", "Community dynamics"],
                "summary": "An active Reddit user who engages regularly with the community through posts and comments."
            }
        # Generate text file
        filename = create_output_filename(username)
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header
                f.write(self._generate_header(username, user_summary))
                
                # Write persona sections with error handling
                try:
                    f.write(self._generate_demographics_section(persona.get('demographics', {})))
                except Exception as e:
                    logger.error(f"Error in demographics section: {e}")
                    f.write("\nDEMOGRAPHICS & BACKGROUND\n" + "-"*40 + "\nUnable to generate demographics section.\n\n")
                
                try:
                    f.write(self._generate_interests_section(persona.get('interests', {})))
                except Exception as e:
                    logger.error(f"Error in interests section: {e}")
                    f.write("\nINTERESTS & HOBBIES\n" + "-"*40 + "\nUnable to generate interests section.\n\n")
                
                try:
                    f.write(self._generate_communication_section(persona.get('communication_style', {})))
                except Exception as e:
                    logger.error(f"Error in communication section: {e}")
                    f.write("\nCOMMUNICATION STYLE\n" + "-"*40 + "\nUnable to generate communication section.\n\n")
                
                try:
                    f.write(self._generate_personality_section(persona.get('personality_traits', {})))
                except Exception as e:
                    logger.error(f"Error in personality section: {e}")
                    f.write("\nPERSONALITY TRAITS\n" + "-"*40 + "\nUnable to generate personality section.\n\n")
                
                try:
                    f.write(self._generate_behavior_section(persona.get('online_behavior', {})))
                except Exception as e:
                    logger.error(f"Error in behavior section: {e}")
                    f.write("\nONLINE BEHAVIOR\n" + "-"*40 + "\nUnable to generate behavior section.\n\n")
                
                try:
                    f.write(self._generate_values_section(persona.get('values_beliefs', {})))
                except Exception as e:
                    logger.error(f"Error in values section: {e}")
                    f.write("\nVALUES & BELIEFS\n" + "-"*40 + "\nUnable to generate values section.\n\n")
                
                try:
                    f.write(self._generate_technical_section(persona.get('technical_proficiency', {})))
                except Exception as e:
                    logger.error(f"Error in technical section: {e}")
                    f.write("\nTECHNICAL PROFICIENCY\n" + "-"*40 + "\nUnable to generate technical section.\n\n")
                
                try:
                    f.write(self._generate_social_section(persona.get('social_engagement', {})))
                except Exception as e:
                    logger.error(f"Error in social section: {e}")
                    f.write("\nSOCIAL ENGAGEMENT\n" + "-"*40 + "\nUnable to generate social section.\n\n")
                
                # Write footer
                f.write(self._generate_footer())
            
            logger.info(f"Text persona file generated successfully: {filepath}")
            
            # Generate PDF file with error handling
            try:
                pdf_filepath = self.pdf_generator.generate_persona_pdf(username, user_summary, persona)
                return pdf_filepath  # Return PDF file path as primary output
            except Exception as e:
                logger.error(f"Error generating PDF: {e}")
                # Return text file path as fallback
                return filepath
            
        except Exception as e:
            logger.error(f"Error generating persona file: {e}")
            raise
    
    def _generate_header(self, username: str, user_summary: Dict[str, Any]) -> str:
        """
        Generate the header section of the persona file.
        
        Args:
            username (str): Reddit username
            user_summary (Dict[str, Any]): User activity summary
            
        Returns:
            str: Formatted header
        """
        header = f"""
{'='*80}
REDDIT USER PERSONA ANALYSIS
{'='*80}

Username: {username}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACCOUNT OVERVIEW:
• Account Age: {user_summary.get('account_age_days', 0)} days
• Total Posts: {user_summary.get('total_posts', 0)}
• Total Comments: {user_summary.get('total_comments', 0)}
• Total Karma: {user_summary.get('total_karma', 0)} (Comment: {user_summary.get('comment_karma', 0)}, Link: {user_summary.get('link_karma', 0)})
• Average Post Score: {user_summary.get('avg_post_score', 0)}
• Average Comment Score: {user_summary.get('avg_comment_score', 0)}
• Unique Subreddits: {user_summary.get('unique_subreddits', 0)}

Top Subreddits:
"""
        
        # Add top subreddits
        top_subreddits = user_summary.get('top_subreddits', [])
        for i, (subreddit, count) in enumerate(top_subreddits[:10], 1):
            header += f"  {i}. r/{subreddit} ({count} posts/comments)\n"
        
        header += f"\n{'='*80}\n\n"
        return header
    
    def _generate_demographics_section(self, demographics: Dict[str, Any]) -> str:
        """
        Generate demographics section.
        
        Args:
            demographics (Dict[str, Any]): Demographics data
            
        Returns:
            str: Formatted demographics section
        """
        section = f"""
DEMOGRAPHICS & BACKGROUND
{'-'*40}

Age Range: {demographics.get('age_range', 'Unable to determine')}
Likely Location: {demographics.get('likely_location', 'Unable to determine')}
Profession: {demographics.get('profession', 'Unable to determine')}

Evidence:
"""
        
        citations = demographics.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_interests_section(self, interests: Dict[str, Any]) -> str:
        """
        Generate interests section.
        
        Args:
            interests (Dict[str, Any]): Interests data
            
        Returns:
            str: Formatted interests section
        """
        section = f"""
INTERESTS & HOBBIES
{'-'*40}

Primary Interests:
"""
        
        primary_interests = interests.get('primary_interests', [])
        for i, interest in enumerate(primary_interests, 1):
            section += f"  {i}. {interest}\n"
        
        section += "\nSecondary Interests:\n"
        secondary_interests = interests.get('secondary_interests', [])
        for i, interest in enumerate(secondary_interests, 1):
            section += f"  {i}. {interest}\n"
        
        section += "\nEvidence:\n"
        citations = interests.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_communication_section(self, communication: Dict[str, Any]) -> str:
        """
        Generate communication style section.
        
        Args:
            communication (Dict[str, Any]): Communication data
            
        Returns:
            str: Formatted communication section
        """
        section = f"""
COMMUNICATION STYLE
{'-'*40}

Tone: {communication.get('tone', 'Unable to determine')}
Writing Style: {communication.get('writing_style', 'Unable to determine')}
Engagement Pattern: {communication.get('engagement_pattern', 'Unable to determine')}

Evidence:
"""
        
        citations = communication.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_personality_section(self, personality: Any) -> str:
        """
        Generate personality traits section.
        
        Args:
            personality (Any): Personality data (can be dict or list)
            
        Returns:
            str: Formatted personality section
        """
        section = f"""
PERSONALITY TRAITS
{'-'*40}

Traits:
"""
        
        # Handle both dict and list formats
        if isinstance(personality, dict):
            traits = personality.get('traits', [])
        elif isinstance(personality, list):
            traits = personality
        else:
            traits = [str(personality)] if personality else []
        
        for i, trait in enumerate(traits, 1):
            section += f"  {i}. {trait}\n"
        
        section += "\nEvidence:\n"
        if isinstance(personality, dict):
            citations = personality.get('detailed_citations', [])
            for i, citation in enumerate(citations, 1):
                section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
                if citation.get('citation'):
                    citation_data = citation['citation']
                    section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_behavior_section(self, behavior: Dict[str, Any]) -> str:
        """
        Generate online behavior section.
        
        Args:
            behavior (Dict[str, Any]): Behavior data
            
        Returns:
            str: Formatted behavior section
        """
        section = f"""
ONLINE BEHAVIOR
{'-'*40}

Reddit Usage: {behavior.get('reddit_usage', 'Unable to determine')}
Posting Frequency: {behavior.get('posting_frequency', 'Unable to determine')}
Engagement Style: {behavior.get('engagement_style', 'Unable to determine')}

Evidence:
"""
        
        citations = behavior.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_values_section(self, values: Dict[str, Any]) -> str:
        """
        Generate values and beliefs section.
        
        Args:
            values (Dict[str, Any]): Values data
            
        Returns:
            str: Formatted values section
        """
        section = f"""
VALUES & BELIEFS
{'-'*40}

Core Values:
"""
        
        core_values = values.get('core_values', [])
        for i, value in enumerate(core_values, 1):
            section += f"  {i}. {value}\n"
        
        section += "\nBeliefs:\n"
        beliefs = values.get('beliefs', [])
        for i, belief in enumerate(beliefs, 1):
            section += f"  {i}. {belief}\n"
        
        section += "\nEvidence:\n"
        citations = values.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_technical_section(self, technical: Dict[str, Any]) -> str:
        """
        Generate technical proficiency section.
        
        Args:
            technical (Dict[str, Any]): Technical data
            
        Returns:
            str: Formatted technical section
        """
        section = f"""
TECHNICAL PROFICIENCY
{'-'*40}

Level: {technical.get('level', 'Unable to determine')}

Areas:
"""
        
        areas = technical.get('areas', [])
        for i, area in enumerate(areas, 1):
            section += f"  {i}. {area}\n"
        
        section += "\nEvidence:\n"
        citations = technical.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_social_section(self, social: Dict[str, Any]) -> str:
        """
        Generate social engagement section.
        
        Args:
            social (Dict[str, Any]): Social data
            
        Returns:
            str: Formatted social section
        """
        section = f"""
SOCIAL ENGAGEMENT
{'-'*40}

Interaction Style: {social.get('interaction_style', 'Unable to determine')}
Community Participation: {social.get('community_participation', 'Unable to determine')}

Evidence:
"""
        
        citations = social.get('detailed_citations', [])
        for i, citation in enumerate(citations, 1):
            section += f"  {i}. {citation.get('text', 'No evidence provided')}\n"
            if citation.get('citation'):
                citation_data = citation['citation']
                section += f"     Citation: {format_citation(citation_data)}\n"
        
        section += "\n"
        return section
    
    def _generate_footer(self) -> str:
        """
        Generate the footer section.
        
        Returns:
            str: Formatted footer
        """
        footer = f"""
{'='*80}
ANALYSIS COMPLETE

This persona analysis was generated using AI-powered analysis of Reddit user activity.
The analysis includes citations from the user's actual posts and comments to support
each characteristic identified in the persona.

Note: This analysis is based on publicly available Reddit data and should be used
responsibly and in accordance with Reddit's terms of service.
{'='*80}
"""
        return footer 