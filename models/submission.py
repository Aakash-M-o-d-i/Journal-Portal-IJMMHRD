from models import db


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text)
    keywords = db.Column(db.String(500))
    research_area = db.Column(db.String(255))
    status = db.Column(db.Enum(
        'submitted', 'initial_review', 'reviewer_assigned',
        'under_review', 'revision_required', 'revision_submitted',
        'accepted', 'rejected', 'published'
    ), nullable=False, default='submitted')
    submitted_by_name = db.Column(db.String(255), nullable=False)
    submitted_by_email = db.Column(db.String(255), nullable=False)
    editor_notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())
    decided_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    authors = db.relationship('SubmissionAuthor', backref='submission', cascade='all, delete-orphan', order_by='SubmissionAuthor.author_order')
    files = db.relationship('SubmissionFile', backref='submission', cascade='all, delete-orphan', order_by='SubmissionFile.version.desc()')
    assignments = db.relationship('ReviewAssignment', backref='submission', cascade='all, delete-orphan')
    article = db.relationship('Article', backref='submission', uselist=False)

    # Valid status transitions
    TRANSITIONS = {
        'submitted': ['initial_review', 'under_review', 'accepted', 'rejected', 'published'],
        'initial_review': ['reviewer_assigned', 'under_review', 'accepted', 'rejected', 'published'],
        'reviewer_assigned': ['under_review', 'accepted', 'rejected', 'published'],
        'under_review': ['revision_required', 'accepted', 'rejected', 'published'],
        'revision_required': ['revision_submitted', 'accepted', 'published'],
        'revision_submitted': ['under_review', 'accepted', 'rejected', 'published'],
        'accepted': ['published'],
        'rejected': ['submitted', 'initial_review', 'under_review', 'published'],
        'published': ['accepted', 'under_review'],
    }

    def can_transition_to(self, new_status):
        if new_status == self.status:
            return True
        return new_status in self.TRANSITIONS.get(self.status, [])

    @property
    def status_display(self):
        return self.status.replace('_', ' ').title()


class SubmissionAuthor(db.Model):
    __tablename__ = 'submission_authors'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    affiliation = db.Column(db.String(500))
    is_corresponding = db.Column(db.Boolean, nullable=False, default=False)
    author_order = db.Column(db.Integer, nullable=False, default=1)


class SubmissionFile(db.Model):
    __tablename__ = 'submission_files'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum('manuscript', 'cover_letter', 'revision', 'supplementary'), nullable=False, default='manuscript')
    version = db.Column(db.Integer, nullable=False, default=1)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
