import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager
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
    from flask import request, redirect, url_for, flash, abort
    from flask_login import current_user
    
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
                candidate_prefixes = ['/dashboard', '/profile', '/resume', '/interview', '/aptitude', '/career']
                is_candidate_route = any(request.path.startswith(pref) for pref in candidate_prefixes) and not request.path.startswith('/admin')
                
                if is_candidate_route:
                    flash('Administrative sessions are automatically redirected to the control panel.', 'info')
                    return redirect(url_for('admin.panel'))
            else:
                # Issue 5: Candidate visiting Admin route -> 403 Forbidden
                if request.path.startswith('/admin'):
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
            db.create_all()
            print("Database schemas created/verified successfully!")
            
            # Auto-seed default credentials and question bank on startup if clean
            from models.user import User
            if User.query.count() == 0:
                print("Database is empty. Initiating automatic seeding process...")
                from seed import perform_seeding
                perform_seeding()
        except Exception as e:
            print(f"Error creating/seeding database tables: {e}")
            
    return app

app = create_app()

if __name__ == '__main__':
    # Run server locally on 127.0.0.1:5000
    app.run(debug=True, host='127.0.0.1', port=5000)
