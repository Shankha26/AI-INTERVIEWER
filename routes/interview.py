import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db
from models.interview import InterviewSession, VoiceInterview, Recording
from services.gemini_service import GeminiService

interview_bp = Blueprint('interview', __name__, url_prefix='/interview')

@interview_bp.route('/setup')
@login_required
def setup():
    domains = ['HR', 'C Programming', 'C++', 'Python', 'Java', 'DBMS', 'Operating Systems', 'Computer Networks', 'Data Structures and Algorithms']
    companies = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Deloitte', 'Cognizant', 'Google', 'Microsoft', 'Amazon']
    return render_template('interview/setup.html', domains=domains, companies=companies)

@interview_bp.route('/start', methods=['POST'])
@login_required
def start():
    category_type = request.form.get('category_type') # 'domain' or 'company'
    domain = request.form.get('domain')
    company = request.form.get('company')
    mode = request.form.get('mode') # 'text' or 'voice'
    
    selected_domain = company if category_type == 'company' else domain
    
    if not selected_domain:
        flash('Please select a valid subject or company!', 'danger')
        return redirect(url_for('interview.setup'))
        
    # Generate questions via Gemini
    try:
        gemini = GeminiService()
        questions_raw = gemini.generate_interview_questions(selected_domain, count=5)
        
        # Save session parameters in Flask session
        session['interview_domain'] = selected_domain
        session['interview_mode'] = mode
        session['interview_questions'] = questions_raw
        session['interview_answers'] = []
        session['interview_start_time'] = datetime.utcnow().isoformat()
        
        return redirect(url_for('interview.session_run'))
    except Exception as e:
        flash(f'Failed to start interview: {e}', 'danger')
        return redirect(url_for('interview.setup'))

@interview_bp.route('/session', methods=['GET'])
@login_required
def session_run():
    if 'interview_questions' not in session:
        flash('No active interview session found.', 'danger')
        return redirect(url_for('interview.setup'))
        
    questions = session['interview_questions']
    domain = session['interview_domain']
    mode = session['interview_mode']
    
    return render_template('interview/session.html', questions=questions, domain=domain, mode=mode)

@interview_bp.route('/upload-recording', methods=['POST'])
@login_required
def upload_recording():
    """AJAX endpoint for uploading audio and video recording chunks."""
    if 'audio' not in request.files and 'video' not in request.files:
        return jsonify({'error': 'No recording files found in request.'}), 400
        
    session_id = request.form.get('session_id')
    question_idx = request.form.get('question_idx', '0')
    
    saved_files = {}
    
    # Save Audio file
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename != '':
            os.makedirs(current_app.config['AUDIO_FOLDER'], exist_ok=True)
            filename = f"user_{current_user.id}_q{question_idx}_{int(datetime.utcnow().timestamp())}.wav"
            file_path = os.path.join(current_app.config['AUDIO_FOLDER'], filename)
            audio_file.save(file_path)
            saved_files['audio'] = f"/uploads/audio/{filename}"
            
            # Log recording
            new_rec = Recording(
                user_id=current_user.id,
                file_path=f"uploads/audio/{filename}",
                file_type='audio'
            )
            db.session.add(new_rec)
            db.session.commit()
            
    # Save Video file
    if 'video' in request.files:
        video_file = request.files['video']
        if video_file.filename != '':
            os.makedirs(current_app.config['VIDEO_FOLDER'], exist_ok=True)
            filename = f"user_{current_user.id}_q{question_idx}_{int(datetime.utcnow().timestamp())}.webm"
            file_path = os.path.join(current_app.config['VIDEO_FOLDER'], filename)
            video_file.save(file_path)
            saved_files['video'] = f"/uploads/videos/{filename}"
            
            # Log recording
            new_rec = Recording(
                user_id=current_user.id,
                file_path=f"uploads/videos/{filename}",
                file_type='video'
            )
            db.session.add(new_rec)
            db.session.commit()
            
    return jsonify({
        'status': 'success',
        'paths': saved_files
    })

