import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()

def init_db(app):
    """
    Initializes SQLAlchemy. Attempts to connect to MySQL first.
    If MySQL connection fails, falls back to local SQLite database.
    """
    # Prefer SQLALCHEMY_DATABASE_URI (this will contain DATABASE_URL from env if present),
    # otherwise fall back to explicit DATABASE_URL or constructed MYSQL_URI from config.
    mysql_uri = (
        app.config.get("SQLALCHEMY_DATABASE_URI")
        or app.config.get("DATABASE_URL")
        or app.config.get("MYSQL_URI")
    )
    sqlite_uri = app.config.get("SQLITE_URI")
    
    # Try connecting to MySQL
    host = app.config.get('DB_HOST')
    port = app.config.get('DB_PORT')
    logging.info(f"Attempting to connect to MySQL at: {host}:{port}")

    try:
        # Create an engine to test connectivity. Mask password in logs if present.
        safe_uri = mysql_uri
        try:
            # rudimentary mask: replace :<password>@ with :***@
            import re
            safe_uri = re.sub(r":[^:@]+@", ":***@", mysql_uri)
        except Exception:
            safe_uri = mysql_uri
        logging.info(f"Testing DB URI: {safe_uri}")

        engine = create_engine(mysql_uri)
        connection = engine.connect()
        connection.close()

        # If successful, use MySQL URI
        app.config["SQLALCHEMY_DATABASE_URI"] = mysql_uri
        logging.info("Successfully connected to MySQL database. Using MySQL.")
    except Exception as e:
        # In strict MySQL-only mode we should fail loudly instead of silently falling back.
        # Raise an error so operator can fix DB connection.
        logging.error(f"Failed to connect to MySQL ({e}). Aborting startup because MySQL is required.")
        raise
        
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        logging.info("Database tables verified/created.")
