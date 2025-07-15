"""
PDF Persona Generator

Creates beautiful single-page PDF persona documents with visual layout similar to user persona templates.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import requests
from io import BytesIO
from PIL import Image as PILImage
import random

logger = logging.getLogger(__name__)


class PDFPersonaGenerator:
    """
    Generates beautiful single-page PDF persona documents with visual layout.
    """
    
    def __init__(self, output_dir: str = "data/sample_outputs"):
        """Initialize PDF persona generator."""
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the persona document."""
        # Main title style
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=4,
            textColor=HexColor('#FF6B35'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=9,  # Slightly larger for section titles
            spaceAfter=2,
            textColor=HexColor('#FF6B35'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=7,  # Smaller for compact look
            spaceAfter=2,
            textColor=black,
            fontName='Helvetica'
        ))
        # Quote style
        self.styles.add(ParagraphStyle(
            name='Quote',
            parent=self.styles['Normal'],
            fontSize=7,  # Smaller for compact look
            spaceAfter=6,
            textColor=white,
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER
        ))
        # Detail text style
        self.styles.add(ParagraphStyle(
            name='DetailText',
            parent=self.styles['Normal'],
            fontSize=7,  # Smaller for compact look
            spaceAfter=2,
            textColor=black,
            fontName='Helvetica'
        ))
    
    def generate_persona_pdf(self, username: str, user_summary: Dict[str, Any], persona: Dict[str, Any]) -> str:
        from reportlab.platypus import Image
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.graphics import renderPDF
        import requests
        from io import BytesIO
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_persona_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), leftMargin=0.4*inch, rightMargin=0.4*inch, topMargin=0.4*inch, bottomMargin=0.4*inch)
            story = []

            # Name as large heading
            story.append(Paragraph(f"<font size=28 color='#FF6B35'><b>{username.upper()}</b></font>", self.styles['MainTitle']))
            story.append(Spacer(1, 8))

            col_gap = 24  # px, slightly reduced for more space
            col_width = (doc.width - 3*col_gap) / 4

            # --- COLUMN 1: Profile image + quote box ---
            col1 = []
            profile_img_url = user_summary.get('profile_img')
            if profile_img_url and profile_img_url != 'https://www.redditstatic.com/avatars/defaults/v2/avatar_default_0.png':
                try:
                    response = requests.get(profile_img_url, timeout=10)
                    if response.status_code == 200:
                        img_data = BytesIO(response.content)
                        profile_img = Image(img_data, width=col_width, height=col_width)
                        profile_img.hAlign = 'CENTER'
                        col1.append(profile_img)
                    else:
                        col1.append(self._profile_placeholder(col_width))
                except Exception:
                    col1.append(self._profile_placeholder(col_width))
            else:
                col1.append(self._profile_placeholder(col_width))
            col1.append(Spacer(1, 8))
            quote_text = persona.get('summary', '')
            quote_box = Table([[Paragraph(quote_text, self.styles['Quote'])]], colWidths=[col_width])
            quote_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FF6B35')),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#FF6B35')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            col1.append(quote_box)

            # --- COLUMN 2: User info (key-value) + traits table ---
            col2 = []
            account_age_years = user_summary.get('account_age_days', 0) // 365
            user_info_lines = [
                f"<b>AGE:</b> {account_age_years}",
                f"<b>OCCUPATION:</b> {persona.get('occupation', 'Reddit User')}",
                f"<b>LOCATION:</b> {persona.get('location', 'Unknown')}",
                f"<b>ACCOUNT AGE:</b> {user_summary.get('account_age_days', 0)} days",
                f"<b>TOTAL KARMA:</b> {user_summary.get('total_karma', 0):,}",
                f"<b>POSTS ANALYZED:</b> {user_summary.get('total_posts', 0)}",
                f"<b>COMMENTS ANALYZED:</b> {user_summary.get('total_comments', 0)}",
                f"<b>SUBREDDITS:</b> {user_summary.get('unique_subreddits', 0)}",
            ]
            for line in user_info_lines:
                col2.append(Paragraph(line, self.styles['DetailText']))
            col2.append(Spacer(1, 10))
            # Traits table (2x2 grid)
            traits = persona.get('personality_traits', [])
            if isinstance(traits, list):
                traits = traits[:4]
            else:
                traits = [str(traits)]
            trait_rows = []
            for i in range(0, len(traits), 2):
                row = []
                row.append(Paragraph(traits[i], self.styles['DetailText']))
                if i+1 < len(traits):
                    row.append(Paragraph(traits[i+1], self.styles['DetailText']))
                else:
                    row.append('')
                trait_rows.append(row)
            if trait_rows:
                traits_table = Table(trait_rows, colWidths=[col_width*0.5-5, col_width*0.5-5])
                traits_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F3F3F3')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#E0E0E0')),
                ]))
                col2.append(traits_table)

            # --- COLUMN 3: Motivations + Personality as tables (dynamic) ---
            col3 = []
            col3.append(Paragraph("MOTIVATIONS", self.styles['SectionTitle']))
            motivations = persona.get('motivations', [
                ["CONVENIENCE", "Medium"],
                ["WELLNESS", "Medium"],
                ["SPEED", "Medium"],
                ["PREFERENCES", "Medium"]
            ])
            if isinstance(motivations, dict):
                motivations = [[k.upper(), v] for k, v in motivations.items()]
            elif isinstance(motivations, list) and motivations and isinstance(motivations[0], str):
                motivations = [[m, "Medium"] for m in motivations]
            motivations_table = Table(motivations, colWidths=[col_width*0.6, col_width*0.4])
            motivations_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F3F3F3')),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#E0E0E0')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
            ]))
            col3.append(motivations_table)
            col3.append(Spacer(1, 10))
            col3.append(Paragraph("PERSONALITY", self.styles['SectionTitle']))
            personality_bars = persona.get('personality_bars', {})
            personality_pairs = [
                ("INTROVERT", "EXTROVERT", "introvert_extrovert"),
                ("INTUITION", "SENSING", "intuition_sensing"),
                ("FEELING", "THINKING", "feeling_thinking"),
                ("PERCEIVING", "JUDGING", "perceiving_judging")
            ]
            personality_rows = []
            for left, right, key in personality_pairs:
                value = personality_bars.get(key, 0.5)
                bar_width = col_width*0.4
                bar_height = 12
                bar = Drawing(bar_width, bar_height)
                bar.add(Rect(0, 2, bar_width, 8, fillColor=HexColor('#E0E0E0')))
                bar.add(Rect(value*(bar_width-20), 2, 20, 8, fillColor=HexColor('#FF6B35')))
                personality_rows.append([
                    Paragraph(f"<b>{left}</b>", self.styles['DetailText']),
                    bar,
                    Paragraph(f"<b>{right}</b>", self.styles['DetailText'])
                ])
            personality_table = Table(personality_rows, colWidths=[col_width*0.3, col_width*0.4, col_width*0.3])
            personality_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F3F3F3')),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#E0E0E0')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
            ]))
            col3.append(personality_table)

            # --- COLUMN 4: Behavior, Frustrations, Goals ---
            col4 = []
            col4.append(Paragraph("BEHAVIOUR & HABITS", self.styles['SectionTitle']))
            for item in persona.get('reddit_behavior', []):
                col4.append(Paragraph(f"• {item}", self.styles['InfoText']))
                col4.append(Spacer(1, 2))
            col4.append(Spacer(1, 8))
            col4.append(Paragraph("FRUSTRATIONS", self.styles['SectionTitle']))
            for item in persona.get('frustrations', []):
                col4.append(Paragraph(f"• {item}", self.styles['InfoText']))
                col4.append(Spacer(1, 2))
            col4.append(Spacer(1, 8))
            col4.append(Paragraph("GOALS & NEEDS", self.styles['SectionTitle']))
            for item in persona.get('goals', []):
                col4.append(Paragraph(f"• {item}", self.styles['InfoText']))
                col4.append(Spacer(1, 2))

            table_data = [[col1, '', col2, '', col3, '', col4]]
            col_widths = [col_width, col_gap, col_width, col_gap, col_width, col_gap, col_width]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(table)
            doc.build(story)
            logger.info(f"PDF persona file generated successfully: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating PDF persona: {e}")
            raise
    
    def _create_column_1(self, user_summary: Dict[str, Any], persona: Dict[str, Any]) -> List:
        """Create first column: Profile image and quote box."""
        content = []
        
        # Profile image - try to use actual Reddit profile image
        profile_img_url = user_summary.get('profile_img')
        if profile_img_url and profile_img_url != 'https://www.redditstatic.com/avatars/defaults/v2/avatar_default_0.png':
            # Use actual profile image
            try:
                from reportlab.platypus import Image
                import requests
                from io import BytesIO
                
                # Download image
                response = requests.get(profile_img_url, timeout=10)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    profile_img = Image(img_data, width=2*inch, height=2*inch)
                    profile_img.hAlign = 'LEFT'
                    content.append(profile_img)
                else:
                    # Fallback to grey box
                    profile_box = Table([['']], colWidths=[2*inch], rowHeights=[2*inch])
                    profile_box.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#CCCCCC')),
                        ('GRID', (0, 0), (-1, -1), 1, black),
                    ]))
                    content.append(profile_box)
            except Exception as e:
                # Fallback to grey box
                profile_box = Table([['']], colWidths=[2*inch], rowHeights=[2*inch])
                profile_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#CCCCCC')),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                ]))
                content.append(profile_box)
        else:
            # Use grey placeholder box
            profile_box = Table([['']], colWidths=[2*inch], rowHeights=[2*inch])
            profile_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#CCCCCC')),
                ('GRID', (0, 0), (-1, -1), 1, black),
            ]))
            content.append(profile_box)
        
        content.append(Spacer(1, 6))
        
        # Quote box (orange background) - same width as profile image
        quote_text = persona.get('summary', 'An active Reddit user who engages regularly with the community.')
        quote_box = Table([[Paragraph(quote_text, self.styles['Quote'])]], colWidths=[2*inch])
        quote_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FF6B35')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#FF6B35')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(quote_box)
        
        return content
    
    def _create_column_2(self, user_summary: Dict[str, Any], persona: Dict[str, Any]) -> List:
        """Create second column: Personal details and personality traits."""
        content = []
        
        # Personal details with name above age
        account_age_years = user_summary.get('account_age_days', 0) // 365
        
        content.append(Paragraph(f"<b>AGE:</b> {account_age_years}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>OCCUPATION:</b> {persona.get('occupation', 'Reddit User')}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>LOCATION:</b> {persona.get('location', 'Unknown')}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>ACCOUNT AGE:</b> {user_summary.get('account_age_days', 0)} days", self.styles['DetailText']))
        content.append(Paragraph(f"<b>TOTAL KARMA:</b> {user_summary.get('total_karma', 0):,}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>POSTS ANALYZED:</b> {user_summary.get('total_posts', 0)}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>COMMENTS ANALYZED:</b> {user_summary.get('total_comments', 0)}", self.styles['DetailText']))
        content.append(Paragraph(f"<b>SUBREDDITS:</b> {user_summary.get('unique_subreddits', 0)}", self.styles['DetailText']))
        
        content.append(Spacer(1, 10))
        
        # Personality traits as boxes (2x2 grid)
        if 'personality_traits' in persona:
            traits = persona['personality_traits']
            if isinstance(traits, list):
                traits = traits[:4]  # Limit to 4 traits
            else:
                traits = [str(traits)]
            
            # Create 2x2 grid of trait boxes
            trait_boxes = []
            for i in range(0, min(len(traits), 4), 2):
                row = []
                row.append(Paragraph(traits[i], self.styles['DetailText']))
                if i + 1 < len(traits):
                    row.append(Paragraph(traits[i + 1], self.styles['DetailText']))
                else:
                    row.append('')
                trait_boxes.append(row)
            
            if trait_boxes:
                traits_table = Table(trait_boxes, colWidths=[0.9*inch, 0.9*inch])
                traits_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#E0E0E0')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                ]))
                content.append(traits_table)
        
        return content
    
    def _create_column_3(self, persona: Dict[str, Any]) -> List:
        """Create third column: Motivations and personality sliders."""
        content = []
        
        # Motivations section
        content.append(Paragraph("MOTIVATIONS", self.styles['SectionTitle']))
        
        motivations = []
        if 'motivations' in persona:
            motivation = persona['motivations']
            if isinstance(motivation, list):
                for item in motivation[:4]:  # Limit to 4 items
                    motivations.append([item, "■■■■■"])
            else:
                motivations.append([str(motivation), "■■■■■"])
        
        if not motivations:
            motivations = [
                ['CONVENIENCE', 'High'],
                ['WELLNESS', 'High'],
                ['SPEED', 'Medium'],
                ['PREFERENCES', 'Medium']
            ]
        
        motivations_table = Table(motivations, colWidths=[1.3*inch, 0.6*inch])
        motivations_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        content.append(motivations_table)
        content.append(Spacer(1, 10))
        
        # Personality section with sliders
        content.append(Paragraph("PERSONALITY", self.styles['SectionTitle']))
        
        personality_data = [
            ['INTROVERT', 'EXTROVERT'],
            ['INTUITION', 'SENSING'],
            ['FEELING', 'THINKING'],
            ['PERCEIVING', 'JUDGING']
        ]
        
        personality_table = Table(personality_data, colWidths=[0.9*inch, 0.9*inch])
        personality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        content.append(personality_table)
        
        return content
    
    def _create_column_4(self, persona: Dict[str, Any]) -> List:
        """Create fourth column: Behavior, frustrations, and goals."""
        content = []
        
        # Behaviour & Habits section
        content.append(Paragraph("BEHAVIOUR & HABITS", self.styles['SectionTitle']))
        
        behaviors = []
        if 'reddit_behavior' in persona:
            behavior = persona['reddit_behavior']
            if isinstance(behavior, list):
                for item in behavior[:4]:  # Limit to 4 items
                    behaviors.append(f"• {item}")
            else:
                behaviors.append(f"• {behavior}")
        
        if behaviors:
            for behavior in behaviors:
                content.append(Paragraph(behavior, self.styles['InfoText']))
        else:
            content.append(Paragraph("• Regular Reddit user", self.styles['InfoText']))
            content.append(Paragraph("• Engages with community", self.styles['InfoText']))
            content.append(Paragraph("• Shares content regularly", self.styles['InfoText']))
        
        content.append(Spacer(1, 10))
        
        # Frustrations section
        content.append(Paragraph("FRUSTRATIONS", self.styles['SectionTitle']))
        
        frustrations = []
        if 'frustrations' in persona:
            frustration = persona['frustrations']
            if isinstance(frustration, list):
                for item in frustration[:3]:  # Limit to 3 items
                    frustrations.append(f"• {item}")
            else:
                frustrations.append(f"• {frustration}")
        
        if frustrations:
            for frustration in frustrations:
                content.append(Paragraph(frustration, self.styles['InfoText']))
        else:
            content.append(Paragraph("• Limited engagement", self.styles['InfoText']))
            content.append(Paragraph("• Content visibility issues", self.styles['InfoText']))
            content.append(Paragraph("• Community dynamics", self.styles['InfoText']))
        
        content.append(Spacer(1, 10))
        
        # Goals & Needs section
        content.append(Paragraph("GOALS & NEEDS", self.styles['SectionTitle']))
        
        goals = []
        if 'goals' in persona:
            goal = persona['goals']
            if isinstance(goal, list):
                for item in goal[:3]:  # Limit to 3 items
                    goals.append(f"• {item}")
            else:
                goals.append(f"• {goal}")
        
        if goals:
            for goal in goals:
                content.append(Paragraph(goal, self.styles['InfoText']))
        else:
            content.append(Paragraph("• Connect with others", self.styles['InfoText']))
            content.append(Paragraph("• Share information", self.styles['InfoText']))
            content.append(Paragraph("• Participate in discussions", self.styles['InfoText']))
        
        return content 