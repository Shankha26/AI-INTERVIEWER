from datetime import datetime
from models.database import db

class CareerGuidance(db.Model):
    __tablename__ = 'career_guidance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skills_input = db.Column(db.Text, nullable=False)
    interests_input = db.Column(db.Text, nullable=False)
    preferred_domain = db.Column(db.String(100), nullable=True)
    
    # AI recommendations stored as structured markdown or JSON text
    career_paths = db.Column(db.Text, nullable=True)
    required_skills = db.Column(db.Text, nullable=True)
    roadmap = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skills_input': self.skills_input,
            'interests_input': self.interests_input,
            'preferred_domain': self.preferred_domain,
            'career_paths': self.career_paths,
            'required_skills': self.required_skills,
            'roadmap': self.roadmap,
            'certifications': self.certifications,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False) # '7-Day', '15-Day', '30-Day'
    plan_content = db.Column(db.Text, nullable=False)    # Detailed Markdown text containing daily tasks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'plan_content': self.plan_content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topics_to_improve = db.Column(db.Text, nullable=True)
    interview_questions = db.Column(db.Text, nullable=True)
    learning_resources = db.Column(db.Text, nullable=True)
    practice_tests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topics_to_improve': self.topics_to_improve,
            'interview_questions': self.interview_questions,
            'learning_resources': self.learning_resources,
            'practice_tests': self.practice_tests,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
