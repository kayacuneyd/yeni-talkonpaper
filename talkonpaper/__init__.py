import os
from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import db, login_manager, register_sqlite_pragmas
from .routes import main_bp
from .admin import admin_bp


def create_app(test_config: dict | None = None) -> Flask:
    """
    Application factory configured for SQLite + Cloudflare R2 signed URL usage.
    """
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )

    # Ensure instance directory exists for SQLite files/logs.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.from_object(Config(app.instance_path))
    if test_config:
        app.config.update(test_config)

    _configure_extensions(app)
    _register_blueprints(app)
    _register_template_globals(app)

    with app.app_context():
        # Create tables if they do not exist; production should use Alembic migrations.
        db.create_all()

    return app


def _configure_extensions(app: Flask) -> None:
    db.init_app(app)
    register_sqlite_pragmas(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.home"


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)


def _register_template_globals(app: Flask) -> None:
    @app.context_processor
    def inject_site_meta():
        return {
            "site_name": "TalkOnPaper",
            "site_tagline": "Cross-border academic visibility without visas, language, or geography barriers",
            "cdn_base_url": os.environ.get("CDN_BASE_URL", ""),
        }
