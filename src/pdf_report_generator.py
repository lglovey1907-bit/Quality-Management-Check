"""
Institutional-Grade PDF Report Generator
Generates professional quality management analysis reports in PDF format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
import os
from typing import List, Dict
from .analyzer import QualityReport, RedFlag, QualityScore


class InstitutionalReportGenerator:
    """
    Generates institutional-grade PDF reports for quality management analysis
    Professional formatting with comprehensive sections
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for professional formatting"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f4f8')
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text with justification
        self.styles.add(ParagraphStyle(
            name='JustifiedBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            backColor=colors.HexColor('#fff9e6'),
            borderWidth=1,
            borderColor=colors.HexColor('#ffcc00'),
            borderPadding=10,
            leading=16
        ))
        
    def _create_cover_page(self, report: QualityReport):
        """Create professional cover page"""
        story = []
        
        # Spacer
        story.append(Spacer(1, 2*inch))
        
        # Main title
        title = Paragraph(
            "INSTITUTIONAL QUALITY ASSESSMENT REPORT",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Company name
        company_style = ParagraphStyle(
            'CompanyName',
            parent=self.styles['CustomTitle'],
            fontSize=28,
            textColor=colors.HexColor('#c0392b')
        )
        company = Paragraph(f"<b>{report.company_name}</b>", company_style)
        story.append(company)
        story.append(Spacer(1, 0.2*inch))
        
        # Ticker
        ticker_text = Paragraph(
            f"Ticker: <b>{report.ticker}</b>",
            ParagraphStyle('Ticker', fontSize=14, alignment=TA_CENTER)
        )
        story.append(ticker_text)
        story.append(Spacer(1, 1*inch))
        
        # Overall score with visual
        score_img = self._create_score_gauge(report.overall_score)
        if score_img:
            story.append(Image(score_img, width=4*inch, height=2*inch))
            story.append(Spacer(1, 0.3*inch))
        
        # Rating
        rating = self._get_rating_text(report.overall_score)
        rating_para = Paragraph(
            f"<b>Overall Rating: {rating}</b>",
            ParagraphStyle('Rating', fontSize=18, alignment=TA_CENTER,
                         textColor=self._get_score_color(report.overall_score))
        )
        story.append(rating_para)
        story.append(Spacer(1, 1*inch))
        
        # Report metadata
        metadata_data = [
            ['Analysis Date:', report.analysis_date],
            ['Period Analyzed:', f'{report.years_analyzed} years'],
            ['Report Type:', 'Institutional Quality Assessment'],
            ['Methodology:', 'Multi-Factor Quantitative & Qualitative Analysis']
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2.5*inch, 3.5*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(metadata_table)
        
        story.append(PageBreak())
        return story
    
    def _create_score_gauge(self, score: float):
        """Create visual score gauge"""
        try:
            fig, ax = plt.subplots(figsize=(6, 3))
            
            # Create horizontal bar
            colors_list = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#2ecc71']
            positions = [0, 2.5, 5, 7.5, 10]
            
            for i in range(len(colors_list)):
                start = positions[i]
                end = positions[i+1] if i < len(positions)-1 else 10
                ax.barh(0, end-start, left=start, height=0.5,
                       color=colors_list[i], alpha=0.7)
            
            # Add score marker
            ax.plot(score, 0, 'v', color='black', markersize=20, zorder=10)
            ax.text(score, -0.15, f'{score:.1f}', ha='center', va='top',
                   fontsize=16, fontweight='bold')
            
            ax.set_xlim(0, 10)
            ax.set_ylim(-0.5, 0.5)
            ax.axis('off')
            
            # Convert to image
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            return buf
        except Exception as e:
            print(f"Error creating score gauge: {e}")
            return None
    
    def _create_radar_chart(self, report: QualityReport):
        """Create radar chart for category scores"""
        try:
            # Get category data
            categories = [cs.category for cs in report.category_scores]
            scores = [cs.score for cs in report.category_scores]
            
            # Number of variables
            num_vars = len(categories)
            
            # Compute angle for each axis
            angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
            scores += scores[:1]  # Complete the circle
            angles += angles[:1]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Draw the chart
            ax.plot(angles, scores, 'o-', linewidth=2, color='#667eea', label='Quality Scores')
            ax.fill(angles, scores, alpha=0.25, color='#667eea')
            
            # Set category labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, size=10, weight='bold')
            
            # Set y-axis
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], size=9)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add title
            plt.title('Category Performance Radar', size=14, weight='bold', pad=20)
            
            # Convert to image
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        except Exception as e:
            print(f"Error creating radar chart: {e}")
            return None
    
    def _create_horizontal_bar_chart(self, report: QualityReport):
        """Create horizontal bar chart for category scores"""
        try:
            # Get category data
            categories = [cs.category for cs in report.category_scores]
            scores = [cs.score for cs in report.category_scores]
            
            # Determine colors based on scores
            colors_list = []
            for score in scores:
                if score >= 7.5:
                    colors_list.append('#10b981')
                elif score >= 6.5:
                    colors_list.append('#3b82f6')
                elif score >= 5.5:
                    colors_list.append('#8b5cf6')
                elif score >= 4.0:
                    colors_list.append('#f59e0b')
                else:
                    colors_list.append('#ef4444')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create bars
            y_pos = range(len(categories))
            bars = ax.barh(y_pos, scores, color=colors_list, edgecolor='white', linewidth=2)
            
            # Add score labels
            for i, (bar, score) in enumerate(zip(bars, scores)):
                ax.text(score + 0.2, i, f'{score:.1f}', va='center', fontsize=11, weight='bold')
            
            # Customize axes
            ax.set_yticks(y_pos)
            ax.set_yticklabels(categories, fontsize=10)
            ax.set_xlabel('Score', fontsize=11, weight='bold')
            ax.set_xlim(0, 10.5)
            ax.set_title('Category Scores Comparison', fontsize=14, weight='bold', pad=15)
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Convert to image
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return None
    
    def _create_gauge_chart(self, score: float):
        """Create enhanced gauge chart for overall score"""
        try:
            fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={'projection': 'polar'})
            
            # Define gauge segments
            theta = [0, 3.14159 * 0.4, 3.14159 * 0.55, 3.14159 * 0.65, 
                    3.14159 * 0.75, 3.14159]
            
            colors_list = ['#ef4444', '#f59e0b', '#8b5cf6', '#3b82f6', '#10b981']
            
            # Draw gauge segments
            for i in range(len(colors_list)):
                ax.barh(1, theta[i+1] - theta[i], left=theta[i], height=0.3,
                       color=colors_list[i], alpha=0.8, edgecolor='white', linewidth=2)
            
            # Calculate needle angle
            needle_angle = (score / 10.0) * 3.14159
            
            # Draw needle
            ax.plot([needle_angle, needle_angle], [0, 1.3], color='black', linewidth=3)
            ax.plot(needle_angle, 1.3, 'o', color='black', markersize=10)
            
            # Add score text in center
            ax.text(3.14159/2, 0.5, f'{score:.1f}', ha='center', va='center',
                   fontsize=32, weight='bold', color='#1e293b')
            ax.text(3.14159/2, 0.2, 'Overall Score', ha='center', va='center',
                   fontsize=12, color='#64748b')
            
            # Customize
            ax.set_ylim(0, 1.5)
            ax.set_xlim(0, 3.14159)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['polar'].set_visible(False)
            ax.grid(False)
            
            # Convert to image
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        except Exception as e:
            print(f"Error creating gauge chart: {e}")
            return None
    
    def _create_red_flags_pie_chart(self, report: QualityReport):
        """Create pie chart for red flags distribution by category"""
        try:
            if not report.red_flags:
                return None
            
            # Count flags by category
            category_counts = {}
            for flag in report.red_flags:
                cat = flag.category if hasattr(flag, 'category') else 'Other'
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 8))
            
            colors_list = ['#ef4444', '#f59e0b', '#eab308', '#84cc16', 
                          '#22c55e', '#14b8a6', '#06b6d4']
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                category_counts.values(),
                labels=category_counts.keys(),
                autopct='%1.1f%%',
                colors=colors_list[:len(category_counts)],
                startangle=90,
                wedgeprops=dict(edgecolor='white', linewidth=2),
                textprops=dict(fontsize=10, weight='bold')
            )
            
            # Add white circle in center for donut effect
            centre_circle = plt.Circle((0, 0), 0.70, fc='white', linewidth=2, edgecolor='white')
            ax.add_artist(centre_circle)
            
            # Add total count in center
            total = sum(category_counts.values())
            ax.text(0, 0, f'{total}\nRed Flags', ha='center', va='center',
                   fontsize=20, weight='bold', color='#1e293b')
            
            ax.set_title('Red Flags Distribution by Category', fontsize=14, weight='bold', pad=20)
            
            # Convert to image
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return None
    
    def _get_rating_text(self, score: float) -> str:
        """Get rating text based on score"""
        if score >= 8.0:
            return "EXCEPTIONAL"
        elif score >= 7.0:
            return "EXCELLENT"
        elif score >= 6.0:
            return "STRONG"
        elif score >= 5.0:
            return "ABOVE AVERAGE"
        elif score >= 4.0:
            return "MODERATE"
        else:
            return "BELOW AVERAGE"
    
    def _get_score_color(self, score: float):
        """Get color based on score"""
        if score >= 7.5:
            return colors.HexColor('#27ae60')
        elif score >= 6.0:
            return colors.HexColor('#2ecc71')
        elif score >= 5.0:
            return colors.HexColor('#f39c12')
        elif score >= 4.0:
            return colors.HexColor('#e67e22')
        else:
            return colors.HexColor('#e74c3c')
    
    def _create_executive_summary(self, report: QualityReport):
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        if report.executive_summary:
            summary_text = Paragraph(report.executive_summary, self.styles['ExecutiveSummary'])
            story.append(summary_text)
        else:
            # Generate summary from available data
            summary = f"""
            This institutional assessment evaluates {report.company_name} ({report.ticker}) 
            across seven critical quality dimensions over a {report.years_analyzed}-year period. 
            The analysis incorporates quantitative metrics, qualitative factors, and comparative 
            industry benchmarking to provide a comprehensive quality rating of 
            <b>{report.overall_score:.1f}/10.0</b>.
            """
            story.append(Paragraph(summary, self.styles['ExecutiveSummary']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _create_quantitative_scoring(self, report: QualityReport):
        """Create quantitative scoring section with category breakdown"""
        story = []
        
        story.append(Paragraph("QUANTITATIVE SCORING ANALYSIS", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Create category scores table
        table_data = [['Category', 'Score', 'Weight', 'Weighted Score', 'Assessment']]
        
        for cat_score in report.category_scores:
            weighted = cat_score.score * cat_score.weight
            assessment = self._get_category_assessment(cat_score.score)
            
            table_data.append([
                cat_score.category,
                f"{cat_score.score:.1f}/10",
                f"{cat_score.weight*100:.0f}%",
                f"{weighted:.2f}",
                assessment
            ])
        
        # Add overall score row
        table_data.append([
            'OVERALL QUALITY SCORE',
            f"{report.overall_score:.1f}/10",
            '100%',
            f"{report.overall_score:.2f}",
            self._get_rating_text(report.overall_score)
        ])
        
        # Create table
        score_table = Table(table_data, colWidths=[2.2*inch, 0.9*inch, 0.8*inch, 
                                                    1.1*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Overall row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add scoring methodology note
        methodology = """
        <b>Scoring Methodology:</b> Each category is evaluated on a 0-10 scale using 
        quantitative metrics and qualitative assessments. Weighted scores reflect the 
        relative importance of each dimension in overall quality evaluation. Scores above 
        7.0 indicate strong quality, 5.0-7.0 indicate moderate quality, and below 5.0 
        indicate areas requiring attention.
        """
        story.append(Paragraph(methodology, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _get_category_assessment(self, score: float) -> str:
        """Get assessment text for category score"""
        if score >= 8.0:
            return "Excellent"
        elif score >= 7.0:
            return "Strong"
        elif score >= 6.0:
            return "Above Avg"
        elif score >= 5.0:
            return "Average"
        elif score >= 4.0:
            return "Below Avg"
        else:
            return "Weak"
    
    def _create_visual_analytics(self, report: QualityReport):
        """Create visual analytics section with charts"""
        story = []
        
        story.append(Paragraph("VISUAL ANALYTICS", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        intro_text = """
        The following visualizations provide a comprehensive overview of the quality assessment 
        across all dimensions. These charts enable quick identification of strengths, weaknesses, 
        and areas requiring attention.
        """
        story.append(Paragraph(intro_text, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Radar Chart
        radar_buf = self._create_radar_chart(report)
        if radar_buf:
            story.append(Paragraph("Category Performance Radar", self.styles['SubHeading']))
            radar_img = Image(radar_buf, width=5*inch, height=5*inch)
            story.append(radar_img)
            story.append(Spacer(1, 0.2*inch))
        
        # Horizontal Bar Chart
        bar_buf = self._create_horizontal_bar_chart(report)
        if bar_buf:
            story.append(Paragraph("Category Scores Comparison", self.styles['SubHeading']))
            bar_img = Image(bar_buf, width=6.5*inch, height=4*inch)
            story.append(bar_img)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Gauge Chart
        gauge_buf = self._create_gauge_chart(report.overall_score)
        if gauge_buf:
            story.append(Paragraph("Overall Quality Score Gauge", self.styles['SubHeading']))
            gauge_img = Image(gauge_buf, width=5.5*inch, height=3.5*inch)
            story.append(gauge_img)
            story.append(Spacer(1, 0.2*inch))
        
        # Red Flags Distribution (only if red flags exist)
        if report.red_flags:
            pie_buf = self._create_red_flags_pie_chart(report)
            if pie_buf:
                story.append(Paragraph("Red Flags Distribution by Category", self.styles['SubHeading']))
                pie_img = Image(pie_buf, width=5*inch, height=5*inch)
                story.append(pie_img)
                story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_strategic_alignment(self, report: QualityReport):
        """Create strategic alignment section"""
        story = []
        
        story.append(Paragraph("STRATEGIC ALIGNMENT & EXECUTION", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Key strengths
        if report.key_strengths:
            story.append(Paragraph("Strategic Strengths:", self.styles['SubHeading']))
            
            for strength in report.key_strengths[:5]:  # Top 5
                bullet_text = f"• {strength}"
                story.append(Paragraph(bullet_text, self.styles['JustifiedBody']))
            
            story.append(Spacer(1, 0.1*inch))
        
        # Extract governance and growth scores for strategic context
        governance_score = 0.0
        growth_score = 0.0
        
        for cat_score in report.category_scores:
            if 'Governance' in cat_score.category:
                governance_score = cat_score.score
            elif 'Growth' in cat_score.category:
                growth_score = cat_score.score
        
        strategic_text = f"""
        The company demonstrates {'strong' if governance_score >= 6.0 else 'moderate'} 
        strategic governance (score: {governance_score:.1f}/10) and 
        {'robust' if growth_score >= 6.0 else 'moderate'} growth execution 
        (score: {growth_score:.1f}/10). This indicates 
        {'effective' if (governance_score + growth_score) >= 12 else 'developing'} 
        alignment between strategic objectives and operational delivery.
        """
        
        story.append(Paragraph(strategic_text, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_capital_allocation(self, report: QualityReport):
        """Create capital allocation discipline section"""
        story = []
        
        story.append(Paragraph("CAPITAL ALLOCATION DISCIPLINE", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Extract relevant scores
        efficiency_score = 0.0
        cash_score = 0.0
        
        for cat_score in report.category_scores:
            if 'Capital Efficiency' in cat_score.category or 'Efficiency' in cat_score.category:
                efficiency_score = cat_score.score
            elif 'Cash' in cat_score.category:
                cash_score = cat_score.score
        
        capital_text = f"""
        <b>Capital Efficiency Rating:</b> {efficiency_score:.1f}/10<br/>
        <b>Cash Management Rating:</b> {cash_score:.1f}/10<br/><br/>
        
        The company's capital allocation demonstrates 
        {'disciplined' if efficiency_score >= 6.5 else 'moderate'} efficiency in 
        deploying resources. Cash flow management is rated as 
        {'strong' if cash_score >= 6.5 else 'adequate' if cash_score >= 5.0 else 'concerning'}, 
        indicating {'effective' if cash_score >= 6.5 else 'developing'} liquidity 
        management and operational cash generation capabilities.
        """
        
        story.append(Paragraph(capital_text, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add metrics if available
        if report.metrics_summary:
            metrics_text = "<b>Key Capital Metrics:</b><br/>"
            
            key_metrics = ['ROE', 'ROIC', 'Asset Turnover', 'Free Cash Flow', 
                          'Operating Cash Flow']
            
            for metric in key_metrics:
                if metric in report.metrics_summary:
                    value = report.metrics_summary[metric]
                    metrics_text += f"• {metric}: {value}<br/>"
            
            if '•' in metrics_text:
                story.append(Paragraph(metrics_text, self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_governance_quality(self, report: QualityReport):
        """Create governance quality section"""
        story = []
        
        story.append(Paragraph("GOVERNANCE QUALITY ASSESSMENT", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Extract governance score
        governance_score = 0.0
        governance_strengths = []
        governance_concerns = []
        
        for cat_score in report.category_scores:
            if 'Governance' in cat_score.category:
                governance_score = cat_score.score
                governance_strengths = cat_score.strengths
                governance_concerns = cat_score.concerns
                break
        
        governance_rating = self._get_rating_text(governance_score)
        
        intro_text = f"""
        <b>Governance Rating: {governance_score:.1f}/10 ({governance_rating})</b><br/><br/>
        
        Corporate governance practices are assessed across multiple dimensions including 
        transparency, shareholder rights, board effectiveness, and regulatory compliance.
        """
        
        story.append(Paragraph(intro_text, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.15*inch))
        
        # Strengths
        if governance_strengths:
            story.append(Paragraph("Governance Strengths:", self.styles['SubHeading']))
            for strength in governance_strengths[:3]:
                story.append(Paragraph(f"✓ {strength}", self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
        
        # Concerns
        if governance_concerns:
            story.append(Paragraph("Areas for Improvement:", self.styles['SubHeading']))
            for concern in governance_concerns[:3]:
                story.append(Paragraph(f"⚠ {concern}", self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_execution_narrative_gap(self, report: QualityReport):
        """Create execution vs narrative gap analysis"""
        story = []
        
        story.append(Paragraph("EXECUTION VS NARRATIVE GAP ANALYSIS", 
                             self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Compare earnings quality vs profitability
        earnings_quality = 0.0
        profitability = 0.0
        
        for cat_score in report.category_scores:
            if 'Earnings Quality' in cat_score.category or 'Quality' in cat_score.category:
                earnings_quality = cat_score.score
            elif 'Profitability' in cat_score.category:
                profitability = cat_score.score
        
        gap = abs(profitability - earnings_quality)
        gap_assessment = "minimal" if gap < 1.0 else "moderate" if gap < 2.0 else "significant"
        
        gap_text = f"""
        <b>Profitability Score:</b> {profitability:.1f}/10<br/>
        <b>Earnings Quality Score:</b> {earnings_quality:.1f}/10<br/>
        <b>Gap Assessment:</b> {gap_assessment.upper()} (Δ {gap:.1f})<br/><br/>
        
        {'The company demonstrates strong alignment between reported profitability and earnings quality, suggesting reliable financial reporting and sustainable profit generation.' if gap < 1.0 else 
         'A moderate gap exists between profitability metrics and earnings quality, warranting closer examination of accounting practices and profit sustainability.' if gap < 2.0 else
         'A significant gap between profitability and earnings quality raises concerns about the sustainability and reliability of reported earnings.'}
        """
        
        story.append(Paragraph(gap_text, self.styles['JustifiedBody']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_red_flags_section(self, report: QualityReport):
        """Create comprehensive red flags section"""
        story = []
        
        story.append(Paragraph("RED FLAGS & RISK INDICATORS", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        if not report.red_flags:
            no_flags = """
            <b>Status: CLEAR</b><br/><br/>
            No significant red flags identified in the analysis. The company demonstrates 
            sound financial practices and quality metrics across all evaluated dimensions.
            """
            story.append(Paragraph(no_flags, self.styles['JustifiedBody']))
        else:
            # Summary
            high_severity = sum(1 for rf in report.red_flags if rf.severity == "High")
            medium_severity = sum(1 for rf in report.red_flags if rf.severity == "Medium")
            low_severity = sum(1 for rf in report.red_flags if rf.severity == "Low")
            
            summary = f"""
            <b>Total Red Flags Identified:</b> {len(report.red_flags)}<br/>
            • High Severity: {high_severity}<br/>
            • Medium Severity: {medium_severity}<br/>
            • Low Severity: {low_severity}<br/><br/>
            """
            
            story.append(Paragraph(summary, self.styles['BodyText']))
            story.append(Spacer(1, 0.15*inch))
            
            # Detailed red flags
            for i, red_flag in enumerate(report.red_flags, 1):
                # Color code by severity
                if red_flag.severity == "High":
                    severity_color = colors.HexColor('#e74c3c')
                elif red_flag.severity == "Medium":
                    severity_color = colors.HexColor('#f39c12')
                else:
                    severity_color = colors.HexColor('#95a5a6')
                
                flag_data = [
                    [f"Red Flag #{i}", f"{red_flag.severity} Severity"],
                    ["Category:", red_flag.category],
                    ["Issue:", red_flag.description],
                    ["Impact:", red_flag.impact],
                    ["Recommendation:", red_flag.recommendation]
                ]
                
                flag_table = Table(flag_data, colWidths=[1.5*inch, 5*inch])
                flag_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), severity_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 1), (0, -1), 9),
                    ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (1, 1), (1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(flag_table)
                story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_final_rating(self, report: QualityReport):
        """Create final rating and recommendation"""
        story = []
        
        story.append(Paragraph("FINAL RATING & INVESTMENT PERSPECTIVE", 
                             self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Rating summary
        rating = self._get_rating_text(report.overall_score)
        
        # Determine investment perspective
        if report.overall_score >= 7.5:
            perspective = "STRONG BUY"
            outlook = "Exceptional quality metrics across all dimensions"
        elif report.overall_score >= 6.5:
            perspective = "BUY"
            outlook = "Strong fundamentals with favorable quality indicators"
        elif report.overall_score >= 5.5:
            perspective = "ACCUMULATE"
            outlook = "Above-average quality with selective strengths"
        elif report.overall_score >= 4.5:
            perspective = "HOLD"
            outlook = "Mixed quality signals requiring monitoring"
        else:
            perspective = "CAUTIOUS"
            outlook = "Quality concerns warrant careful evaluation"
        
        rating_summary = f"""
        <b>OVERALL QUALITY RATING: {report.overall_score:.1f}/10.0 ({rating})</b><br/>
        <b>Investment Perspective: {perspective}</b><br/><br/>
        
        {outlook}. {report.investment_thesis if report.investment_thesis else 
        f'Based on comprehensive analysis of {report.years_analyzed} years of data, ' +
        f'{report.company_name} demonstrates {rating.lower()} quality characteristics.'}<br/><br/>
        
        <b>Risk Assessment:</b> {report.risk_assessment if report.risk_assessment else
        f'{"Low to moderate" if report.overall_score >= 6.5 else "Moderate to elevated" if report.overall_score >= 5.0 else "Elevated"} ' +
        f'risk profile based on identified quality metrics and red flag analysis.'}
        """
        
        story.append(Paragraph(rating_summary, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        disclaimer = """
        <b>Important Disclaimer:</b> This report is for informational purposes only and 
        does not constitute investment advice. Past performance does not guarantee future 
        results. Investors should conduct their own due diligence and consult with 
        qualified financial advisors before making investment decisions. Quality ratings 
        are based on historical data and analytical models and may not reflect future 
        company performance.
        """
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_JUSTIFY,
            borderWidth=0.5,
            borderColor=colors.grey,
            borderPadding=5,
            backColor=colors.HexColor('#ecf0f1')
        )
        
        story.append(Paragraph(disclaimer, disclaimer_style))
        
        return story
    
    def generate_report(self, report: QualityReport, output_path: str) -> str:
        """
        Generate complete institutional PDF report
        
        Args:
            report: QualityReport object with analysis results
            output_path: Path to save PDF file
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Build story
            story = []
            
            # Cover page
            story.extend(self._create_cover_page(report))
            
            # Executive summary
            story.extend(self._create_executive_summary(report))
            
            # Quantitative scoring (includes category breakdown)
            story.extend(self._create_quantitative_scoring(report))
            story.append(PageBreak())
            
            # Visual Analytics Section (New)
            story.extend(self._create_visual_analytics(report))
            story.append(PageBreak())
            
            # Strategic alignment
            story.extend(self._create_strategic_alignment(report))
            
            # Capital allocation
            story.extend(self._create_capital_allocation(report))
            story.append(PageBreak())
            
            # Governance quality
            story.extend(self._create_governance_quality(report))
            
            # Execution vs narrative gap
            story.extend(self._create_execution_narrative_gap(report))
            story.append(PageBreak())
            
            # Red flags
            story.extend(self._create_red_flags_section(report))
            story.append(PageBreak())
            
            # Final rating
            story.extend(self._create_final_rating(report))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, 
                     onLaterPages=self._add_page_number)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error generating PDF report: {str(e)}")
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page numbers to each page"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(7.5*inch, 0.5*inch, text)
        canvas_obj.restoreState()


def generate_institutional_pdf(report: QualityReport, output_path: str = None) -> str:
    """
    Convenience function to generate institutional PDF report
    
    Args:
        report: QualityReport object
        output_path: Optional custom output path
        
    Returns:
        Path to generated PDF
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"Quality_Report_{report.ticker}_{timestamp}.pdf"
    
    generator = InstitutionalReportGenerator()
    return generator.generate_report(report, output_path)
