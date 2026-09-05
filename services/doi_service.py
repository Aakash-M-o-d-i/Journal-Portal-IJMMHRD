import secrets
from datetime import datetime
from models import db
from models.article import Article
from models.content import Setting


def generate_doi(article_id, force=False):
    """Generate a unique DOI identifier for an article using cryptographically secure randomness."""
    article = Article.query.get_or_404(article_id)
    if article.doi and article.doi_status != 'pending' and not force:
        raise ValueError("DOI already generated for this article.")

    prefix = Setting.get('doi_prefix', '10.5281')
    if not prefix or 'XXXXX' in prefix:
        prefix = '10.5281'
        Setting.set('doi_prefix', prefix)

    year = datetime.now().year
    # Cryptographically random suffix; retry until unique
    for _ in range(10):
        suffix = secrets.randbelow(900000) + 100000  # 100000–999999
        doi = f"{prefix}/ijmmhrd.{year}.{suffix}"
        if not Article.query.filter_by(doi=doi).first():
            break
    else:
        # Fallback: use article ID for guaranteed uniqueness
        doi = f"{prefix}/ijmmhrd.{year}.{article.id:06d}"

    article.doi = doi
    if not article.doi_status or article.doi_status == 'pending':
        article.doi_status = 'generated'
    db.session.commit()
    return doi


def mark_registered(article_id):
    """Mark a DOI as officially registered."""
    article = Article.query.get_or_404(article_id)
    if not article.doi:
        raise ValueError("No DOI to register.")
    article.doi_status = 'registered'
    db.session.commit()
