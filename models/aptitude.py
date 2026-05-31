from datetime import datetime
from models.database import db

class AptitudeResult(db.Model):
    __tablename__ = 'aptitude_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(100), nullable=False) # 'Quantitative Aptitude', 'Logical Reasoning', 'Verbal Ability'
    score = db.Column(db.Integer, nullable=False)        # Correct answers
    total_questions = db.Column(db.Integer, nullable=False) # Total questions in test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': round((self.score / self.total_questions) * 100) if self.total_questions > 0 else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
