from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vocabulary(db.Model):
    """Store vocabulary words with their definitions and examples"""
    __tablename__ = 'vocabulary'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text)
    translation = db.Column(db.String(200))  # Translation to native language
    ipa_us = db.Column(db.String(100))  # US pronunciation (IPA)
    ipa_uk = db.Column(db.String(100))  # UK pronunciation (IPA)
    audio_us = db.Column(db.String(500))  # US audio URL
    audio_uk = db.Column(db.String(500))  # UK audio URL
    status = db.Column(db.String(20), default='learning')  # learning, learned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    learned_at = db.Column(db.DateTime)  # When marked as learned
    times_practiced = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'definition': self.definition,
            'example': self.example,
            'translation': self.translation,
            'ipa_us': self.ipa_us,
            'ipa_uk': self.ipa_uk,
            'audio_us': self.audio_us,
            'audio_uk': self.audio_uk,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'learned_at': self.learned_at.isoformat() if self.learned_at else None,
            'times_practiced': self.times_practiced
        }

class LearningHistory(db.Model):
    """Track learning activities and statistics"""
    __tablename__ = 'learning_history'
    
    id = db.Column(db.Integer, primary_key=True)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50))  # flashcard, fill_blank, review
    correct = db.Column(db.Boolean)
    practiced_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vocabulary = db.relationship('Vocabulary', backref=db.backref('history', cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'vocabulary_id': self.vocabulary_id,
            'activity_type': self.activity_type,
            'correct': self.correct,
            'practiced_at': self.practiced_at.isoformat() if self.practiced_at else None
        }
