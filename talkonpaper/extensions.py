import sqlite3

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import event

db = SQLAlchemy()
login_manager = LoginManager()


def register_sqlite_pragmas(app) -> None:
    """
    Enforce WAL, busy timeout, and foreign key constraints for SQLite.
    """

    if not app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        return

    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout=5000;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    with app.app_context():
        event.listen(db.engine, "connect", _set_sqlite_pragma)
