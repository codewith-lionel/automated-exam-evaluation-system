"""API routes for the application."""

from flask import Blueprint, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

from backend.auth import login_required, admin_required
from backend.database import (
    create_evaluation, get_evaluation, get_user_evaluations, get_all_evaluations,
    create_question, get_evaluation_questions, create_feedback, get_evaluation_feedback,
    update_feedback, create_uploaded_file, get_dashboard_stats, get_user_by_id,
    delete_evaluation
)
from backend.ocr_processor import process_uploaded_file
from backend.nlp_evaluator import NLPEvaluator
from backend.pdf_generator import generate_evaluation_report
from backend.utils import allowed_file, save_uploaded_file, parse_questions_from_text
from config import Config

api_bp = Blueprint('api', __name__)

# Initialize NLP evaluator lazily
_nlp_evaluator = None

def get_nlp_evaluator():
    """Get or create NLP evaluator instance."""
    global _nlp_evaluator
    if _nlp_evaluator is None:
        _nlp_evaluator = NLPEvaluator()
    return _nlp_evaluator

@api_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_statistics():
    """Get dashboard statistics."""
    try:
        user_id = session.get('user_id')
        role = session.get('role')
        
        stats = get_dashboard_stats(user_id, role)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/dashboard/recent', methods=['GET'])
