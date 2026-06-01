import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, login_required
from config import Config
from models.database import db
from models.user import User

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.resume import resume_bp
from routes.interview import interview_bp
from routes.aptitude import aptitude_bp
from routes.career import career_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Apply ProxyFix middleware (Issue 3: Session Persist over Reverse Proxies)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize DB
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Ensure necessary upload folders exist on startup (wrapped safely for serverless environments)
    for folder_path in [
        app.config['UPLOAD_FOLDER'],
        app.config['RESUME_FOLDER'],
        app.config['VIDEO_FOLDER'],
        app.config['AUDIO_FOLDER'],
        app.config['PROFILE_FOLDER']
    ]:
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create upload directory {folder_path} on serverless runtime: {e}")
        
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(aptitude_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(admin_bp)
    
    # Protected Routes Middleware (Issue 5: Access Control Enforcement)
    from flask import request, redirect, url_for, flash, abort, session
    from flask_login import current_user
    
    @app.before_request
    def debug_log_request():
        if not app.config.get('DEBUG_MODE', False) and os.environ.get('FLASK_DEBUG') != '1':
            return
            
        user_info = "Anonymous"
        role_info = "None"
        if current_user.is_authenticated:
            user_info = f"ID: {current_user.id}, Email: {current_user.email}"
            role_info = current_user.role
            
        cookie_info = {k: v for k, v in request.cookies.items()}
        session_info = {k: v for k, v in session.items() if not k.startswith('_')}
        
        print("\n--- [PROD DEBUG MODE: Request Interceptor] ---")
        print(f"Path: {request.path}")
        print(f"Method: {request.method}")
        print(f"Client IP: {request.remote_addr}")
        print(f"Current User: {user_info}")
        print(f"Current Role: {role_info}")
        print(f"Session Status: {session_info}")
        print(f"Cookie Status: {cookie_info}")
        print("----------------------------------------------\n")
    
    @app.before_request
    def check_route_access():
        # Exempt static assets, dynamic uploads, authentication routes, and the landing page from role checks
        exempt_prefixes = ['/static', '/uploads', '/auth', '/login', '/register', '/logout']
        exempt_endpoints = ['auth.login', 'auth.register', 'auth.logout', 'static', 'uploaded_file', 'dashboard.landing']
        
        if not request.endpoint or request.endpoint in exempt_endpoints:
            return
            
        for prefix in exempt_prefixes:
            if request.path.startswith(prefix):
                return
                
        if current_user.is_authenticated:
            # Issue 5: Admin visiting Candidate route -> Redirect to Admin Dashboard (/admin/panel)
            if current_user.is_admin:
                candidate_prefixes = ['/dashboard', '/profile', '/resume', '/interview', '/aptitude', '/career', '/application']
                is_candidate_route = any(request.path.startswith(pref) for pref in candidate_prefixes) and not request.path.startswith('/admin')
                
                if is_candidate_route:
                    flash('Administrative sessions are automatically redirected to the control panel.', 'info')
                    return redirect(url_for('admin.panel'))
            else:
                # Issue 5: Candidate visiting Admin route -> 403 Forbidden
                if request.path.startswith('/admin') or request.path.startswith('/admindashboard'):
                    abort(403)
                    
    # Serve `/admindashboard` redirect (Issue 5: Admin Routes protection)
    @app.route('/admindashboard')
    @login_required
    def admin_dashboard_redirect():
        if current_user.is_admin:
            return redirect(url_for('admin.panel'))
        else:
            abort(403)
                    
    # Serve uploaded media (resumes, video responses, audio responses, profile photos)
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    # Error Handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
        
    # Custom template variables / context processor
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
        
    # Initialize database tables and auto-seed if empty
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            if 'users' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('users')]
                
                # Migrate password_hash -> password
                if 'password_hash' in columns and 'password' not in columns:
                    print("[Migration] Migrating users table: password_hash -> password...")
                    try:
                        db.session.execute(text("ALTER TABLE users ADD COLUMN password VARCHAR(255)"))
                        db.session.commit()
                        db.session.execute(text("UPDATE users SET password = password_hash"))
                        db.session.commit()
                    except Exception as ex:
                        print(f"[Migration Warning] Error migrating password: {ex}")
                        db.session.rollback()
                        
                # Migrate is_admin -> role
                if 'is_admin' in columns and 'role' not in columns:
                    print("[Migration] Migrating users table: is_admin -> role...")
                    try:
                        db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'candidate'"))
                        db.session.commit()
                        db.session.execute(text("UPDATE users SET role = 'admin' WHERE is_admin = 1 OR is_admin = true"))
                        db.session.commit()
                    except Exception as ex:
                        print(f"[Migration Warning] Error migrating role: {ex}")
                        db.session.rollback()
                        
                # Migrate created_at -> createdAt
                if 'created_at' in columns and 'createdAt' not in columns:
                    print("[Migration] Migrating users table: created_at -> createdAt...")
                    try:
                        db.session.execute(text('ALTER TABLE users ADD COLUMN "createdAt" TIMESTAMP'))
                        db.session.commit()
                        db.session.execute(text('UPDATE users SET "createdAt" = created_at'))
                        db.session.commit()
                    except Exception as ex:
                        print(f"[Migration Warning] Error migrating createdAt: {ex}")
                        db.session.rollback()
                        
            db.create_all()
            print("Database schemas created/verified successfully!")
            
            # Auto-seed default credentials and question bank on startup if clean
            from models.user import User
            if User.query.count() == 0:
                print("Database is empty. Initiating automatic seeding process...")
                from seed import perform_seeding
                perform_seeding()
            else:
                # Correct role of any users who were incorrectly marked as admin (email does not contain "admin" or does not end with "@prepai.pro")
                incorrect_admins = User.query.filter(User.role == 'admin').all()
                corrected = False
                for u in incorrect_admins:
                    email_lower = u.email.lower()
                    if not ("admin" in email_lower and email_lower.endswith("@prepai.pro")):
                        print(f"[Correction] Reverting user {u.email} role from admin back to candidate...")
                        u.is_admin = False
                        corrected = True
                if corrected:
                    db.session.commit()
        except Exception as e:
            print(f"Error creating/seeding database tables: {e}")
            
    return app

app = create_app()

if __name__ == '__main__':
    # Run server locally on 127.0.0.1:5000
    app.run(debug=True, host='127.0.0.1', port=5000)
