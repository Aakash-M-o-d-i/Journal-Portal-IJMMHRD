import re
from models import db


class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.Enum('draft', 'published'), nullable=False, default='draft')
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    publish_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class EditorialBoard(db.Model):
    __tablename__ = 'editorial_board'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    affiliation = db.Column(db.String(500))
    board_role = db.Column(db.String(100))
    photo_path = db.Column(db.String(500))
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class ResearchArea(db.Model):
    __tablename__ = 'research_areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def slug(self):
        s = self.name.lower().replace('&', 'and')
        return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @staticmethod
    def get(key, default=None):
        s = Setting.query.filter_by(setting_key=key).first()
        return s.setting_value if s else default

    @staticmethod
    def set(key, value):
        from models import db
        s = Setting.query.filter_by(setting_key=key).first()
        if s:
            s.setting_value = value
        else:
            s = Setting(setting_key=key, setting_value=value)
            db.session.add(s)
        db.session.commit()


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
