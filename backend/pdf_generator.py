"""PDF report generator using ReportLab."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import json
import os

def generate_evaluation_report(evaluation_data, output_path):
    """
    Generate a PDF report for an evaluation.
    
    Args:
        evaluation_data: Dictionary containing evaluation details
        output_path: Path where PDF will be saved
        
    Returns:
        Path to generated PDF
    """
    try:
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#58a6ff'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#58a6ff'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = styles['Normal']
        
        # Title
        story.append(Paragraph("ExamEval AI - Evaluation Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Student Information
        story.append(Paragraph("Student Information", heading_style))
        
        student_info = [
            ['Student Name:', evaluation_data.get('username', 'N/A')],
            ['Email:', evaluation_data.get('email', 'N/A')],
            ['Subject:', evaluation_data.get('subject', 'N/A')],
            ['Exam Type:', evaluation_data.get('exam_type', 'N/A')],
            ['Date:', evaluation_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        ]
        
        student_table = Table(student_info, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(student_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Score
        story.append(Paragraph("Overall Score", heading_style))
        
        percentage = evaluation_data.get('percentage', 0)
        obtained_marks = evaluation_data.get('obtained_marks', 0)
        total_marks = evaluation_data.get('total_marks', 0)
        
        score_info = [
            ['Obtained Marks:', f"{obtained_marks} / {total_marks}"],
            ['Percentage:', f"{percentage}%"],
            ['Status:', 'Pass' if percentage >= 40 else 'Fail']
        ]
        
        score_table = Table(score_info, colWidths=[2*inch, 4*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Question-wise Breakdown
        story.append(Paragraph("Question-wise Breakdown", heading_style))
        
        questions = evaluation_data.get('questions', [])
        
        for q in questions:
            # Question header
            q_text = f"Question {q.get('question_number', '')}: {q.get('question_text', '')[:100]}"
            story.append(Paragraph(q_text, ParagraphStyle('QuestionText', parent=normal_style, fontSize=11, textColor=colors.HexColor('#0d1117'), spaceBefore=10)))
            
            # Score
            q_score = f"Score: {q.get('obtained_marks', 0)} / {q.get('max_marks', 0)}"
            story.append(Paragraph(q_score, ParagraphStyle('Score', parent=normal_style, fontSize=10, textColor=colors.HexColor('#3fb950'))))
            
            # Keywords matched/missed
            keywords_matched = q.get('keywords_matched', [])
            keywords_missed = q.get('keywords_missed', [])
            
            if isinstance(keywords_matched, str):
                try:
                    keywords_matched = json.loads(keywords_matched)
                except:
                    keywords_matched = []
            
            if isinstance(keywords_missed, str):
                try:
                    keywords_missed = json.loads(keywords_missed)
                except:
                    keywords_missed = []
            
            if keywords_matched:
                story.append(Paragraph(f"✓ Keywords Matched: {', '.join(keywords_matched[:5])}", 
                                     ParagraphStyle('Matched', parent=normal_style, fontSize=9, textColor=colors.HexColor('#3fb950'))))
            
            if keywords_missed:
                story.append(Paragraph(f"✗ Keywords Missed: {', '.join(keywords_missed[:5])}", 
                                     ParagraphStyle('Missed', parent=normal_style, fontSize=9, textColor=colors.HexColor('#f85149'))))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Feedback Section
        feedback = evaluation_data.get('feedback', {})
        
        if feedback:
            story.append(PageBreak())
            story.append(Paragraph("Detailed Feedback", heading_style))
            
            # Good Answers
            good_answers = feedback.get('good_answers', [])
            if isinstance(good_answers, str):
                try:
                    good_answers = json.loads(good_answers)
                except:
                    good_answers = []
            
            if good_answers:
                story.append(Paragraph("✅ Good Answers:", ParagraphStyle('FeedbackHead', parent=normal_style, fontSize=12, textColor=colors.HexColor('#3fb950'), spaceBefore=10)))
                for item in good_answers:
                    story.append(Paragraph(f"• {item}", normal_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Areas to Improve
            areas_to_improve = feedback.get('areas_to_improve', [])
            if isinstance(areas_to_improve, str):
                try:
                    areas_to_improve = json.loads(areas_to_improve)
                except:
                    areas_to_improve = []
            
            if areas_to_improve:
                story.append(Paragraph("⚠️ Areas to Improve:", ParagraphStyle('FeedbackHead', parent=normal_style, fontSize=12, textColor=colors.HexColor('#d29922'), spaceBefore=10)))
                for item in areas_to_improve:
                    story.append(Paragraph(f"• {item}", normal_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Suggestions
            suggestions = feedback.get('suggestions', [])
            if isinstance(suggestions, str):
                try:
                    suggestions = json.loads(suggestions)
                except:
                    suggestions = []
            
            if suggestions:
                story.append(Paragraph("💡 Suggestions:", ParagraphStyle('FeedbackHead', parent=normal_style, fontSize=12, textColor=colors.HexColor('#58a6ff'), spaceBefore=10)))
                for item in suggestions:
                    story.append(Paragraph(f"• {item}", normal_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by ExamEval AI"
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise
