import os

SECRET_KEY = os.environ.get("SECRET_KEY")
CRON_SECRET = os.environ.get("CRON_SECRET")
SQLALCHEMY_URI = os.environ.get("SQLALCHEMY_URI")
POSTGRES_ADMIN_URI = os.environ.get("POSTGRES_ADMIN_URI")
SERVER_USERNAME = os.environ.get("SERVER_USERNAME")
SERVER_PASSWORD = os.environ.get("SERVER_PASSWORD")