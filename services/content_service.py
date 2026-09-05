from models import db
from models.content import Page, Announcement, Setting


def get_page(slug):
    return Page.query.filter_by(slug=slug, status='published').first()


def get_all_pages():
    return Page.query.order_by(Page.title).all()


def save_page(slug, title, content, status='draft', user_id=None):
    page = Page.query.filter_by(slug=slug).first()
    if page:
        page.title = title
        page.content = content
        page.status = status
        page.updated_by = user_id
    else:
        page = Page(slug=slug, title=title, content=content, status=status, updated_by=user_id)
        db.session.add(page)
    db.session.commit()
    return page


def get_published_announcements(limit=None):
    q = Announcement.query.filter_by(is_published=True).order_by(Announcement.publish_date.desc())
    if limit:
        q = q.limit(limit)
    return q.all()


def get_all_settings():
    return {s.setting_key: s.setting_value for s in Setting.query.all()}


def save_settings(data):
    for key, value in data.items():
        Setting.set(key, value)
