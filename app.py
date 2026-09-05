import os
import bleach
from bleach.css_sanitizer import CSSSanitizer
from flask import Flask, render_template, session
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config, _DANGEROUS_DEFAULT_KEYS
from models import db
from models.user import User
from models.content import Setting

# ── Bleach allowed configuration (for CMS |safe content) ─────────
_ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'div', 'span', 'hr', 'sup', 'sub',
]
_ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    '*': ['class', 'style', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}
_CSS_SANITIZER = CSSSanitizer(allowed_css_properties=[
    'color', 'background-color', 'font-size', 'font-weight', 'font-style',
    'text-align', 'text-decoration', 'margin', 'padding', 'border',
    'width', 'height', 'max-width', 'line-height', 'display',
])

# Global limiter instance (configured per-route)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No default — apply per-route only
    storage_uri="memory://",
)


def sanitize_html(content):
    """Strip dangerous HTML tags/attributes; safe for use in templates."""
    if not content:
        return ''
    return bleach.clean(
        content,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
    )


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── 🔐 Startup: abort if default secret key used in production ─
    flask_env = os.getenv('FLASK_ENV', 'production')
    if flask_env != 'development' and app.config['SECRET_KEY'] in _DANGEROUS_DEFAULT_KEYS:
        raise RuntimeError(
            "SECURITY ERROR: SECRET_KEY is set to an insecure default value. "
            "Set a strong, random SECRET_KEY in your .env file before running in production."
        )

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Extensions
    db.init_app(app)
    CSRFProtect(app)
    limiter.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── 🌐 Security response headers ──────────────────────────────
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Allow inline styles/scripts for current CSS-heavy templates
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob:; "
            "frame-ancestors 'self';"
        )
        return response

    # ── 🧠 Jinja2 sanitize filter (replaces raw |safe on CMS content) ─
    @app.template_filter('sanitize')
    def sanitize_filter(content):
        return sanitize_html(content)

    # ── Session permanence (enforces PERMANENT_SESSION_LIFETIME) ──
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Context processor — inject settings, sidebar volumes, and research areas
    @app.context_processor
    def inject_settings():
        try:
            settings = {s.setting_key: s.setting_value for s in Setting.query.all()}
            from models.issue import Volume
            from models.content import ResearchArea
            sidebar_volumes = Volume.query.order_by(Volume.year.desc()).all()
            nav_research_areas = ResearchArea.query.filter_by(is_active=True).order_by(ResearchArea.display_order).all()
        except Exception:
            settings = {}
            sidebar_volumes = []
            nav_research_areas = []
        return dict(site_settings=settings, sidebar_volumes=sidebar_volumes, nav_research_areas=nav_research_areas)

    # Register blueprints
    from routes.public import public
    from routes.author import author
    from routes.admin import admin

    app.register_blueprint(public)
    app.register_blueprint(author)
    app.register_blueprint(admin)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template('errors/429.html', error=e.description), 429

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
