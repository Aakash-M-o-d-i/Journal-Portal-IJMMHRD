from models import db


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='SET NULL'), unique=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='SET NULL'))
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text)
    keywords = db.Column(db.String(500))
    article_id = db.Column(db.String(50), unique=True)
    doi = db.Column(db.String(255), unique=True)
    doi_status = db.Column(db.Enum('pending', 'generated', 'registered'), default='pending')
    page_start = db.Column(db.Integer)
    page_end = db.Column(db.Integer)
    pdf_path = db.Column(db.String(500))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    authors = db.relationship('ArticleAuthor', backref='article', cascade='all, delete-orphan', order_by='ArticleAuthor.author_order')
    issue = db.relationship('Issue', backref='articles')

    @property
    def pages_display(self):
        if self.page_start and self.page_end:
            return f"{self.page_start}-{self.page_end}"
        return ''

    @property
    def doi_url(self):
        if not self.doi:
            return ''
        try:
            from flask import url_for
            return url_for('public.resolve_doi', doi=self.doi, _external=True)
        except Exception:
            return f"/doi/{self.doi}"

    @property
    def external_doi_url(self):
        return f"https://doi.org/{self.doi}" if self.doi else ''


class ArticleAuthor(db.Model):
    __tablename__ = 'article_authors'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    affiliation = db.Column(db.String(500))
    author_order = db.Column(db.Integer, nullable=False, default=1)
