from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user, logout_user
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
        if not current_user.is_authenticated:
            flash('Please log in to access the Administrative Panel.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            logout_user() # Auto-logout sticking non-admin candidate sessions
            flash('Access Denied: Admin privileges required. Please sign in with an Administrator account.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/panel')
@login_required
@admin_required
def panel():
    # Gather global metrics
    total_users = User.query.count()
    total_candidates = User.query.filter_by(is_admin=False).count()
    total_admins = User.query.filter_by(is_admin=True).count()
    total_resumes = ResumeAnalysis.query.count()
    total_interviews = InterviewSession.query.count()
    total_quizzes = AptitudeResult.query.count()
    
    # Simple Pagination
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)
    users = pagination.items
    
    questions = Question.query.order_by(Question.created_at.desc()).all()
    form = QuestionForm()
    
    # Production debugging telemetry under DEBUG_MODE (Issue 8)
    from flask import current_app
    if current_app.config.get('DEBUG_MODE', False):
        print("\n--- [PROD DEBUG MODE: Database Query Telemetry] ---")
        print(f"Total Users Count: {total_users}")
        print(f"Total Candidates Count: {total_candidates}")
        print(f"Total Admins Count: {total_admins}")
        print(f"Loaded users page {page}: {[u.to_dict() for u in users]}")
        print("---------------------------------------------------\n")
        
    return render_template(
        'admin/panel.html',
        total_users=total_users,
        total_candidates=total_candidates,
        total_admins=total_admins,
        total_resumes=total_resumes,
        total_interviews=total_interviews,
        total_quizzes=total_quizzes,
        users=users,
        pagination=pagination,
        questions=questions,
        form=form
    )

@admin_bp.route('/users')
@admin_bp.route('/manage')
@admin_bp.route('/settings')
@login_required
@admin_required
def admin_redirects():
    return redirect(url_for('admin.panel'))

@admin_bp.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    name = request.form.get('name')
    email = request.form.get('email')
    college = request.form.get('college')
    branch = request.form.get('branch')
    role = request.form.get('role')
    
    if not name or not email:
        flash('Name and Email are required fields!', 'danger')
        return redirect(url_for('admin.panel'))
        
    # Prevent duplicate emails
    existing = User.query.filter(User.email == email, User.id != user_id).first()
    if existing:
        flash('Email address is already linked to another user account.', 'danger')
        return redirect(url_for('admin.panel'))
        
    try:
        user.name = name
        user.email = email
        user.college = college
        user.branch = branch
        
        # Prevent self-demotion lockout
        if current_user.id != user_id and role in ['admin', 'candidate']:
            user.role = role
            
        db.session.commit()
        flash(f'User {user.name} profile successfully updated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user details: {e}', 'danger')
        
    return redirect(url_for('admin.panel'))

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

@admin_bp.route('/user/toggle-role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_role(user_id):
    if current_user.id == user_id:
        flash('You cannot change your own administrative role!', 'danger')
        return redirect(url_for('admin.panel'))
        
    user = User.query.get_or_404(user_id)
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        role_name = "Admin" if user.is_admin else "Candidate"
        flash(f'User {user.name} role successfully changed to {role_name}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing user role: {e}', 'danger')
        
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
