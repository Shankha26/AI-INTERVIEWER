from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    college = db.Column(db.String(150), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True, default='default.png')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('ResumeAnalysis', backref='user', cascade='all, delete-orphan', lazy=True)
    interviews = db.relationship('InterviewSession', backref='user', cascade='all, delete-orphan', lazy=True)
    aptitude_results = db.relationship('AptitudeResult', backref='user', cascade='all, delete-orphan', lazy=True)
    career_guidances = db.relationship('CareerGuidance', backref='user', cascade='all, delete-orphan', lazy=True)
    study_plans = db.relationship('StudyPlan', backref='user', cascade='all, delete-orphan', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', cascade='all, delete-orphan', lazy=True)
    recordings = db.relationship('Recording', backref='user', cascade='all, delete-orphan', lazy=True)
    voice_interviews = db.relationship('VoiceInterview', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'college': self.college,
            'branch': self.branch,
            'profile_image': self.profile_image,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
