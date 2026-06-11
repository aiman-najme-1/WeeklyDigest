import sqlite3
from datetime import datetime, timezone

from database import get_connection


def _now_text():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _user_from_row(row):
    if not row:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def create_user(username, email, password_hash):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username.strip(), email.strip().lower(), password_hash, _now_text()),
            )
            user_id = cursor.lastrowid
            connection.execute(
                """
                INSERT INTO user_preferences (user_id, language, category)
                VALUES (?, ?, ?)
                """,
                (user_id, "ru", "sports"),
            )
    except sqlite3.IntegrityError:
        return None
    finally:
        connection.close()

    return get_user_by_id(user_id)


def get_user_by_email(email):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT id, username, email, password_hash, created_at
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()
    finally:
        connection.close()

    return row


def get_user_by_id(user_id):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT id, username, email, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        connection.close()

    return _user_from_row(row)


def get_preferences(user_id):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT language, category
            FROM user_preferences
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        connection.close()

    if not row:
        return {"language": "ru", "category": "sports"}

    return {"language": row["language"], "category": row["category"]}


def update_preferences(user_id, language, category):
    connection = get_connection()
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO user_preferences (user_id, language, category)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    language = excluded.language,
                    category = excluded.category
                """,
                (user_id, language, category),
            )
    finally:
        connection.close()

    return get_preferences(user_id)


def _saved_article_from_row(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "url": row["url"],
        "source": row["source"] or "Unknown source",
        "published_at": row["published_at"] or "",
        "created_at": row["created_at"],
    }


def get_saved_articles(user_id):
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT id, title, url, source, published_at, created_at
            FROM saved_articles
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        connection.close()

    return [_saved_article_from_row(row) for row in rows]


def save_article(user_id, article):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO saved_articles
                (user_id, title, url, source, published_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    article["title"].strip(),
                    article["url"].strip(),
                    article.get("source") or "Unknown source",
                    article.get("published_at") or article.get("publishedAt") or "",
                    _now_text(),
                ),
            )

            if cursor.rowcount:
                article_id = cursor.lastrowid
            else:
                article_id = connection.execute(
                    """
                    SELECT id
                    FROM saved_articles
                    WHERE user_id = ? AND url = ?
                    """,
                    (user_id, article["url"].strip()),
                ).fetchone()["id"]

        row = connection.execute(
            """
            SELECT id, title, url, source, published_at, created_at
            FROM saved_articles
            WHERE id = ? AND user_id = ?
            """,
            (article_id, user_id),
        ).fetchone()
    finally:
        connection.close()

    return _saved_article_from_row(row)


def delete_saved_article(user_id, article_id):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                DELETE FROM saved_articles
                WHERE id = ? AND user_id = ?
                """,
                (article_id, user_id),
            )
            return cursor.rowcount > 0
    finally:
        connection.close()
