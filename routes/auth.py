import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db
from models.user import User
from forms import RegistrationForm, LoginForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create user
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                college=form.college.data,
                branch=form.branch.data
            )
            new_user.set_password(form.password.data)
            
            # Elevate to admin automatically if first user or email/password contains "admin" for local development ease
            if User.query.count() == 0 or "admin" in form.email.data.lower() or "admin" in form.password.data.lower():
                new_user.is_admin = True
                
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user or not user.check_password(form.password.data):
            flash('Invalid email or password!', 'danger')
            return render_template('auth/login.html', form=form)
            
        login_user(user, remember=form.remember.data)
        flash(f'Welcome back, {user.name}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        elif user.is_admin:
            return redirect(url_for('admin.panel'))
        else:
            return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    # Manually populate choices if SelectField needs loading
    if request.method == 'GET':
        form.name.data = current_user.name
        form.college.data = current_user.college
        form.branch.data = current_user.branch
        
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.college = form.college.data
        current_user.branch = form.branch.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
            
        # File Upload for Profile Picture
        file = form.profile_image.data
        if file:
            filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
            file_path = os.path.join(current_app.config['PROFILE_FOLDER'], filename)
            
            # Make sure profile folder exists
            os.makedirs(current_app.config['PROFILE_FOLDER'], exist_ok=True)
            
            file.save(file_path)
            current_user.profile_image = filename
                
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')
            
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', form=form)

