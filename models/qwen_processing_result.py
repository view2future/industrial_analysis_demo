from datetime import datetime
from app import db


class QwenProcessingResult(db.Model):
    """Store Qwen text processing results and history"""
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)  # Original input text
    processed_text = db.Column(db.Text)  # Processed/modified text
    summary = db.Column(db.Text)  # Summary of the content
    key_points = db.Column(db.JSON)  # Key points extracted as JSON array
    sentiment = db.Column(db.String(50))  # Sentiment (positive, negative, neutral)
    sentiment_score = db.Column(db.Float, default=0.0)  # Sentiment score (-1 to 1)
    entities = db.Column(db.JSON)  # Extracted entities as JSON array
    topics = db.Column(db.JSON)  # Identified topics as JSON array
    suggestions = db.Column(db.JSON)  # Suggestions as JSON array
    processing_type = db.Column(db.String(100), default='analysis')  # Type of processing
    metadata = db.Column(db.JSON)  # Additional metadata as JSON
    status = db.Column(db.String(50), default='completed')  # Status: pending, processing, completed, failed
    error_message = db.Column(db.Text)  # Error details if processing failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'original_text': self.original_text,
            'processed_text': self.processed_text,
            'summary': self.summary,
            'key_points': self.key_points or [],
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'entities': self.entities or [],
            'topics': self.topics or [],
            'suggestions': self.suggestions or [],
            'processing_type': self.processing_type,
            'metadata': self.metadata or {},
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }