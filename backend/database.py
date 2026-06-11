import sqlite3
from pathlib import Path

from config import BASE_DIR


DATABASE_PATH = BASE_DIR / "data" / "weekly_digest.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT NOT NULL,
                category TEXT NOT NULL,
                digest TEXT NOT NULL,
                generatedAt TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                digest_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT,
                summary TEXT,
                publishedAt TEXT,
                createdAt TEXT,
                FOREIGN KEY (digest_id) REFERENCES digests (id)
            )
            """
        )
        article_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(articles)").fetchall()
        }
        if "summary" not in article_columns:
            connection.execute("ALTER TABLE articles ADD COLUMN summary TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                language TEXT NOT NULL,
                category TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT,
                published_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_articles_language_category
            ON articles (language, category, digest_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_digests_language_category
            ON digests (language, category, generatedAt)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_saved_articles_user_id
            ON saved_articles (user_id, id)
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_saved_articles_user_url
            ON saved_articles (user_id, url)
            """
        )
        connection.commit()
    finally:
        connection.close()