@interview_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    if 'interview_questions' not in session:
        return jsonify({'error': 'No active interview session.'}), 400
        
    data = request.json
    answers = data.get('answers', []) # List of answers submitted
    voice_details = data.get('voice_details', {}) # Dict indexed by question index containing paths, transcripts
    
    questions = session['interview_questions']
    domain = session['interview_domain']
    mode = session['interview_mode']
    
    if not answers or len(answers) == 0:
        return jsonify({'error': 'No answers submitted!'}), 400
        
    # Build list of Q&A for Gemini Service
    qas = []
    for idx, question in enumerate(questions):
        # Fallback to empty if answer is missing
        answer = answers[idx] if idx < len(answers) else "No answer provided."
        qas.append({
            'question': question['question_text'],
            'answer': answer
        })
        
    try:
        gemini = GeminiService()
        evaluation = gemini.evaluate_interview_answers(domain, qas)
        
        # Save main interview session
        new_session = InterviewSession(
            user_id=current_user.id,
            domain=domain,
            score=int(evaluation.get('score', 50)),
            feedback=evaluation.get('feedback', 'No feedback provided.')
        )
        db.session.add(new_session)
        db.session.flush() # Flush to get session ID
        
        # Process Voice/Communication details if voice mode was active
        if mode == 'voice' or voice_details:
            for idx, q_item in enumerate(questions):
                ans_str = answers[idx] if idx < len(answers) else ""
                q_details = voice_details.get(str(idx), {})
                
                audio_path = q_details.get('audio_path', '')
                video_path = q_details.get('video_path', '')
                transcript = q_details.get('transcript', ans_str) # Real-time webkit transcript
                
                # Perform granular speech assessment on Gemini
                voice_analysis = gemini.evaluate_voice_response(q_item['question_text'], transcript)
                
                voice_interview = VoiceInterview(
                    user_id=current_user.id,
                    session_id=new_session.id,
                    question_text=q_item['question_text'],
                    transcript=transcript,
                    audio_path=audio_path,
                    video_path=video_path,
                    fluency_score=int(voice_analysis.get('fluency_score', 50)),
                    confidence_score=int(voice_analysis.get('confidence_score', 50)),
                    technical_accuracy_score=int(voice_analysis.get('technical_accuracy_score', 50)),
                    grammar_score=int(voice_analysis.get('grammar_score', 50)),
                    relevance_score=int(voice_analysis.get('relevance_score', 50)),
                    feedback=voice_analysis.get('feedback', 'Voice evaluation processed.')
                )
                db.session.add(voice_interview)
                
        db.session.commit()
        
        # Clear interview context from Flask session
        session.pop('interview_domain', None)
        session.pop('interview_mode', None)
        session.pop('interview_questions', None)
        session.pop('interview_answers', None)
        session.pop('interview_start_time', None)
        
        return jsonify({
            'status': 'success',
            'redirect_url': url_for('interview.report', session_id=new_session.id)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting interview: {e}")
        return jsonify({'error': f'Failed to process session evaluation: {e}'}), 500

@interview_bp.route('/report/<int:session_id>')
@login_required
def report(session_id):
    interview = InterviewSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    
    # Check if voice interviews exist
    voice_evals = VoiceInterview.query.filter_by(session_id=interview.id).all()
    
    # Calculate communications scorecard averages
    comm_stats = None
    if voice_evals:
        comm_stats = {
            'fluency': round(sum(v.fluency_score for v in voice_evals) / len(voice_evals)),
            'confidence': round(sum(v.confidence_score for v in voice_evals) / len(voice_evals)),
            'accuracy': round(sum(v.technical_accuracy_score for v in voice_evals) / len(voice_evals)),
            'grammar': round(sum(v.grammar_score for v in voice_evals) / len(voice_evals)),
            'relevance': round(sum(v.relevance_score for v in voice_evals) / len(voice_evals))
        }
        
    # Get any saved recordings for this session
    # We can fetch via matching filenames or simply check all recordings for user
    
    return render_template(
        'interview/report.html',
        interview=interview,
        voice_evals=voice_evals,
        comm_stats=comm_stats
    )

@interview_bp.route('/history')
@login_required
def history():
    sessions = InterviewSession.query.filter_by(user_id=current_user.id).order_by(InterviewSession.created_at.desc()).all()
    return render_template('interview/history.html', sessions=sessions)
