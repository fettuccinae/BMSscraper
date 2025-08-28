from flask import Flask
from logging.config import dictConfig


def create_app():
    from dotenv import load_dotenv
    load_dotenv()  

    app = Flask(__name__)
    app.config.from_pyfile("config.py", silent=True)

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )

    from webserver import db

    db.initalize_databse_if_it_dont_exist(app)
    db.init_db_engine(app.config["SQLALCHEMY_URI"])

    from webserver.views import auth, tix

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(tix.tix_bp)
    app.add_url_rule("/", endpoint="index")

    return app
