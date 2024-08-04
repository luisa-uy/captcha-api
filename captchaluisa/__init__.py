from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import time

db = SQLAlchemy()

def retry(max_retries=10, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    print(f"Database connection failed. Retry {retries}/{max_retries} after {delay} seconds.")
                    time.sleep(delay)
            raise Exception(f"Failed to connect to the database after {max_retries} attempts.")
        return wrapper
    return decorator

@retry(max_retries=10, delay=2)
def initialize_db(app):
    db.init_app(app)
    with app.app_context():
        from . import routes  # Import routes
        db.create_all()  # Create sql tables for our data models
        app.logger.info("Database connection successful.")

def init_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    initialize_db(app)