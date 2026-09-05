from datetime import datetime
from models import db
from models.article import Article, ArticleAuthor
from models.submission import Submission


def create_article_from_submission(submission_id, issue_id=None, page_start=None, page_end=None, pdf_path=None):
    """Create an article record from an accepted or published submission."""
    import os
    import shutil
    from flask import current_app

    sub = Submission.query.get_or_404(submission_id)
    if sub.status not in ('accepted', 'published'):
        raise ValueError("Submission must be accepted or published before creating article.")

    existing = Article.query.filter_by(submission_id=submission_id).first()
    if existing:
        return existing

    # Automatically pick previous uploaded file if pdf_path is not explicitly passed
    temp_dst_path = None
    if not pdf_path and sub.files:
        latest_file = sub.files[0]  # ordered by version desc
        upload_folder = current_app.config['UPLOAD_FOLDER']

        src_path = latest_file.file_path
        if not os.path.isabs(src_path):
            src_path = os.path.join(upload_folder, src_path)

        if os.path.exists(src_path):
            ext = os.path.splitext(latest_file.file_name)[1] or '.pdf'
            pdf_folder = os.path.join(upload_folder, 'articles')
            os.makedirs(pdf_folder, exist_ok=True)

            temp_name = f"sub_{sub.id}_{latest_file.file_name}"
            temp_dst_path = os.path.join(pdf_folder, temp_name)
            try:
                shutil.copy2(src_path, temp_dst_path)
                pdf_path = f"articles/{temp_name}"
            except Exception:
                pdf_path = f"submissions/{sub.paper_id}/{latest_file.file_name}"
        else:
            pdf_path = f"submissions/{sub.paper_id}/{latest_file.file_name}"

    article = Article(
        submission_id=sub.id,
        issue_id=issue_id,
        title=sub.title,
        abstract=sub.abstract,
        keywords=sub.keywords,
        page_start=page_start,
        page_end=page_end,
        pdf_path=pdf_path,
        published_at=datetime.now()
    )
    db.session.add(article)
    db.session.flush()

    # Generate article ID
    article.article_id = f"IJMMHRD-A-{article.id:05d}"

    # Rename temp PDF to match article.article_id if copied
    if temp_dst_path and os.path.exists(temp_dst_path):
        ext = os.path.splitext(sub.files[0].file_name)[1] or '.pdf'
        final_name = f"{article.article_id}{ext}"
        final_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'articles', final_name)
        try:
            os.rename(temp_dst_path, final_path)
            article.pdf_path = f"articles/{final_name}"
        except Exception:
            pass

    # Copy authors from submission
    for sa in sub.authors:
        db.session.add(ArticleAuthor(
            article_id=article.id,
            full_name=sa.full_name,
            email=sa.email,
            affiliation=sa.affiliation,
            author_order=sa.author_order
        ))

    sub.status = 'published'
    db.session.commit()

    # Auto generate DOI
    try:
        from services import doi_service
        if not article.doi:
            doi_service.generate_doi(article.id)
    except Exception:
        pass

    return article


def create_article_direct(title, abstract=None, keywords=None, issue_id=None, page_start=None, page_end=None, pdf_path=None, authors_data=None, auto_publish=True):
    """Create an article record directly by admin without requiring a manuscript submission."""
    if not title or not title.strip():
        raise ValueError("Article title is required.")

    article = Article(
        issue_id=issue_id,
        title=title.strip(),
        abstract=abstract.strip() if abstract else None,
        keywords=keywords.strip() if keywords else None,
        page_start=page_start,
        page_end=page_end,
        pdf_path=pdf_path,
        published_at=datetime.now() if auto_publish else None
    )
    db.session.add(article)
    db.session.flush()

    # Generate article ID
    article.article_id = f"IJMMHRD-A-{article.id:05d}"

    # Add authors
    if authors_data:
        for idx, a in enumerate(authors_data, 1):
            name = a.get('full_name', '').strip()
            if name:
                db.session.add(ArticleAuthor(
                    article_id=article.id,
                    full_name=name,
                    email=a.get('email', '').strip() or None,
                    affiliation=a.get('affiliation', '').strip() or None,
                    author_order=idx
                ))

    db.session.commit()

    # Auto generate DOI
    try:
        from services import doi_service
        doi_service.generate_doi(article.id)
    except Exception:
        pass

    return article


def publish_article(article_id):
    """Mark article as published with timestamp."""
    article = Article.query.get_or_404(article_id)
    article.published_at = datetime.now()
    if article.submission:
        article.submission.status = 'published'
    db.session.commit()
    return article


def get_published_articles(issue_id=None, limit=None):
    q = Article.query.filter(Article.published_at.isnot(None))
    if issue_id:
        q = q.filter_by(issue_id=issue_id)
    q = q.order_by(Article.published_at.desc())
    if limit:
        q = q.limit(limit)
    return q.all()


def search_articles(query_str):
    """Search articles by title, keywords, author name, or article ID."""
    if not query_str:
        return []
    like = f"%{query_str}%"
    articles = Article.query.filter(
        Article.published_at.isnot(None),
        db.or_(
            Article.title.ilike(like),
            Article.keywords.ilike(like),
            Article.abstract.ilike(like),
            Article.article_id.ilike(like),
            Article.doi.ilike(like),
            Article.id.in_(
                db.session.query(ArticleAuthor.article_id).filter(
                    ArticleAuthor.full_name.ilike(like)
                )
            )
        )
    ).order_by(Article.published_at.desc()).limit(50).all()
    return articles
