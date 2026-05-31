import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db
from models.resume import ResumeAnalysis
from services.resume_parser import extract_text_from_pdf
from services.gemini_service import GeminiService

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@resume_bp.route('/analyzer', methods=['GET', 'POST'])
@login_required
def analyzer():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        if file.filename == '':
            flash('No resume selected for upload.', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
            file_path = os.path.join(current_app.config['RESUME_FOLDER'], filename)
            
            # Ensure upload folder exists
            os.makedirs(current_app.config['RESUME_FOLDER'], exist_ok=True)
            
            try:
                # Save the file
                file.save(file_path)
                
                # Extract text
                resume_text = extract_text_from_pdf(file_path)
                
                if not resume_text:
                    flash('Could not extract legible text from your PDF. Please ensure it is not scanned/image-only.', 'danger')
                    return redirect(request.url)
                
                # Analyze using Gemini API
                gemini = GeminiService()
                analysis_results = gemini.analyze_resume_ats(resume_text)
                
                # Parse JSON fields safely
                # GeminiService already handles fallback and json validation
                ats_score = int(analysis_results.get('ats_score', 0))
                strengths_list = analysis_results.get('strengths', [])
                weaknesses_list = analysis_results.get('weaknesses', [])
                suggestions_list = analysis_results.get('suggestions', [])
                skills_list = analysis_results.get('skills', [])
                missing_kw_list = analysis_results.get('missing_keywords', [])
                formatting_feedback = analysis_results.get('formatting_feedback', 'Formatting analysis completed.')
                
                # Join lists to store in database as plain text / structured strings
                strengths = "\n".join([f"- {s}" for s in strengths_list])
                weaknesses = "\n".join([f"- {w}" for w in weaknesses_list])
                suggestions = "\n".join([f"- {s}" for s in suggestions_list])
                skills = ", ".join(skills_list)
                missing_keywords = ", ".join(missing_kw_list)
                
                # Save to database
                new_analysis = ResumeAnalysis(
                    user_id=current_user.id,
                    ats_score=ats_score,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    suggestions=suggestions,
                    skills=skills,
                    missing_keywords=missing_keywords,
                    formatting_feedback=formatting_feedback
                )
                
                db.session.add(new_analysis)
                db.session.commit()
                
                flash('Resume successfully uploaded and evaluated!', 'success')
                return redirect(url_for('resume.report', analysis_id=new_analysis.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while analyzing the resume: {e}', 'danger')
                return redirect(request.url)
        else:
            flash('Only PDF resumes are supported!', 'danger')
            return redirect(request.url)
            
    return render_template('resume/analyzer.html')

@resume_bp.route('/report/<int:analysis_id>')
@login_required
def report(analysis_id):
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    
    # Split strings back into lists for clean layout rendering
    strengths_list = [line[2:] for line in analysis.strengths.split('\n') if line.startswith('- ')] if analysis.strengths else []
    weaknesses_list = [line[2:] for line in analysis.weaknesses.split('\n') if line.startswith('- ')] if analysis.weaknesses else []
    suggestions_list = [line[2:] for line in analysis.suggestions.split('\n') if line.startswith('- ')] if analysis.suggestions else []
    skills_list = [s.strip() for s in analysis.skills.split(',')] if analysis.skills else []
    missing_kw_list = [k.strip() for k in analysis.missing_keywords.split(',')] if analysis.missing_keywords else []
    
    return render_template(
        'resume/report.html',
        analysis=analysis,
        strengths=strengths_list,
        weaknesses=weaknesses_list,
        suggestions=suggestions_list,
        skills=skills_list,
        missing_keywords=missing_kw_list
    )

@resume_bp.route('/history')
@login_required
def history():
    analyses = ResumeAnalysis.query.filter_by(user_id=current_user.id).order_by(ResumeAnalysis.created_at.desc()).all()
    return render_template('resume/history.html', analyses=analyses)
