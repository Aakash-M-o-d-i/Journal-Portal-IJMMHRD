import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from models import db
from models.submission import Submission
from models.article import Article
from models.issue import Volume, Issue
from models.content import Page, Announcement, EditorialBoard, ResearchArea, ContactMessage, Setting
from services import submission_service, article_service, content_service

public = Blueprint('public', __name__)


@public.route('/')
def home():
    settings = content_service.get_all_settings()
    intro = content_service.get_page('home-intro')
    latest_articles = article_service.get_published_articles(limit=6)
    areas = ResearchArea.query.filter_by(is_active=True).order_by(ResearchArea.display_order).all()
    announcements = content_service.get_published_announcements(limit=3)
    current_issue = Issue.query.filter_by(is_current=True).first()
    # Stats
    total_articles = Article.query.filter(Article.published_at.isnot(None)).count()
    total_submissions = Submission.query.count()
    total_areas = ResearchArea.query.filter_by(is_active=True).count()
    total_volumes = Volume.query.count()
    return render_template('public/home.html',
                           settings=settings, intro=intro,
                           latest_articles=latest_articles, areas=areas,
                           announcements=announcements, current_issue=current_issue,
                           total_articles=total_articles, total_submissions=total_submissions,
                           total_areas=total_areas, total_volumes=total_volumes)


@public.route('/about')
def about():
    page = content_service.get_page('about')
    scope = content_service.get_page('aim-scope')
    return render_template('public/about.html', page=page, scope=scope)


@public.route('/editorial-board')
def editorial_board():
    members = EditorialBoard.query.filter_by(is_active=True).order_by(EditorialBoard.display_order).all()
    return render_template('public/editorial_board.html', members=members)


@public.route('/guidelines')
def guidelines():
    page = content_service.get_page('author-guidelines')
    return render_template('public/static_page.html', page=page, title='Author Guidelines')


@public.route('/paper-format')
def paper_format():
    page = content_service.get_page('paper-format')
    return render_template('public/static_page.html', page=page, title='Paper Format')


@public.route('/how-to-publish')
def how_to_publish():
    page = content_service.get_page('how-to-publish')
    return render_template('public/static_page.html', page=page, title='How to Publish')


@public.route('/charges')
def charges():
    page = content_service.get_page('processing-charges')
    return render_template('public/static_page.html', page=page, title='Processing Charges')


@public.route('/research-areas')
def research_areas():
    areas = ResearchArea.query.filter_by(is_active=True).order_by(ResearchArea.display_order).all()
    return render_template('public/research_areas.html', areas=areas)


@public.route('/journal/<slug>')
@public.route('/research-area/<slug>')
@public.route('/<slug>-journals')
@public.route('/<slug>-journal')
def discipline_detail(slug):
    areas = ResearchArea.query.filter_by(is_active=True).order_by(ResearchArea.display_order).all()
    target_area = None

    clean_slug = slug.lower().replace('-journals', '').replace('-journal', '').strip()

    for area in areas:
        if area.slug == clean_slug or area.slug.replace('-and-', '-') == clean_slug.replace('-and-', '-'):
            target_area = area
            break

    if not target_area:
        for area in areas:
            if clean_slug.replace('-', ' ') in area.name.lower():
                target_area = area
                break

    if not target_area and areas:
        target_area = areas[0]

    matching_articles = []
    if target_area:
        like_pattern = f"%{target_area.name}%"
        matching_articles = Article.query.filter(
            Article.published_at.isnot(None),
            db.or_(
                Article.title.ilike(like_pattern),
                Article.keywords.ilike(like_pattern),
                Article.abstract.ilike(like_pattern)
            )
        ).order_by(Article.published_at.desc()).limit(20).all()

        if not matching_articles:
            matching_articles = article_service.get_published_articles(limit=6)

    return render_template(
        'public/discipline_detail.html',
        area=target_area,
        articles=matching_articles,
        all_areas=areas
    )



