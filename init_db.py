import datetime
import bcrypt
from app import create_app
from models import db
from models.user import User
from models.content import Page, Setting, ResearchArea
from models.issue import Volume, Issue

def init_db():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        # 1. Default Admin User
        admin = User.query.filter_by(email='admin@ijmmhrd.com').first()
        if not admin:
            hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            admin = User(
                email='admin@ijmmhrd.com',
                password_hash=hashed,
                full_name='IJMMHRD Admin',
                role='admin'
            )
            db.session.add(admin)
            print("Created default admin user: admin@ijmmhrd.com / admin123")

        # 2. Default Settings
        default_settings = {
            'journal_name': 'International Journal of Multidisciplinary Modern Research and Development',
            'journal_abbr': 'IJMMHRD',
            'journal_issn': 'XXXX-XXXX',
            'journal_email': 'editor@ijmmhrd.com',
            'journal_url': 'https://ijmmhrd.com',
            'doi_prefix': '10.XXXXX',
            'publication_frequency': 'Monthly',
            'footer_text': '© 2026 IJMMHRD. All rights reserved.',
            'contact_address': 'Main Administrative Office, IJMMHRD',
            'contact_phone': '+1 (555) 019-2831',
            'contact_email': 'editor@ijmmhrd.com'
        }
        for key, val in default_settings.items():
            if not Setting.query.filter_by(setting_key=key).first():
                db.session.add(Setting(setting_key=key, setting_value=val))
        print("Seeded default settings.")

        # 3. Default CMS Pages
        pages_data = [
            ('about', 'About IJMMHRD', '<p>The International Journal of Multidisciplinary Modern Research and Development (IJMMHRD) is a peer-reviewed, open-access journal that publishes high-quality research across all disciplines.</p>'),
            ('aim-scope', 'Aim & Scope', '<p>IJMMHRD aims to provide a platform for researchers, scholars, and academicians to share their research findings across multiple disciplines including engineering, science, humanities, and social sciences.</p>'),
            ('author-guidelines', 'Author Guidelines', '<p>Authors are invited to submit original research papers, review articles, and short communications. All manuscripts must be submitted electronically through the journal submission portal.</p>'),
            ('paper-format', 'Paper Format', '<p>Manuscripts should be prepared in accordance with standard double-column academic paper templates in Microsoft Word or LaTeX format.</p>'),
            ('how-to-publish', 'How to Publish', '<p>Publishing with IJMMHRD is a 4-step process: 1. Submit Paper, 2. Peer Review, 3. Revision (if requested), 4. Publication and DOI Assignment.</p>'),
            ('processing-charges', 'Processing Charges', '<p>IJMMHRD is an open-access journal. Article Processing Charges (APC) cover open access publication, indexing, permanent archiving, and DOI assignment.</p>'),
            ('home-intro', 'Home Introduction', '<p>Welcome to IJMMHRD — a leading multidisciplinary journal dedicated to advancing knowledge through rigorous peer-reviewed research.</p>'),
            ('call-for-papers', 'Call for Papers', '<p>IJMMHRD invites authors to submit papers for the upcoming monthly volume. Submit your manuscript online today.</p>')
        ]
        for slug, title, content in pages_data:
            if not Page.query.filter_by(slug=slug).first():
                db.session.add(Page(slug=slug, title=title, content=content, status='published'))
        print("Seeded default pages.")

        # 4. Research Areas
        areas = [
            'Computer Science & Engineering', 'Electronics & Communication', 'Mechanical Engineering',
            'Civil Engineering', 'Electrical Engineering', 'Biotechnology', 'Physics', 'Chemistry',
            'Mathematics', 'Management & Commerce', 'Arts & Humanities', 'Medical Sciences',
            'Environmental Science', 'Social Sciences', 'Education'
        ]
        for i, name in enumerate(areas, 1):
            if not ResearchArea.query.filter_by(name=name).first():
                db.session.add(ResearchArea(name=name, display_order=i))
        print("Seeded research areas.")

        # 5. Sample Volumes & Issues for Archive Sidebar
        sample_volumes = [
            (15, 2026),
            (14, 2025),
            (13, 2024),
            (12, 2023)
        ]
        for vol_num, year in sample_volumes:
            vol = Volume.query.filter_by(volume_number=vol_num).first()
            if not vol:
                vol = Volume(volume_number=vol_num, year=year)
                db.session.add(vol)
                db.session.flush()

                # Add sample issues 1..4 for each volume
                for issue_num in range(1, 5):
                    is_curr = (vol_num == 15 and issue_num == 1)
                    pub_date = datetime.date(year, issue_num * 3, 15)
                    issue = Issue(
                        volume_id=vol.id,
                        issue_number=issue_num,
                        title=f"Regular Issue {issue_num}",
                        publication_date=pub_date,
                        is_current=is_curr
                    )
                    db.session.add(issue)
        print("Seeded sample volumes and issues.")

        db.session.commit()
        print("Database initialization complete!")

if __name__ == '__main__':
    init_db()
