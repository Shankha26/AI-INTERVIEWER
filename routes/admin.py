from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.database import db
from models.user import User
from models.question import Question
from models.resume import ResumeAnalysis
from models.interview import InterviewSession
from models.aptitude import AptitudeResult
from forms import QuestionForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/panel')
@login_required
@admin_required
def panel():
    # Gather global metrics
    total_users = User.query.count()
    total_resumes = ResumeAnalysis.query.count()
    total_interviews = InterviewSession.query.count()
    total_quizzes = AptitudeResult.query.count()
    
    users = User.query.all()
    questions = Question.query.order_by(Question.created_at.desc()).all()
    form = QuestionForm()
    
    return render_template(
        'admin/panel.html',
        total_users=total_users,
        total_resumes=total_resumes,
        total_interviews=total_interviews,
        total_quizzes=total_quizzes,
        users=users,
        questions=questions,
        form=form
    )

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash('You cannot delete your own admin account!', 'danger')
        return redirect(url_for('admin.panel'))
        
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.name} has been successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {e}', 'danger')
        
    return redirect(url_for('admin.panel'))

@admin_bp.route('/question/add', methods=['POST'])
@login_required
@admin_required
def add_question():
    form = QuestionForm()
    
    if form.validate_on_submit():
        try:
            new_q = Question(
                subject=form.subject.data,
                category=form.category.data,
                question_text=form.question_text.data,
                option_a=form.option_a.data,
                option_b=form.option_b.data,
                option_c=form.option_c.data,
                option_d=form.option_d.data,
                correct_option=form.correct_option.data,
                difficulty=form.difficulty.data,
                explanation=form.explanation.data
            )
            db.session.add(new_q)
            db.session.commit()
            flash('New question successfully added to the bank!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding question: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
        
    return redirect(url_for('admin.panel'))

@admin_bp.route('/question/delete/<int:q_id>', methods=['POST'])
@login_required
@admin_required
def delete_question(q_id):
    q = Question.query.get_or_404(q_id)
    try:
        db.session.delete(q)
        db.session.commit()
        flash('Question has been successfully removed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {e}', 'danger')
        
    return redirect(url_for('admin.panel'))
