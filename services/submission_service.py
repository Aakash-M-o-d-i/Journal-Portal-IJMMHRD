import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db
from models.submission import Submission, SubmissionAuthor, SubmissionFile

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odt', 'rtf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_paper_id():
    """Generate unique paper ID like IJMMHRD-2026-XXXX."""
    year = datetime.now().year
    while True:
        seq = uuid.uuid4().hex[:6].upper()
        pid = f"IJMMHRD-{year}-{seq}"
        if not Submission.query.filter_by(paper_id=pid).first():
            return pid


def create_submission(form_data, file, upload_folder):
    """Create a new submission from form data and manuscript file."""
    if not file or not allowed_file(file.filename):
        raise ValueError("Please upload a valid manuscript file (PDF, DOC, DOCX).")

    paper_id = generate_paper_id()

    sub = Submission(
        paper_id=paper_id,
        title=form_data['title'],
        abstract=form_data.get('abstract', ''),
        keywords=form_data.get('keywords', ''),
        research_area=form_data.get('research_area', ''),
        submitted_by_name=form_data['author_name'],
        submitted_by_email=form_data['author_email'],
    )
    db.session.add(sub)
    db.session.flush()  # get sub.id

    # Corresponding author
    ca = SubmissionAuthor(
        submission_id=sub.id,
        full_name=form_data['author_name'],
        email=form_data['author_email'],
        affiliation=form_data.get('author_affiliation', ''),
        is_corresponding=True,
        author_order=1
    )
    db.session.add(ca)

    # Co-authors
    co_names = form_data.getlist('co_author_name') if hasattr(form_data, 'getlist') else []
    co_emails = form_data.getlist('co_author_email') if hasattr(form_data, 'getlist') else []
    co_affiliations = form_data.getlist('co_author_affiliation') if hasattr(form_data, 'getlist') else []
    for i, name in enumerate(co_names):
        if name.strip():
            db.session.add(SubmissionAuthor(
                submission_id=sub.id,
                full_name=name.strip(),
                email=co_emails[i] if i < len(co_emails) else '',
                affiliation=co_affiliations[i] if i < len(co_affiliations) else '',
                author_order=i + 2
            ))

    # Save file
    sub_folder = os.path.join(upload_folder, 'submissions', paper_id)
    os.makedirs(sub_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(sub_folder, filename)
    file.save(file_path)

    sf = SubmissionFile(
        submission_id=sub.id,
        file_path=file_path,
        file_name=filename,
        file_type='manuscript',
        version=1
    )
    db.session.add(sf)
    db.session.commit()
    return sub


def upload_revision(submission, file, upload_folder):
    """Upload a revision for a submission that's in 'revision_required' status."""
    if submission.status != 'revision_required':
        raise ValueError("Revision upload is only allowed when revision is requested.")
    if not file or not allowed_file(file.filename):
        raise ValueError("Please upload a valid manuscript file.")

    current_max = max((f.version for f in submission.files), default=0)
    new_version = current_max + 1

    sub_folder = os.path.join(upload_folder, 'submissions', submission.paper_id)
    os.makedirs(sub_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    versioned_name = f"v{new_version}_{filename}"
    file_path = os.path.join(sub_folder, versioned_name)
    file.save(file_path)

    sf = SubmissionFile(
        submission_id=submission.id,
        file_path=file_path,
        file_name=versioned_name,
        file_type='revision',
        version=new_version
    )
    db.session.add(sf)
    submission.status = 'revision_submitted'
    submission.updated_at = datetime.now()
    db.session.commit()
    return sf


def update_status(submission, new_status, editor_notes=None):
    """Transition submission status with validation."""
    if not submission.can_transition_to(new_status):
        raise ValueError(f"Cannot move from '{submission.status}' to '{new_status}'.")
    submission.status = new_status
    if editor_notes:
        submission.editor_notes = editor_notes
    if new_status in ('accepted', 'rejected', 'published'):
        submission.decided_at = datetime.now()
    db.session.commit()


def get_author_submissions(email):
    """Get all submissions for an author email."""
    return Submission.query.filter_by(submitted_by_email=email).order_by(Submission.submitted_at.desc()).all()


def get_submission_by_paper_id(paper_id, email=None):
    """Get a submission by paper ID, optionally verifying author email."""
    q = Submission.query.filter_by(paper_id=paper_id)
    if email:
        q = q.filter_by(submitted_by_email=email)
    return q.first()
