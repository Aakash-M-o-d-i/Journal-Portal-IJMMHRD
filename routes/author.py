from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.submission import Submission
from services import submission_service

author = Blueprint('author', __name__, url_prefix='/author')


def get_author_session():
    """Check if author is logged in via Paper ID + Email session."""
    return session.get('author_email'), session.get('author_paper_id')


def require_author(f):
    """Decorator to require author session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        email, _ = get_author_session()
        if not email:
            flash('Please log in with your Paper ID and email.', 'error')
            return redirect(url_for('author.login'))
        return f(*args, **kwargs)
    return decorated


@author.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        paper_id = request.form.get('paper_id', '').strip()
        email = request.form.get('email', '').strip()
        if not paper_id or not email:
            flash('Please enter both Paper ID and email.', 'error')
            return render_template('author/login.html')

        sub = submission_service.get_submission_by_paper_id(paper_id, email)
        if not sub:
            flash('No submission found with that Paper ID and email.', 'error')
            return render_template('author/login.html')

        session['author_email'] = email
        session['author_paper_id'] = paper_id
        session['author_name'] = sub.submitted_by_name
        return redirect(url_for('author.dashboard'))
    return render_template('author/login.html')


@author.route('/logout')
def logout():
    session.pop('author_email', None)
    session.pop('author_paper_id', None)
    session.pop('author_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.home'))


@author.route('/dashboard')
@require_author
def dashboard():
    email, _ = get_author_session()
    submissions = submission_service.get_author_submissions(email)
    return render_template('author/dashboard.html', submissions=submissions)


@author.route('/paper/<paper_id>')
@require_author
def paper_detail(paper_id):
    email, _ = get_author_session()
    sub = submission_service.get_submission_by_paper_id(paper_id, email)
    if not sub:
        flash('Paper not found or access denied.', 'error')
        return redirect(url_for('author.dashboard'))
    return render_template('author/paper_detail.html', submission=sub)


@author.route('/paper/<paper_id>/revision', methods=['GET', 'POST'])
@require_author
def upload_revision(paper_id):
    email, _ = get_author_session()
    sub = submission_service.get_submission_by_paper_id(paper_id, email)
    if not sub:
        flash('Paper not found or access denied.', 'error')
        return redirect(url_for('author.dashboard'))

    if sub.status != 'revision_required':
        flash('Revision upload is only available when revision is requested.', 'error')
        return redirect(url_for('author.paper_detail', paper_id=paper_id))

    if request.method == 'POST':
        try:
            file = request.files.get('revision_file')
            submission_service.upload_revision(sub, file, current_app.config['UPLOAD_FOLDER'])
            flash('Revision uploaded successfully.', 'success')
            return redirect(url_for('author.paper_detail', paper_id=paper_id))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('author/revision.html', submission=sub)


@author.route('/profile', methods=['GET', 'POST'])
@require_author
def profile():
    email, _ = get_author_session()
    # For Paper ID + Email auth, profile is read-only from submissions
    submissions = submission_service.get_author_submissions(email)
    if submissions:
        author_info = {
            'name': submissions[0].submitted_by_name,
            'email': email,
            'affiliation': submissions[0].authors[0].affiliation if submissions[0].authors else ''
        }
    else:
        author_info = {'name': '', 'email': email, 'affiliation': ''}
    return render_template('author/profile.html', author_info=author_info)
