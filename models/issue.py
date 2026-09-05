from models import db


class Volume(db.Model):
    __tablename__ = 'volumes'

    id = db.Column(db.Integer, primary_key=True)
    volume_number = db.Column(db.Integer, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    issues = db.relationship('Issue', backref='volume', cascade='all, delete-orphan', order_by='Issue.issue_number')


class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    volume_id = db.Column(db.Integer, db.ForeignKey('volumes.id', ondelete='CASCADE'), nullable=False)
    issue_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, nullable=False, default=False)
    cover_path = db.Column(db.String(500))

    @property
    def display_name(self):
        return f"Volume {self.volume.volume_number}, Issue {self.issue_number} ({self.volume.year})"
