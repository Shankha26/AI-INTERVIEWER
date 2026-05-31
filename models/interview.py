from datetime import datetime
from models.database import db

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    domain = db.Column(db.String(100), nullable=False) # HR, Python, C++, etc.
    score = db.Column(db.Integer, nullable=False)      # Average out of 100
    feedback = db.Column(db.Text, nullable=True)       # Full feedback report
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    voice_interviews = db.relationship('VoiceInterview', backref='session', cascade='all, delete-orphan', lazy=True)
    recordings = db.relationship('Recording', backref='session', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'domain': self.domain,
            'score': self.score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class VoiceInterview(db.Model):
    __tablename__ = 'voice_interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    transcript = db.Column(db.Text, nullable=True)      # Speech converted to text
    audio_path = db.Column(db.String(255), nullable=True)
    video_path = db.Column(db.String(255), nullable=True)
    
    # Granular communication metrics (0 to 100)
    fluency_score = db.Column(db.Integer, nullable=True)
    confidence_score = db.Column(db.Integer, nullable=True)
    technical_accuracy_score = db.Column(db.Integer, nullable=True)
    grammar_score = db.Column(db.Integer, nullable=True)
    relevance_score = db.Column(db.Integer, nullable=True)
    
    feedback = db.Column(db.Text, nullable=True)        # Detailed evaluation report
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'question_text': self.question_text,
            'transcript': self.transcript,
            'audio_path': self.audio_path,
            'video_path': self.video_path,
            'fluency_score': self.fluency_score,
            'confidence_score': self.confidence_score,
            'technical_accuracy_score': self.technical_accuracy_score,
            'grammar_score': self.grammar_score,
            'relevance_score': self.relevance_score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Recording(db.Model):
    __tablename__ = 'recordings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False) # 'audio' or 'video'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
