from datetime import datetime
from models.database import db

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ats_score = db.Column(db.Integer, nullable=False)  # 0 to 100
    strengths = db.Column(db.Text, nullable=True)      # Detailed list or paragraph
    weaknesses = db.Column(db.Text, nullable=True)     # Detailed list or paragraph
    suggestions = db.Column(db.Text, nullable=True)    # Improvement tips
    skills = db.Column(db.Text, nullable=True)         # Identified skills (stored as text or comma-separated)
    missing_keywords = db.Column(db.Text, nullable=True) # Recommended terms to insert
    formatting_feedback = db.Column(db.Text, nullable=True) # Analysis of style/structure
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ats_score': self.ats_score,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'suggestions': self.suggestions,
            'skills': self.skills,
            'missing_keywords': self.missing_keywords,
            'formatting_feedback': self.formatting_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