@public.route('/submit', methods=['GET', 'POST'])
def submit_paper():
    areas = ResearchArea.query.filter_by(is_active=True).order_by(ResearchArea.display_order).all()
    if request.method == 'POST':
        try:
            file = request.files.get('manuscript')
            sub = submission_service.create_submission(
                request.form, file, current_app.config['UPLOAD_FOLDER']
            )
            flash(f'Paper submitted successfully! Your Paper ID is: {sub.paper_id}. Please save this for tracking.', 'success')
            return redirect(url_for('public.submit_success', paper_id=sub.paper_id))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('public/submit.html', areas=areas)


@public.route('/submit/success/<paper_id>')
def submit_success(paper_id):
    sub = Submission.query.filter_by(paper_id=paper_id).first_or_404()
    return render_template('public/submit_success.html', submission=sub)


@public.route('/track', methods=['GET', 'POST'])
def track_paper():
    submission = None
    if request.method == 'POST':
        paper_id = request.form.get('paper_id', '').strip()
        email = request.form.get('email', '').strip()
        if paper_id and email:
            submission = submission_service.get_submission_by_paper_id(paper_id, email)
            if not submission:
                flash('No submission found with that Paper ID and email combination.', 'error')
        else:
            flash('Please enter both Paper ID and email.', 'error')
    return render_template('public/track.html', submission=submission)


@public.route('/archives')
def archives():
    volumes = Volume.query.order_by(Volume.year.desc()).all()
    return render_template('public/archives.html', volumes=volumes)


@public.route('/archives/<int:volume_id>')
def archive_volume(volume_id):
    volume = Volume.query.get_or_404(volume_id)
    return render_template('public/archive_volume.html', volume=volume)


@public.route('/archives/<int:volume_id>/<int:issue_id>')
def archive_issue(volume_id, issue_id):
    issue = Issue.query.get_or_404(issue_id)
    articles = Article.query.filter_by(issue_id=issue_id).filter(
        Article.published_at.isnot(None)
    ).order_by(Article.page_start).all()
    return render_template('public/archive_issue.html', issue=issue, articles=articles)


@public.route('/search')
def search():
    q = request.args.get('q', '').strip()[:200]  # Cap at 200 chars to prevent abuse
    results = article_service.search_articles(q) if q else []
    return render_template('public/search.html', query=q, results=results)


@public.route('/article/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    if not article.published_at:
        return render_template('errors/404.html'), 404
    return render_template('public/article.html', article=article)


@public.route('/doi/<path:doi>')
@public.route('/10.5281/<path:suffix>')
def resolve_doi(doi=None, suffix=None):
    if not doi and suffix:
        doi = f"10.5281/{suffix}"

    if doi:
        doi_clean = doi.strip()
        article = Article.query.filter_by(doi=doi_clean).first()
        if not article:
            article = Article.query.filter(Article.doi.ilike(doi_clean)).first()

        if article:
            return redirect(url_for('public.article_detail', article_id=article.id))

    flash(f'DOI "{doi}" was not found.', 'error')
    return redirect(url_for('public.home'))


@public.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = content_service.get_all_settings()
    if request.method == 'POST':
        msg = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form.get('subject', ''),
            message=request.form['message']
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent. We will get back to you soon.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('public/contact.html', settings=settings)


@public.route('/call-for-papers')
def call_for_papers():
    page = content_service.get_page('call-for-papers')
    return render_template('public/static_page.html', page=page, title='Call for Papers')


@public.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        page = Page.query.filter(Page.slug.ilike(slug)).first_or_404()
    return render_template('public/static_page.html', page=page, title=page.title)


# Allowed extensions for public upload serving (PDFs and docs only)
_UPLOAD_SERVE_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.gif'
}


@public.route('/uploads/<path:filename>')
def uploaded_file(filename):
    import os as _os
    # Security: only serve whitelisted file types
    ext = _os.path.splitext(filename)[1].lower()
    if ext not in _UPLOAD_SERVE_EXTENSIONS:
        return render_template('errors/404.html'), 404
    # Security: prevent path traversal
    safe_root = _os.path.realpath(current_app.config['UPLOAD_FOLDER'])
    requested = _os.path.realpath(_os.path.join(safe_root, filename))
    if not requested.startswith(safe_root + _os.sep):
        return render_template('errors/404.html'), 404
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
