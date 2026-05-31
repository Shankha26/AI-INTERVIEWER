from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.career import CareerGuidance, StudyPlan, Recommendation
from models.interview import InterviewSession
from models.aptitude import AptitudeResult
from services.gemini_service import GeminiService
from sqlalchemy import desc
from forms import CareerCounselorForm, StudyPlanForm

career_bp = Blueprint('career', __name__, url_prefix='/career')

@career_bp.route('/counselor', methods=['GET', 'POST'])
@login_required
def counselor():
    guidance = CareerGuidance.query.filter_by(user_id=current_user.id).order_by(desc(CareerGuidance.created_at)).first()
    form = CareerCounselorForm()
    
    if form.validate_on_submit():
        skills = form.skills.data
        interests = form.interests.data
        preferred_domain = form.preferred_domain.data
        
        try:
            gemini = GeminiService()
            roadmap_data = gemini.generate_career_guidance(skills, interests, preferred_domain)
            
            # Save to Database
            new_guidance = CareerGuidance(
                user_id=current_user.id,
                skills_input=skills,
                interests_input=interests,
                preferred_domain=preferred_domain,
                career_paths=roadmap_data.get('career_paths', ''),
                required_skills=roadmap_data.get('required_skills', ''),
                roadmap=roadmap_data.get('roadmap', ''),
                certifications=roadmap_data.get('certifications', '')
            )
            db.session.add(new_guidance)
            
            # Also generate standard Recommendations dynamically
            rec_data = gemini.evaluate_voice_response(
                f"Skills: {skills}, Interests: {interests}, Domain: {preferred_domain}", 
                "Identify top 3 coding domains to study, resource links, and next practice targets."
            )
            # Adapt the output into Recommendation format
            new_rec = Recommendation(
                user_id=current_user.id,
                topics_to_improve=f"Practice in {preferred_domain or 'General Tech'} areas.",
                interview_questions="Study Object Oriented design, and advanced algorithmic puzzles.",
                learning_resources="- PrepAI Pro Question Bank\n- Official Language Docs\n- GeeksforGeeks placement section",
                practice_tests="Recommended Mock Interview on Career Choice and basic Verbal Aptitude tests."
            )
            db.session.add(new_rec)
            
            db.session.commit()
            flash('Career pathway roadmap generated successfully!', 'success')
            return redirect(url_for('career.counselor'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('career.counselor'))
            
    return render_template('career/counselor.html', guidance=guidance, form=form)

@career_bp.route('/study-plan', methods=['GET', 'POST'])
@login_required
def study_plan():
    plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(desc(StudyPlan.created_at)).all()
    latest_plan = plans[0] if plans else None
    form = StudyPlanForm()
    
    if form.validate_on_submit():
        plan_type = form.plan_type.data
        weak_topics = form.weak_topics.data
        
        # Calculate recent scores to pass to Gemini API
        interviews = InterviewSession.query.filter_by(user_id=current_user.id).all()
        avg_interview = round(sum(i.score for i in interviews) / len(interviews)) if interviews else 60
        
        aptitude = AptitudeResult.query.filter_by(user_id=current_user.id).all()
        avg_apt = round(sum(a.score / a.total_questions * 100 for a in aptitude) / len(aptitude)) if aptitude else 60
        
        try:
            gemini = GeminiService()
            plan_data = gemini.generate_study_plan(plan_type, avg_interview, avg_apt, weak_topics)
            
            new_plan = StudyPlan(
                user_id=current_user.id,
                plan_type=plan_type,
                plan_content=plan_data.get('plan_content', '# Study Plan')
            )
            db.session.add(new_plan)
            db.session.commit()
            
            flash(f'Your personalized {plan_type} study plan is ready!', 'success')
            return redirect(url_for('career.study_plan'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating study plan: {e}', 'danger')
            
    return render_template('career/study_plan.html', plans=plans, latest_plan=latest_plan, form=form)

@career_bp.route('/recommendations')
@login_required
def recommendations():
    recs = Recommendation.query.filter_by(user_id=current_user.id).order_by(desc(Recommendation.created_at)).all()
    return render_template('career/recommendations.html', recommendations=recs)
