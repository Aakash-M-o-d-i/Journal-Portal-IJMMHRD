# IJMMHRD Journal Portal — Production Guide
**International Journal of Multidisciplinary Modern Research and Development**
> ESTD: 2018 | ISSN: 2321-8622 | UGC Approved Serial No. 64537

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Environment Variables](#4-environment-variables)
5. [Database Setup](#5-database-setup)
6. [Admin Credentials](#6-admin-credentials)
7. [All API Endpoints](#7-all-api-endpoints)
8. [Frontend Pages](#8-frontend-pages)
9. [Bug Fixes Applied](#9-bug-fixes-applied)
10. [Production Checklist](#10-production-checklist)
11. [MySQL Migration (Production)](#11-mysql-migration-production)
12. [Deployment on LAMPP/cPanel](#12-deployment-on-lamppcpanel)

---

## 1. System Overview

IJMMHRD is a full-stack Flask-based academic journal management system. It supports:

- **Public portal** — homepage, article browsing, archives, research area pages, search
- **Paper submission** — multi-author submission form with file upload
- **Paper tracking** — authors track submission status via Paper ID + email
- **Author portal** — login with Paper ID, revision upload, profile view
- **Admin panel** — full CRUD for submissions, articles, volumes/issues, announcements, CMS pages, editorial board, reviewers, users, DOI management, settings, messages

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Framework | Flask 3.0 |
| ORM | Flask-SQLAlchemy 3.1 |
| Auth | Flask-Login 0.6 + bcrypt 4.0 |
| CSRF | Flask-WTF 1.2 |
| Database (Dev) | SQLite (auto-configured) |
| Database (Prod) | MySQL 8+ via PyMySQL |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| File Uploads | Werkzeug `secure_filename` |
| Env Config | python-dotenv |

---

## 3. Project Structure

```
new_Simple_LB/
├── app.py                  # Flask application factory
├── config.py               # Config class (reads .env)
├── init_db.py              # DB initialization + seed script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── passenger_wsgi.py       # WSGI entry point for cPanel
├── ijmmhrd.db              # SQLite DB (dev only)
│
├── models/
│   ├── __init__.py         # db = SQLAlchemy()
│   ├── user.py             # User model (admin/editor/author)
│   ├── submission.py       # Submission, SubmissionAuthor, SubmissionFile
│   ├── article.py          # Article, ArticleAuthor
│   ├── review.py           # Reviewer, ReviewAssignment, Review
│   ├── issue.py            # Volume, Issue
│   ├── content.py          # Page, Announcement, EditorialBoard, ResearchArea, Setting, ContactMessage
│   └── audit.py            # AuditLog
│
├── routes/
│   ├── public.py           # Public-facing routes (/)
│   ├── admin.py            # Admin panel routes (/admin/*)
│   └── author.py           # Author portal routes (/author/*)
│
├── services/
│   ├── article_service.py  # Article CRUD, publish, search
│   ├── submission_service.py # Submission create, status transition
│   ├── review_service.py   # Reviewer management, review recording
│   ├── content_service.py  # CMS pages, announcements, settings
│   └── doi_service.py      # DOI generation and registration
│
├── templates/
│   ├── base.html           # Public base (navbar, footer)
│   ├── public/             # Public-facing templates
│   ├── admin/              # Admin panel templates
│   │   └── base_admin.html # Admin base (sidebar nav)
│   ├── author/             # Author portal templates
│   ├── components/         # Shared Jinja2 macros
│   └── errors/             # 404, 500 pages
│
├── static/
│   ├── css/style.css       # Full design system
│   ├── js/app.js           # Frontend JS (nav, rich editor, etc.)
│   └── images/logo.png     # Journal logo
│
└── uploads/                # User-uploaded files (not in git)
    ├── submissions/        # Manuscript files (by Paper ID)
    └── articles/           # Published article PDFs
```

---

## 4. Environment Variables

File: `.env` (project root)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-this-to-a-random-secret-key-in-production` | **MUST change in production** — Flask session signing key |
| `USE_SQLITE` | `true` | Set `false` to use MySQL in production |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_USER` | `root` | MySQL username |
| `DB_PASS` | _(empty)_ | MySQL password |
| `DB_NAME` | `ijmmhrd` | MySQL database name |
| `UPLOAD_FOLDER` | `uploads` | Directory for uploaded files (relative to project root) |
| `MAX_CONTENT_LENGTH` | `16777216` | Max upload size in bytes (16 MB default) |

### Example Production `.env`
```env
SECRET_KEY=a-very-long-random-string-min-32-chars
USE_SQLITE=false
DB_HOST=localhost
DB_USER=ijmmhrd_db_user
DB_PASS=strongpassword
DB_NAME=ijmmhrd
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

> ⚠️ **Security**: Never commit `.env` to version control. The `.gitignore` already excludes it.

---

## 5. Database Setup

### Development (SQLite — zero config)
```bash
cd /opt/lampp/htdocs/new_Simple_LB
python3 init_db.py
```
This creates `ijmmhrd.db` and seeds all default data.

### Production (MySQL)
1. Create the database and user in MySQL:
```sql
CREATE DATABASE ijmmhrd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ijmmhrd_user'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON ijmmhrd.* TO 'ijmmhrd_user'@'localhost';
FLUSH PRIVILEGES;
```
2. Update `.env` with the MySQL credentials and `USE_SQLITE=false`
3. Run the init script:
```bash
python3 init_db.py
```

### Seeded Data by `init_db.py`
- 1 default admin user (`admin@ijmmhrd.com`)
- 13 journal settings (name, ISSN, email, DOI prefix, etc.)
- 8 default CMS pages (About, Aim & Scope, Guidelines, etc.)
- 15 research areas (Computer Science, Management, etc.)
- 4 sample volumes (2023–2026) with 4 issues each

---

## 6. Admin Credentials

### Default Admin Account
| Field | Value |
|-------|-------|
| URL | `/admin/login` |
| Email | `admin@ijmmhrd.com` |
| Password | `admin123` |
| Role | `admin` |

> ⚠️ **IMPORTANT**: Change the admin password immediately after first login in production.
> Go to **Admin → Users → Add User** to create a new admin, then delete or deactivate the default one.

### Author Portal Login
Authors do NOT have a username/password. They log in using:
- **Paper ID** (e.g., `IJMMHRD-2026-A1B2C3`) — given at submission
- **Email** used during submission

Login URL: `/author/login`

---

## 7. All API Endpoints

### 7.1 Public Routes

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Homepage (latest articles, announcements, stats) |
| GET | `/about` | About the journal |
| GET | `/editorial-board` | Editorial board members |
| GET | `/guidelines` | Author guidelines (CMS page) |
| GET | `/paper-format` | Paper format instructions (CMS page) |
| GET | `/how-to-publish` | How to publish guide (CMS page) |
| GET | `/charges` | Processing charges (CMS page) |
| GET | `/research-areas` | All research areas listing |
| GET | `/journal/<slug>` | Research area detail + related articles |
| GET | `/research-area/<slug>` | (alias for journal/<slug>) |
| GET | `/<slug>-journals` | (alias for journal/<slug>) |
| GET | `/<slug>-journal` | (alias for journal/<slug>) |
| GET | `/archives` | Browse all volumes |
| GET | `/archives/<volume_id>` | Browse single volume's issues |
| GET | `/archives/<volume_id>/<issue_id>` | Browse articles in an issue |
| GET | `/search?q=<query>` | Full-text article search |
| GET | `/article/<article_id>` | Published article detail page |
| GET | `/doi/<doi>` | DOI resolver (redirects to article) |
| GET | `/10.5281/<suffix>` | (alias DOI resolver) |
| GET,POST | `/submit` | Paper submission form |
| GET | `/submit/success/<paper_id>` | Submission success confirmation |
| GET,POST | `/track` | Track paper status by Paper ID + email |
| GET,POST | `/contact` | Contact form |
| GET | `/call-for-papers` | Call for Papers (CMS page) |
| GET | `/page/<slug>` | Generic CMS page viewer |
| GET | `/uploads/<path:filename>` | Serve uploaded files |

### 7.2 Author Routes (`/author`)

| Method | URL | Description |
|--------|-----|-------------|
| GET,POST | `/author/login` | Author login (Paper ID + email) |
| GET | `/author/logout` | Author logout |
| GET | `/author/dashboard` | Author's submission dashboard |
| GET | `/author/paper/<paper_id>` | Individual paper detail |
| GET,POST | `/author/paper/<paper_id>/revision` | Upload a revision |
| GET,POST | `/author/profile` | Author profile (read-only) |

### 7.3 Admin Routes (`/admin`) — All require admin/editor login

#### Authentication
| Method | URL | Description |
|--------|-----|-------------|
| GET,POST | `/admin/login` | Admin login form |
| GET | `/admin/logout` | Admin logout |
| GET | `/admin/` | Dashboard with stats |

#### Submissions
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/submissions` | List all submissions (filterable by status) |
| GET | `/admin/submissions/<sub_id>` | Submission detail + reviewer assignment |
| POST | `/admin/submissions/<sub_id>/status` | Update submission status |
| POST | `/admin/submissions/<sub_id>/assign` | Assign a reviewer |

#### Reviewers & Reviews
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/reviewers` | List reviewers |
| POST | `/admin/reviewers/add` | Add a reviewer |
| POST | `/admin/reviewers/<rev_id>/toggle` | Activate/deactivate reviewer |
| GET,POST | `/admin/reviews/<assignment_id>` | View/record a review |

#### Articles
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/articles` | List all articles |
| GET,POST | `/admin/articles/new` | Create a brand-new article directly |
| GET,POST | `/admin/articles/create/<sub_id>` | Create article from accepted submission |
| GET,POST | `/admin/articles/<article_id>/edit` | Edit article metadata + PDF upload |
| POST | `/admin/articles/<article_id>/publish` | Publish article |

#### DOI Management
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/doi` | DOI management overview |
| POST | `/admin/doi/generate/<article_id>` | Generate DOI for article |
| POST | `/admin/doi/register/<article_id>` | Mark DOI as registered |

#### Volumes & Issues
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/issues` | List all volumes and issues |
| POST | `/admin/volumes/add` | Add a new volume |
| POST | `/admin/volumes/<vol_id>/add-issue` | Add issue to a volume |
| POST | `/admin/volumes/<vol_id>/delete` | Delete a volume |
| POST | `/admin/issues/<issue_id>/delete` | Delete an issue |
| POST | `/admin/issues/<issue_id>/set-current` | Mark issue as current |

#### Editorial Board
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/editorial-board` | List board members |
| POST | `/admin/editorial-board/add` | Add a board member |
| POST | `/admin/editorial-board/<member_id>/toggle` | Activate/deactivate member |

#### Users
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/users` | List all admin/editor users |
| POST | `/admin/users/add` | Create new admin/editor user |
| POST | `/admin/users/<user_id>/toggle` | Activate/deactivate user |
| POST | `/admin/users/<user_id>/delete` | **Permanently delete** user account |

#### CMS Content Pages
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/content` | List all CMS pages |
| GET,POST | `/admin/content/<slug>/edit` | Edit a CMS page |
| GET,POST | `/admin/content/new` | Create new CMS page |

#### Announcements
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/admin/announcements` | List + create announcements |
| POST | `/admin/announcements/add` | Add new announcement |
| GET,POST | `/admin/announcements/<ann_id>/edit` | Edit an announcement |
| POST | `/admin/announcements/<ann_id>/toggle` | Publish/unpublish announcement |
| POST | `/admin/announcements/<ann_id>/delete` | Delete announcement |

#### Settings & Messages
| Method | URL | Description |
|--------|-----|-------------|
| GET,POST | `/admin/settings` | Journal settings (name, ISSN, email, DOI prefix, etc.) |
| GET | `/admin/messages` | View contact messages |
| POST | `/admin/messages/<msg_id>/read` | Mark message as read |

---

## 8. Frontend Pages

### Public Pages
| Page | Template | Notes |
|------|----------|-------|
| Homepage | `public/home.html` | Hero, stats, latest articles, announcements, research areas |
| About | `public/about.html` | CMS-driven content |
| Editorial Board | `public/editorial_board.html` | From DB |
| Research Areas | `public/research_areas.html` | Grid of all areas |
| Discipline Detail | `public/discipline_detail.html` | Filtered articles by area |
| Archives | `public/archives.html` | Volume listing |
| Archive Volume | `public/archive_volume.html` | Issues within a volume |
| Archive Issue | `public/archive_issue.html` | Articles within an issue |
| Article Detail | `public/article.html` | Full article with PDF download |
| Submit Paper | `public/submit.html` | Multi-author submission form |
| Submit Success | `public/submit_success.html` | Paper ID confirmation page |
| Track Paper | `public/track.html` | Status tracking by Paper ID + email |
| Search | `public/search.html` | Full-text search results |
| Contact | `public/contact.html` | Contact form |
| Static Pages | `public/static_page.html` | Guidelines, charges, how-to, CfP |

### Admin Panel Pages
| Page | Template |
|------|----------|
| Dashboard | `admin/dashboard.html` |
| Submissions List | `admin/submissions.html` |
| Submission Detail | `admin/submission_detail.html` |
| Articles List | `admin/articles.html` |
| Article Edit | `admin/article_edit.html` |
| Article Direct Create | `admin/article_direct_create.html` |
| Article From Submission | `admin/article_create.html` |
| DOI Management | `admin/doi_management.html` |
| Volumes & Issues | `admin/issues.html` |
| Editorial Board | `admin/editorial_board.html` |
| Reviewers | `admin/reviewers.html` |
| Review Detail | `admin/review_detail.html` |
| Users | `admin/users.html` |
| Announcements | `admin/announcements.html` |
| CMS Content List | `admin/content_list.html` |
| CMS Content Edit | `admin/content_edit.html` |
| Settings | `admin/settings.html` |
| Messages | `admin/messages.html` |

---

## 9. Bug Fixes Applied

The following bugs were identified and fixed during the production review:

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `routes/public.py` (L214) | `url_for('public.index')` — endpoint `public.index` does not exist; would cause a 500 error when a DOI is not found | Changed to `url_for('public.home')` |
| 2 | `routes/admin.py` | `add_announcement` route did not parse date strings or default publish_date when "Publish Immediately" was checked | Added `datetime.strptime` parsing with `date.today()` fallback |
| 3 | `routes/admin.py` | Missing `from datetime import datetime, date` import | Added import |
| 4 | `templates/admin/announcements.html` | Old layout crammed into 2-column grid making the rich editor unusable | Replaced with single-column centered container (max 960px) |
| 5 | `templates/admin/users.html` | No delete user button in the template | Added 🗑️ Delete button with confirmation dialog |
| 6 | Backend | `delete_user` route was missing from `admin.py` | Full route added with self-deletion guard |

---

## 10. Production Checklist

### ✅ Security
- [ ] Change `SECRET_KEY` in `.env` to a random 32+ char string
- [ ] Change default admin password (`admin123` → strong password)
- [ ] Set `SESSION_COOKIE_SECURE = True` in `config.py` if using HTTPS
- [ ] Set `SESSION_COOKIE_SAMESITE = 'Strict'` in `config.py` for production
- [ ] Set `USE_SQLITE=false` and configure MySQL credentials
- [ ] Ensure `.env` is NOT in version control

### ✅ Database
- [ ] Run `python3 init_db.py` on fresh production server
- [ ] Update journal settings via Admin → Settings (name, ISSN, email, DOI prefix)
- [ ] Add editorial board members via Admin → Editorial Board
- [ ] Add real volumes and issues via Admin → Issues

### ✅ Media & Assets
- [ ] Upload actual journal logo to `static/images/logo.png`
- [ ] Ensure `uploads/` directory is writable (`chmod 775 uploads`)
- [ ] Configure web server to NOT serve `.env`, `.git`, or `*.db` files

### ✅ CMS Content
- [ ] Edit "About" page via Admin → Content → about
- [ ] Edit "Author Guidelines" via Admin → Content → author-guidelines
- [ ] Edit "Processing Charges" via Admin → Content → processing-charges
- [ ] Edit "How to Publish" via Admin → Content → how-to-publish
- [ ] Update footer text via Admin → Settings → footer_text

### ✅ Functional Testing
- [ ] Test paper submission flow (submit → track → admin review)
- [ ] Test announcement creation and homepage display
- [ ] Test PDF upload for articles
- [ ] Test contact form message receipt
- [ ] Verify DOI resolve works (`/doi/<doi>` redirects to article)

---

## 11. MySQL Migration (Production)

When switching from SQLite to MySQL:

1. Update `.env`:
```
USE_SQLITE=false
DB_HOST=localhost
DB_USER=ijmmhrd_user
DB_PASS=yourpassword
DB_NAME=ijmmhrd
```

2. Install MySQL connector (already in requirements):
```bash
pip install PyMySQL
```

3. Create database in MySQL and run:
```bash
python3 init_db.py
```

4. To migrate existing SQLite data to MySQL, use a tool like [sqlite3-to-mysql](https://github.com/techouse/sqlite3-to-mysql):
```bash
pip install sqlite3-to-mysql
sqlite3mysql --sqlite-file ijmmhrd.db --mysql-database ijmmhrd --mysql-user ijmmhrd_user --mysql-password yourpassword
```

---

## 12. Deployment on LAMPP/cPanel

### LAMPP (Local)
```bash
# Start LAMPP
sudo /opt/lampp/lampp start

# Install dependencies
cd /opt/lampp/htdocs/new_Simple_LB
pip3 install -r requirements.txt

# Initialize DB
python3 init_db.py

# Run Flask dev server
python3 app.py
# Access at: http://localhost:5000
```

### cPanel / Shared Hosting (Passenger WSGI)
The `passenger_wsgi.py` file is already configured:
```python
# passenger_wsgi.py
from app import create_app
application = create_app()
```

1. In cPanel → Python App: Set application root to the project directory
2. Set the startup file to `passenger_wsgi.py`
3. Set the application entry point to `application`
4. Click **Restart** in the Python App section

### Gunicorn (VPS / Docker)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

---

## Appendix: Submission Status Workflow

```
submitted
    └─► initial_review
            └─► reviewer_assigned
                    └─► under_review
                            ├─► revision_required
                            │       └─► revision_submitted ──┐
                            ├─► accepted ──────────────────┤
                            └─► rejected                   │
                                                            ▼
                                                        published
```

Status transitions are enforced by `Submission.can_transition_to()` in `models/submission.py`.

---

*Documentation generated: September 2026 | Version: 1.0*
