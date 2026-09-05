from models import db


class Reviewer(db.Model):
    __tablename__ = 'reviewers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    specialization = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    assignments = db.relationship('ReviewAssignment', backref='reviewer', cascade='all, delete-orphan')


class ReviewAssignment(db.Model):
    __tablename__ = 'review_assignments'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewers.id', ondelete='CASCADE'), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    due_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'completed', 'overdue', 'cancelled'), nullable=False, default='pending')

    review = db.relationship('Review', backref='assignment', uselist=False)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('review_assignments.id', ondelete='CASCADE'), unique=True, nullable=False)
    recommendation = db.Column(db.Enum('accept', 'minor_revision', 'major_revision', 'reject'), nullable=False)
    rating = db.Column(db.Integer)
    comments_to_author = db.Column(db.Text)
    confidential_comments = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, server_default=db.func.now())
