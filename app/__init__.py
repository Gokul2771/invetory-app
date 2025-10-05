from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.update(
        SECRET_KEY="dev-secret-change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///inventory.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
