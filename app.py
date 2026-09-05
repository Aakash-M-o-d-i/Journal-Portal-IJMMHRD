import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db
from models.user import User
from models.content import Setting


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Extensions
    db.init_app(app)
    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
