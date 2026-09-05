from models import db


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='audit_entries')

    @staticmethod
    def log(action, entity_type=None, entity_id=None, details=None, user_id=None):
        from models import db
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(entry)
        db.session.commit()
