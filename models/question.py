from datetime import datetime
from models.database import db

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)   # 'C', 'C++', 'Python', 'Java', 'DBMS', 'OS', 'CN', 'DSA', 'HR', 'Quantitative Aptitude', etc.
    category = db.Column(db.String(50), nullable=False)    # 'tech', 'aptitude', 'hr'
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(5), nullable=False)  # 'A', 'B', 'C', 'D'
    difficulty = db.Column(db.String(20), default='medium')   # 'easy', 'medium', 'hard'
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'category': self.category,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_option': self.correct_option,
            'difficulty': self.difficulty,
            'explanation': self.explanation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
