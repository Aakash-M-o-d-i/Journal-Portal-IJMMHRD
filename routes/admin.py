import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import bcrypt
from models import db
from models.user import User
from models.submission import Submission
from models.article import Article, ArticleAuthor
from models.review import Reviewer, ReviewAssignment, Review
from models.issue import Volume, Issue
from models.content import Page, Announcement, EditorialBoard, ResearchArea, Setting, ContactMessage
from models.audit import AuditLog
from services import submission_service, review_service, article_service, doi_service, content_service

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin/editor role."""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.is_admin and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            login_user(user)
            AuditLog.log('login', 'user', user.id, user_id=user.id)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('admin/login.html')


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('admin.login'))


# ── Dashboard ─────────────────────────────────────────────────

@admin.route('/')
@admin_required
def dashboard():
    stats = {
        'submissions': Submission.query.count(),
        'pending_submissions': Submission.query.filter(Submission.status.in_(['submitted', 'initial_review'])).count(),
        'under_review': Submission.query.filter_by(status='under_review').count(),
        'accepted': Submission.query.filter_by(status='accepted').count(),
        'published_articles': Article.query.filter(Article.published_at.isnot(None)).count(),
        'pending_reviews': ReviewAssignment.query.filter_by(status='pending').count(),
        'volumes': Volume.query.count(),
        'issues': Issue.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count(),
    }
    recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(5).all()
    recent_articles = Article.query.filter(Article.published_at.isnot(None)).order_by(Article.published_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_submissions=recent_submissions, recent_articles=recent_articles)


# ── Submissions ───────────────────────────────────────────────

@admin.route('/submissions')
@admin_required
def submissions():
    status_filter = request.args.get('status', '')
    q = Submission.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    subs = q.order_by(Submission.submitted_at.desc()).all()
    statuses = ['submitted', 'initial_review', 'reviewer_assigned', 'under_review',
                'revision_required', 'revision_submitted', 'accepted', 'rejected', 'published']
    return render_template('admin/submissions.html', submissions=subs,
                           statuses=statuses, current_status=status_filter)


@admin.route('/submissions/<int:sub_id>')
@admin_required
def submission_detail(sub_id):
    sub = Submission.query.get_or_404(sub_id)
    reviewers = Reviewer.query.filter_by(is_active=True).order_by(Reviewer.full_name).all()
    return render_template('admin/submission_detail.html', submission=sub, reviewers=reviewers)


@admin.route('/submissions/<int:sub_id>/status', methods=['POST'])
@admin_required
def update_status(sub_id):
    sub = Submission.query.get_or_404(sub_id)
    new_status = request.form.get('status')
    notes = request.form.get('editor_notes', '')
    try:
        submission_service.update_status(sub, new_status, notes)
        AuditLog.log('status_change', 'submission', sub.id,
                     f"Status: {new_status}", user_id=current_user.id)
        flash(f'Status updated to {new_status.replace("_", " ").title()}.', 'success')

        if new_status in ('published', 'accepted'):
            existing_art = Article.query.filter_by(submission_id=sub.id).first()
            if existing_art:
                flash('Article for this submission is already created.', 'info')
                return redirect(url_for('admin.article_edit', article_id=existing_art.id))
            else:
                return redirect(url_for('admin.create_article', sub_id=sub.id))
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('admin.submission_detail', sub_id=sub_id))


# ── Reviewers ─────────────────────────────────────────────────

@admin.route('/reviewers')
@admin_required
def reviewers():
    all_reviewers = Reviewer.query.order_by(Reviewer.full_name).all()
    return render_template('admin/reviewers.html', reviewers=all_reviewers)


@admin.route('/reviewers/add', methods=['POST'])
@admin_required
def add_reviewer():
    try:
        review_service.create_reviewer(
            request.form['full_name'],
            request.form['email'],
            request.form.get('specialization', '')
        )
        flash('Reviewer added.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('admin.reviewers'))


@admin.route('/reviewers/<int:rev_id>/toggle', methods=['POST'])
@admin_required
def toggle_reviewer(rev_id):
    r = Reviewer.query.get_or_404(rev_id)
    r.is_active = not r.is_active
    db.session.commit()
    flash(f'Reviewer {"activated" if r.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.reviewers'))


# ── Review Assignment ─────────────────────────────────────────

@admin.route('/submissions/<int:sub_id>/assign', methods=['POST'])
@admin_required
def assign_reviewer(sub_id):
    reviewer_id = request.form.get('reviewer_id', type=int)
    due_date = request.form.get('due_date') or None
    try:
        review_service.assign_reviewer(sub_id, reviewer_id, due_date)
        AuditLog.log('assign_reviewer', 'submission', sub_id, user_id=current_user.id)
        flash('Reviewer assigned.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('admin.submission_detail', sub_id=sub_id))


@admin.route('/reviews/<int:assignment_id>', methods=['GET', 'POST'])
@admin_required
def review_detail(assignment_id):
    assignment = ReviewAssignment.query.get_or_404(assignment_id)
    if request.method == 'POST':
        try:
            review_service.record_review(
                assignment_id,
                request.form['recommendation'],
                request.form.get('rating', type=int),
                request.form.get('comments_to_author', ''),
                request.form.get('confidential_comments', '')
            )
            AuditLog.log('record_review', 'review_assignment', assignment_id, user_id=current_user.id)
            flash('Review recorded.', 'success')
            return redirect(url_for('admin.submission_detail', sub_id=assignment.submission_id))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('admin/review_detail.html', assignment=assignment)


# ── Articles ──────────────────────────────────────────────────

@admin.route('/articles')
@admin_required
def articles():
    all_articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=all_articles)


@admin.route('/articles/new', methods=['GET', 'POST'])
@admin_required
def article_direct_create():
    issues = Issue.query.order_by(Issue.id.desc()).all()
    if request.method == 'POST':
        title = request.form.get('title')
        abstract = request.form.get('abstract')
        keywords = request.form.get('keywords')
        issue_id = request.form.get('issue_id', type=int)
        page_start = request.form.get('page_start', type=int)
        page_end = request.form.get('page_end', type=int)
        auto_publish = request.form.get('auto_publish') == 'on' or request.form.get('auto_publish') == 'true'

        author_names = request.form.getlist('author_name[]') or request.form.getlist('author_name')
        author_emails = request.form.getlist('author_email[]') or request.form.getlist('author_email')
        author_affils = request.form.getlist('author_affiliation[]') or request.form.getlist('author_affiliation')

        authors_data = []
        for i in range(len(author_names)):
            if author_names[i] and author_names[i].strip():
                authors_data.append({
                    'full_name': author_names[i].strip(),
                    'email': author_emails[i].strip() if i < len(author_emails) else None,
                    'affiliation': author_affils[i].strip() if i < len(author_affils) else None,
                })

        pdf = request.files.get('pdf_file')

        try:
            article = article_service.create_article_direct(
                title=title,
                abstract=abstract,
                keywords=keywords,
                issue_id=issue_id,
                page_start=page_start,
                page_end=page_end,
                pdf_path=None,
                authors_data=authors_data,
                auto_publish=auto_publish
            )

            if pdf and pdf.filename:
                pdf_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'articles')
                os.makedirs(pdf_folder, exist_ok=True)
                pdf_name = secure_filename(f"{article.article_id}.pdf")
                full_pdf_path = os.path.join(pdf_folder, pdf_name)
                pdf.save(full_pdf_path)
                article.pdf_path = f"articles/{pdf_name}"
                db.session.commit()

            AuditLog.log('create_article_direct', 'article', article.id, user_id=current_user.id)
            flash(f'Article "{article.title}" created successfully.', 'success')
            return redirect(url_for('admin.article_edit', article_id=article.id))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('admin/article_direct_create.html', issues=issues)



@admin.route('/articles/create/<int:sub_id>', methods=['GET', 'POST'])
@admin_required
def create_article(sub_id):
    sub = Submission.query.get_or_404(sub_id)
    issues = Issue.query.order_by(Issue.id.desc()).all()
    if request.method == 'POST':
        try:
            article = article_service.create_article_from_submission(
                sub_id,
                issue_id=request.form.get('issue_id', type=int),
                page_start=request.form.get('page_start', type=int),
                page_end=request.form.get('page_end', type=int),
            )
            # Handle PDF upload
            pdf = request.files.get('pdf_file')
            if pdf and pdf.filename:
                pdf_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'articles')
                os.makedirs(pdf_folder, exist_ok=True)
                pdf_name = secure_filename(f"{article.article_id}.pdf")
                pdf_path = os.path.join(pdf_folder, pdf_name)
                pdf.save(pdf_path)
                article.pdf_path = f"articles/{pdf_name}"
                db.session.commit()

            AuditLog.log('create_article', 'article', article.id, user_id=current_user.id)
            flash('Article created.', 'success')
            return redirect(url_for('admin.article_edit', article_id=article.id))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('admin/article_create.html', submission=sub, issues=issues)


@admin.route('/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@admin_required
def article_edit(article_id):
    article = Article.query.get_or_404(article_id)
    issues = Issue.query.order_by(Issue.id.desc()).all()
    if request.method == 'POST':
        article.title = request.form.get('title', article.title)
        article.abstract = request.form.get('abstract', article.abstract)
        article.keywords = request.form.get('keywords', article.keywords)
        article.issue_id = request.form.get('issue_id', type=int) or article.issue_id
        article.page_start = request.form.get('page_start', type=int)
        article.page_end = request.form.get('page_end', type=int)
        # PDF upload
        pdf = request.files.get('pdf_file')
        if pdf and pdf.filename:
            pdf_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'articles')
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_name = secure_filename(f"{article.article_id}.pdf")
            pdf_path = os.path.join(pdf_folder, pdf_name)
            pdf.save(pdf_path)
            article.pdf_path = f"articles/{pdf_name}"
        db.session.commit()
        flash('Article updated.', 'success')
        return redirect(url_for('admin.article_edit', article_id=article_id))
    return render_template('admin/article_edit.html', article=article, issues=issues)


@admin.route('/articles/<int:article_id>/publish', methods=['POST'])
@admin_required
def publish_article(article_id):
    article = article_service.publish_article(article_id)
    AuditLog.log('publish_article', 'article', article_id, user_id=current_user.id)
    flash('Article published.', 'success')
    return redirect(url_for('admin.article_edit', article_id=article_id))


# ── DOI Management ────────────────────────────────────────────

@admin.route('/doi')
@admin_required
def doi_management():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/doi_management.html', articles=articles)


@admin.route('/doi/generate/<int:article_id>', methods=['POST'])
@admin_required
def generate_doi(article_id):
    try:
        force = request.form.get('force') == 'true' or request.args.get('force') == 'true'
        doi = doi_service.generate_doi(article_id, force=force)
        AuditLog.log('generate_doi', 'article', article_id, f"DOI: {doi}", user_id=current_user.id)
        flash(f'DOI generated: {doi}', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('admin.doi_management'))



@admin.route('/doi/register/<int:article_id>', methods=['POST'])
@admin_required
def register_doi(article_id):
    try:
        doi_service.mark_registered(article_id)
        flash('DOI marked as registered.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('admin.doi_management'))


# ── Volumes & Issues ──────────────────────────────────────────

@admin.route('/issues')
@admin_required
def issues():
    volumes = Volume.query.order_by(Volume.year.desc()).all()
    return render_template('admin/issues.html', volumes=volumes)


@admin.route('/volumes/add', methods=['POST'])
@admin_required
def add_volume():
    v = Volume(
        volume_number=request.form.get('volume_number', type=int),
        year=request.form.get('year', type=int)
    )
    db.session.add(v)
    db.session.commit()
    flash('Volume added.', 'success')
    return redirect(url_for('admin.issues'))


@admin.route('/volumes/<int:vol_id>/add-issue', methods=['POST'])
@admin_required
def add_issue(vol_id):
    i = Issue(
        volume_id=vol_id,
        issue_number=request.form.get('issue_number', type=int),
        title=request.form.get('title', ''),
        publication_date=request.form.get('publication_date') or None,
    )
    db.session.add(i)
    db.session.commit()
    flash('Issue added.', 'success')
    return redirect(url_for('admin.issues'))


@admin.route('/issues/<int:issue_id>/set-current', methods=['POST'])
@admin_required
def set_current_issue(issue_id):
    Issue.query.update({'is_current': False})
    issue = Issue.query.get_or_404(issue_id)
    issue.is_current = True
    db.session.commit()
    flash('Current issue updated.', 'success')
    return redirect(url_for('admin.issues'))


@admin.route('/volumes/<int:vol_id>/delete', methods=['POST'])
@admin_required
def delete_volume(vol_id):
    vol = Volume.query.get_or_404(vol_id)
    for issue in vol.issues:
        for article in issue.articles:
            article.issue_id = None
    vol_num = vol.volume_number
    vol_yr = vol.year
    db.session.delete(vol)
    db.session.commit()
    AuditLog.log('delete_volume', 'volume', vol_id, user_id=current_user.id)
    flash(f'Volume {vol_num} ({vol_yr}) removed successfully.', 'success')
    return redirect(url_for('admin.issues'))


@admin.route('/issues/<int:issue_id>/delete', methods=['POST'])
@admin_required
def delete_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    iss_num = issue.issue_number
    for article in issue.articles:
        article.issue_id = None
    db.session.delete(issue)
    db.session.commit()
    AuditLog.log('delete_issue', 'issue', issue_id, user_id=current_user.id)
    flash(f'Issue {iss_num} removed successfully.', 'success')
    return redirect(url_for('admin.issues'))


# ── Editorial Board ───────────────────────────────────────────

@admin.route('/editorial-board')
@admin_required
def editorial_board():
    members = EditorialBoard.query.order_by(EditorialBoard.display_order).all()
    return render_template('admin/editorial_board.html', members=members)


@admin.route('/editorial-board/add', methods=['POST'])
@admin_required
def add_board_member():
    m = EditorialBoard(
        full_name=request.form['full_name'],
        title=request.form.get('title', ''),
        affiliation=request.form.get('affiliation', ''),
        board_role=request.form.get('board_role', ''),
        display_order=request.form.get('display_order', 0, type=int)
    )
    db.session.add(m)
    db.session.commit()
    flash('Board member added.', 'success')
    return redirect(url_for('admin.editorial_board'))


@admin.route('/editorial-board/<int:member_id>/toggle', methods=['POST'])
@admin_required
def toggle_board_member(member_id):
    m = EditorialBoard.query.get_or_404(member_id)
    m.is_active = not m.is_active
    db.session.commit()
    flash(f'Member {"activated" if m.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.editorial_board'))


# ── Users ─────────────────────────────────────────────────────

@admin.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    pw = request.form['password']
    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    u = User(
        email=request.form['email'],
        password_hash=hashed,
        full_name=request.form['full_name'],
        role=request.form.get('role', 'author')
    )
    db.session.add(u)
    db.session.commit()
    AuditLog.log('create_user', 'user', u.id, user_id=current_user.id)
    flash('User created.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash('Cannot deactivate yourself.', 'error')
    else:
        u.is_active = not u.is_active
        db.session.commit()
        flash(f'User {"activated" if u.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


# ── Content Management ────────────────────────────────────────

@admin.route('/content')
@admin_required
def content_list():
    pages = content_service.get_all_pages()
    return render_template('admin/content_list.html', pages=pages)


@admin.route('/content/<slug>/edit', methods=['GET', 'POST'])
@admin_required
def content_edit(slug):
    page = Page.query.filter_by(slug=slug).first()
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        status = request.form.get('status', 'draft')
        content_service.save_page(slug, title, content, status, current_user.id)
        AuditLog.log('edit_content', 'page', None, f"Slug: {slug}", user_id=current_user.id)
        flash('Content saved.', 'success')
        return redirect(url_for('admin.content_edit', slug=slug))
    return render_template('admin/content_edit.html', page=page, slug=slug)


@admin.route('/content/new', methods=['GET', 'POST'])
@admin_required
def content_new():
    if request.method == 'POST':
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        status = request.form.get('status', 'draft')
        if Page.query.filter_by(slug=slug).first():
            flash('A page with that slug already exists.', 'error')
        else:
            content_service.save_page(slug, title, content, status, current_user.id)
            flash('Page created.', 'success')
            return redirect(url_for('admin.content_list'))
    return render_template('admin/content_edit.html', page=None, slug='')


# ── Announcements ─────────────────────────────────────────────

@admin.route('/announcements')
@admin_required
def announcements():
    all_ann = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=all_ann, editing_announcement=None)


@admin.route('/announcements/add', methods=['POST'])
@admin_required
def add_announcement():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if not title:
        flash('Title is required for an announcement.', 'error')
        return redirect(url_for('admin.announcements'))

    is_pub = 'is_published' in request.form
    pub_date_str = request.form.get('publish_date', '').strip()
    pub_date = None
    if pub_date_str:
        try:
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d').date()
        except ValueError:
            pub_date = date.today()
    elif is_pub:
        pub_date = date.today()

    a = Announcement(
        title=title,
        content=content,
        is_published=is_pub,
        publish_date=pub_date,
        created_by=current_user.id
    )
    db.session.add(a)
    db.session.commit()
    flash('Announcement created successfully.', 'success')
    return redirect(url_for('admin.announcements'))


@admin.route('/announcements/<int:ann_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_announcement(ann_id):
    a = Announcement.query.get_or_404(ann_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return redirect(url_for('admin.edit_announcement', ann_id=ann_id))
        
        a.title = title
        a.content = request.form.get('content', '').strip()
        a.is_published = 'is_published' in request.form
        
        pub_date_str = request.form.get('publish_date', '').strip()
        if pub_date_str:
            try:
                a.publish_date = datetime.strptime(pub_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        elif a.is_published and not a.publish_date:
            a.publish_date = date.today()

        db.session.commit()
        flash('Announcement updated successfully.', 'success')
        return redirect(url_for('admin.announcements'))

    all_ann = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=all_ann, editing_announcement=a)


@admin.route('/announcements/<int:ann_id>/toggle', methods=['POST'])
@admin_required
def toggle_announcement(ann_id):
    a = Announcement.query.get_or_404(ann_id)
    a.is_published = not a.is_published
    if a.is_published and not a.publish_date:
        a.publish_date = date.today()
    db.session.commit()
    flash(f'Announcement {"published" if a.is_published else "unpublished"}.', 'success')
    return redirect(url_for('admin.announcements'))


@admin.route('/announcements/<int:ann_id>/delete', methods=['POST'])
@admin_required
def delete_announcement(ann_id):
    a = Announcement.query.get_or_404(ann_id)
    db.session.delete(a)
    db.session.commit()
    flash('Announcement deleted successfully.', 'success')
    return redirect(url_for('admin.announcements'))


# ── Settings ──────────────────────────────────────────────────

@admin.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        data = {}
        for key in ['journal_name', 'journal_abbr', 'journal_issn', 'journal_email',
                     'journal_url', 'doi_prefix', 'publication_frequency',
                     'footer_text', 'contact_address', 'contact_phone', 'contact_email']:
            val = request.form.get(key)
            if val is not None:
                data[key] = val
        content_service.save_settings(data)
        AuditLog.log('update_settings', user_id=current_user.id)
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.settings'))
    all_settings = content_service.get_all_settings()
    return render_template('admin/settings.html', settings=all_settings)


# ── Messages ──────────────────────────────────────────────────

@admin.route('/messages')
@admin_required
def messages():
    all_msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=all_msgs)


@admin.route('/messages/<int:msg_id>/read', methods=['POST'])
@admin_required
def mark_read(msg_id):
    m = ContactMessage.query.get_or_404(msg_id)
    m.is_read = True
    db.session.commit()
    return redirect(url_for('admin.messages'))