@login_required
def get_recent_activities():
    """Get recent evaluation activities."""
    try:
        user_id = session.get('user_id')
        role = session.get('role')
        
        limit = request.args.get('limit', 10, type=int)
        
        if role == 'admin':
            evaluations = get_all_evaluations(limit=limit)
        else:
            evaluations = get_user_evaluations(user_id, limit=limit)
        
        # Convert to list of dicts
        activities = []
        for eval in evaluations:
            activities.append({
                'id': eval['id'],
                'subject': eval['subject'],
                'exam_type': eval['exam_type'],
                'percentage': eval['percentage'],
                'status': eval['status'],
                'created_at': eval['created_at'],
                'username': eval.get('username', 'N/A') if role == 'admin' else None
            })
        
        return jsonify({
            'success': True,
            'activities': activities
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_exam():
    """Upload and process exam file."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file format. Allowed: PNG, JPG, JPEG, PDF'}), 400
        
        # Get form data
        subject = request.form.get('subject', 'General')
        exam_type = request.form.get('exam_type', 'Test')
        mode = request.form.get('mode', 'offline')  # offline or online
        total_marks = int(request.form.get('total_marks', 100))
        
        # Save file
        filename, filepath, filesize = save_uploaded_file(file)
        
        # Create initial evaluation record
        user_id = session.get('user_id')
        evaluation_id = create_evaluation(
            user_id, subject, exam_type, mode, total_marks, 0, 0, 'processing'
        )
        
        # Record uploaded file
        create_uploaded_file(evaluation_id, filename, filepath, filesize)
        
        # Process file based on mode
        if mode == 'offline':
            # Extract text using OCR
            extracted_text = process_uploaded_file(filepath)
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully',
                'evaluation_id': evaluation_id,
                'extracted_text': extracted_text
            }), 200
        else:
            # For online mode, text is provided directly
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'evaluation_id': evaluation_id
            }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/api/evaluate', methods=['POST'])
@login_required
def evaluate_exam():
    """Evaluate exam answers using NLP."""
    try:
        data = request.get_json()
        
        evaluation_id = data.get('evaluation_id')
        questions_data = data.get('questions', [])
        
        if not evaluation_id or not questions_data:
            return jsonify({'success': False, 'message': 'Missing evaluation_id or questions'}), 400
        
        # Get evaluation details
        evaluation = get_evaluation(evaluation_id)
        
        if not evaluation:
            return jsonify({'success': False, 'message': 'Evaluation not found'}), 404
        
        # Verify ownership
        if evaluation['user_id'] != session.get('user_id') and session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Evaluate answers
        nlp_evaluator = get_nlp_evaluator()
        results = nlp_evaluator.evaluate_multiple_answers(questions_data)
        
        # Save questions to database
        for q_result in results['questions']:
            create_question(
                evaluation_id,
                q_result['question_number'],
                q_result['question_text'],
                q_result['model_answer'],
                q_result['student_answer'],
                q_result['max_marks'],
                q_result['obtained_marks'],
                q_result['keywords_matched'],
                q_result['keywords_missed']
            )
        
        # Generate feedback
        nlp_evaluator = get_nlp_evaluator()
        feedback = nlp_evaluator.generate_feedback(results)
        
        # Save feedback
        create_feedback(
            evaluation_id,
            feedback['good_answers'],
            feedback['areas_to_improve'],
            feedback['suggestions']
        )
        
        # Update evaluation with final scores
        from backend.database import execute_query
        execute_query(
            'UPDATE evaluations SET obtained_marks = ?, percentage = ?, status = ? WHERE id = ?',
            (results['obtained_marks'], results['percentage'], 'completed', evaluation_id)
        )
        
        return jsonify({
            'success': True,
            'message': 'Evaluation completed successfully',
            'evaluation_id': evaluation_id,
            'results': results,
            'feedback': feedback
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Evaluation failed: {str(e)}'}), 500

@api_bp.route('/api/results/<int:evaluation_id>', methods=['GET'])
@login_required
def get_results(evaluation_id):
    """Get evaluation results."""
    try:
        # Get evaluation
        evaluation = get_evaluation(evaluation_id)
        
        if not evaluation:
            return jsonify({'success': False, 'message': 'Evaluation not found'}), 404
        
        # Verify ownership
        if evaluation['user_id'] != session.get('user_id') and session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get questions
        questions = get_evaluation_questions(evaluation_id)
        
        # Get feedback
        feedback = get_evaluation_feedback(evaluation_id)
        
        # Get user info
        user = get_user_by_id(evaluation['user_id'])
        
        # Format response
        result = {
            'id': evaluation['id'],
            'subject': evaluation['subject'],
            'exam_type': evaluation['exam_type'],
            'mode': evaluation['mode'],
            'total_marks': evaluation['total_marks'],
            'obtained_marks': evaluation['obtained_marks'],
            'percentage': evaluation['percentage'],
            'status': evaluation['status'],
            'created_at': evaluation['created_at'],
            'username': user['username'] if user else 'N/A',
            'email': user['email'] if user else 'N/A',
            'questions': []
        }
        
        # Format questions
        for q in questions:
            result['questions'].append({
                'question_number': q['question_number'],
                'question_text': q['question_text'],
                'model_answer': q['model_answer'],
                'student_answer': q['student_answer'],
                'max_marks': q['max_marks'],
                'obtained_marks': q['obtained_marks'],
                'keywords_matched': json.loads(q['keywords_matched']) if q['keywords_matched'] else [],
                'keywords_missed': json.loads(q['keywords_missed']) if q['keywords_missed'] else []
            })
        
        # Format feedback
        if feedback:
            result['feedback'] = {
                'good_answers': json.loads(feedback['good_answers']) if feedback['good_answers'] else [],
                'areas_to_improve': json.loads(feedback['areas_to_improve']) if feedback['areas_to_improve'] else [],
                'suggestions': json.loads(feedback['suggestions']) if feedback['suggestions'] else [],
                'additional_notes': feedback['additional_notes'] or ''
            }
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/results/<int:evaluation_id>', methods=['DELETE'])
@login_required
def delete_result(evaluation_id):
    """Delete an evaluation."""
    try:
        # Get evaluation
        evaluation = get_evaluation(evaluation_id)
        
        if not evaluation:
            return jsonify({'success': False, 'message': 'Evaluation not found'}), 404
        
        # Verify ownership or admin
        if evaluation['user_id'] != session.get('user_id') and session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Delete evaluation
        delete_evaluation(evaluation_id)
        
        return jsonify({
            'success': True,
            'message': 'Evaluation deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/results', methods=['GET'])
@login_required
def get_all_results():
    """Get all evaluation results for current user."""
    try:
        user_id = session.get('user_id')
        role = session.get('role')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if role == 'admin':
            evaluations = get_all_evaluations()
        else:
            evaluations = get_user_evaluations(user_id)
        
        # Format results
        results = []
        for eval in evaluations:
            # Get questions for this evaluation to calculate stats
            questions = get_evaluation_questions(eval['id'])
            
            correct = 0
            partial = 0
            incorrect = 0
            
            for q in questions:
                if q['obtained_marks'] == q['max_marks']:
                    correct += 1
                elif q['obtained_marks'] > 0:
                    partial += 1
                else:
                    incorrect += 1
            
            # Get student name from username or email
            student_name = eval.get('username', eval.get('email', 'Student'))
            if student_name and '@' in student_name:
                student_name = student_name.split('@')[0].title()
            
            results.append({
                'id': eval['id'],
                'student_name': student_name,
                'exam_name': f"{eval['subject']} - {eval['exam_type']}",
                'subject': eval['subject'],
                'exam_type': eval['exam_type'],
                'score': round(eval['percentage'], 2),
                'percentage': round(eval['percentage'], 2),
                'status': eval['status'],
                'date': eval['created_at'],
                'created_at': eval['created_at'],
                'correct': correct,
                'partial': partial,
                'incorrect': incorrect,
                'total_questions': len(questions)
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/feedback/<int:evaluation_id>', methods=['PUT'])
@admin_required
def update_evaluation_feedback(evaluation_id):
    """Update feedback for an evaluation (admin only)."""
    try:
        data = request.get_json()
        
        good_answers = data.get('good_answers', [])
        areas_to_improve = data.get('areas_to_improve', [])
        suggestions = data.get('suggestions', [])
        additional_notes = data.get('additional_notes', '')
        
        update_feedback(evaluation_id, good_answers, areas_to_improve, suggestions, additional_notes)
        
        return jsonify({
            'success': True,
            'message': 'Feedback updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/api/results/<int:evaluation_id>/pdf', methods=['GET'])
@login_required
def download_pdf_report(evaluation_id):
    """Generate and download PDF report."""
    try:
        # Get evaluation data
        evaluation = get_evaluation(evaluation_id)
        
        if not evaluation:
            return jsonify({'success': False, 'message': 'Evaluation not found'}), 404
        
        # Verify ownership
        if evaluation['user_id'] != session.get('user_id') and session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get complete evaluation data
        questions = get_evaluation_questions(evaluation_id)
        feedback = get_evaluation_feedback(evaluation_id)
        user = get_user_by_id(evaluation['user_id'])
        
        # Prepare data for PDF
        pdf_data = {
            'username': user['username'] if user else 'N/A',
            'email': user['email'] if user else 'N/A',
            'subject': evaluation['subject'],
            'exam_type': evaluation['exam_type'],
            'total_marks': evaluation['total_marks'],
            'obtained_marks': evaluation['obtained_marks'],
            'percentage': evaluation['percentage'],
            'created_at': evaluation['created_at'],
            'questions': []
        }
        
        for q in questions:
            pdf_data['questions'].append({
                'question_number': q['question_number'],
                'question_text': q['question_text'],
                'obtained_marks': q['obtained_marks'],
                'max_marks': q['max_marks'],
                'keywords_matched': q['keywords_matched'],
                'keywords_missed': q['keywords_missed']
            })
        
        if feedback:
            pdf_data['feedback'] = {
                'good_answers': feedback['good_answers'],
                'areas_to_improve': feedback['areas_to_improve'],
                'suggestions': feedback['suggestions']
            }
        
        # Generate PDF
        pdf_filename = f"evaluation_report_{evaluation_id}.pdf"
        pdf_path = os.path.join(Config.UPLOAD_FOLDER, pdf_filename)
        
        generate_evaluation_report(pdf_data, pdf_path)
        
        # Send file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'PDF generation failed: {str(e)}'}), 500

@api_bp.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get current user profile."""
    try:
        user_id = session.get('user_id')
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user['created_at']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
