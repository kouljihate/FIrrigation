"""Farm Irrigation Workbench — Flask app factory."""
from __future__ import annotations

from flask import Flask, session

from config import Config
from logging_config import setup_logging


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    setup_logging(Config.LOG_DIR, Config.LOG_LEVEL)

    # ---- extensions ----
    from db.connection import init_app as init_db
    init_db(app)

    # ---- blueprints ----
    from routes.home import bp as home_bp
    from routes.project import bp as project_bp
    from routes.geometry import bp as geometry_bp
    from routes.hydrology import bp as hydrology_bp
    from routes.field import bp as field_bp
    from routes.export import bp as export_bp
    from routes.api import bp as api_bp
    from routes.map_view import bp as map_bp
    from routes.logs import bp as logs_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(geometry_bp)
    app.register_blueprint(hydrology_bp)
    app.register_blueprint(field_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(map_bp)
    app.register_blueprint(logs_bp)

    # ---- session defaults ----
    @app.before_request
    def _default_project():
        if "project_id" not in session:
            session["project_id"] = ""  # empty until home chooses one

    # ---- context processor: inject global values into every template ----
    @app.context_processor
    def inject_globals():
        from db import queries
        pid = session.get("project_id", "")
        summary = {}
        if pid:
            try:
                summary = queries.project_summary(pid)
            except Exception:
                summary = {}
        return {
            "app_title": app.config["APP_TITLE"],
            "app_version": app.config["APP_VERSION"],
            "project_id": pid or "(none)",
            "summary": summary,
        }

    # ---- error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        app.logger.exception("Internal server error")
        return render_template("error.html", code=500,
                               message="Internal server error"), 500

    return app