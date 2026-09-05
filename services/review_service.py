from datetime import datetime, date
from models import db
from models.review import Reviewer, ReviewAssignment, Review


def create_reviewer(full_name, email, specialization=None):
    r = Reviewer(full_name=full_name, email=email, specialization=specialization)
    db.session.add(r)
    db.session.commit()
    return r


def assign_reviewer(submission_id, reviewer_id, due_date=None):
    existing = ReviewAssignment.query.filter_by(
        submission_id=submission_id, reviewer_id=reviewer_id
    ).filter(ReviewAssignment.status.in_(['pending', 'completed'])).first()
    if existing:
        raise ValueError("This reviewer is already assigned to this submission.")
    a = ReviewAssignment(
        submission_id=submission_id,
        reviewer_id=reviewer_id,
        due_date=due_date
    )
    db.session.add(a)
    db.session.commit()
    return a


def record_review(assignment_id, recommendation, rating=None, comments='', confidential=''):
    assignment = ReviewAssignment.query.get_or_404(assignment_id)
    if assignment.status == 'completed':
        raise ValueError("Review already submitted for this assignment.")
    review = Review(
        assignment_id=assignment_id,
        recommendation=recommendation,
        rating=rating,
        comments_to_author=comments,
        confidential_comments=confidential
    )
    assignment.status = 'completed'
    db.session.add(review)
    db.session.commit()
    return review


def get_pending_reviews():
    return ReviewAssignment.query.filter_by(status='pending').all()


def get_overdue_reviews():
    today = date.today()
    overdue = ReviewAssignment.query.filter(
        ReviewAssignment.status == 'pending',
        ReviewAssignment.due_date != None,
        ReviewAssignment.due_date < today
    ).all()
    # Update status
    for a in overdue:
        a.status = 'overdue'
    if overdue:
        db.session.commit()
    return overdue
