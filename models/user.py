from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from models.database import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    college = db.Column(db.String(150), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True, default='default.png')
    role = db.Column(db.String(50), default='candidate', nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('ResumeAnalysis', backref='user', cascade='all, delete-orphan', lazy=True)
    interviews = db.relationship('InterviewSession', backref='user', cascade='all, delete-orphan', lazy=True)
    aptitude_results = db.relationship('AptitudeResult', backref='user', cascade='all, delete-orphan', lazy=True)
    career_guidances = db.relationship('CareerGuidance', backref='user', cascade='all, delete-orphan', lazy=True)
    study_plans = db.relationship('StudyPlan', backref='user', cascade='all, delete-orphan', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', cascade='all, delete-orphan', lazy=True)
    recordings = db.relationship('Recording', backref='user', cascade='all, delete-orphan', lazy=True)
    voice_interviews = db.relationship('VoiceInterview', backref='user', cascade='all, delete-orphan', lazy=True)

    # Hybrid properties for full backward compatibility
    @hybrid_property
    def password_hash(self):
        return self.password
        
    @password_hash.setter
    def password_hash(self, value):
        self.password = value

    @hybrid_property
    def is_admin(self):
        return self.role == 'admin'
        
    @is_admin.setter
    def is_admin(self, value):
        self.role = 'admin' if value else 'candidate'
        
    @is_admin.expression
    def is_admin(cls):
        return cls.role == 'admin'

    @hybrid_property
    def created_at(self):
        return self.createdAt
        
    @created_at.setter
    def created_at(self, value):
        self.createdAt = value
        
    @created_at.expression
    def created_at(cls):
        return cls.createdAt

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'college': self.college,
            'branch': self.branch,
            'profile_image': self.profile_image,
            'role': self.role,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None
        }

