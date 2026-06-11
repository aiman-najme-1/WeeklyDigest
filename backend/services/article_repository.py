from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from database import get_connection


CACHE_DAYS = 7


def _now_text():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        pass

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _is_recent_article_date(value):
    published_at = _parse_datetime(value)
    if not published_at:
        return False

    now = datetime.now(timezone.utc)
    oldest_allowed = now - timedelta(days=CACHE_DAYS)
    newest_allowed = now + timedelta(days=1)
    return oldest_allowed <= published_at <= newest_allowed


def _cache_age_days(generated_at):
    generated_datetime = _parse_datetime(generated_at)
    if not generated_datetime:
        return None

    age = datetime.now(timezone.utc) - generated_datetime
    return round(age.total_seconds() / 86400, 2)


def _article_for_response(row):
    published_at = row["publishedAt"] or ""
    return {
        "title": row["title"],
        "url": row["url"],
        "source": row["source"] or "Unknown source",
        "published": published_at,
        "publishedAt": published_at,
        "summary": row["summary"] or "",
    }


def _article_values(article, language, category, digest_id, created_at):
    published_at = article.get("publishedAt") or article.get("published") or ""
    return (
        digest_id,
        language,
        category,
        article.get("title", ""),
        article.get("url", ""),
        article.get("source") or "Unknown source",
        article.get("summary") or "",
        published_at,
        created_at,
    )


def get_cached_digest(language, category):
    min_date = datetime.now(timezone.utc) - timedelta(days=CACHE_DAYS)
    min_date_text = min_date.isoformat(timespec="seconds").replace("+00:00", "Z")

    connection = get_connection()
    try:
        digest_row = connection.execute(
            """
            SELECT id, language, category, digest, generatedAt
            FROM digests
            WHERE language = ? AND category = ? AND generatedAt >= ?
            ORDER BY generatedAt DESC, id DESC
            LIMIT 1
            """,
            (language, category, min_date_text),
        ).fetchone()

        if not digest_row:
            return None

        article_rows = connection.execute(
            """
            SELECT title, url, source, summary, publishedAt
            FROM articles
            WHERE digest_id = ?
            ORDER BY id ASC
            """,
            (digest_row["id"],),
        ).fetchall()
    finally:
        connection.close()

    if not article_rows:
        return None

    for row in article_rows:
        if not _is_recent_article_date(row["publishedAt"]):
            print(
                "WeeklyDigest cache skipped: "
                f"language={language} category={category} reason=stale_article_dates",
                flush=True,
            )
            return None

    return {
        "category": digest_row["category"],
        "language": digest_row["language"],
        "digest": digest_row["digest"],
        "generatedAt": digest_row["generatedAt"],
        "cacheAgeDays": _cache_age_days(digest_row["generatedAt"]),
        "articles": [_article_for_response(row) for row in article_rows],
    }


def save_digest_with_articles(language, category, digest, articles):
    generated_at = _now_text()
    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO digests (language, category, digest, generatedAt)
                VALUES (?, ?, ?, ?)
                """,
                (language, category, digest, generated_at),
            )
            digest_id = cursor.lastrowid

            for article in articles:
                title = (article.get("title") or "").strip()
                url = (article.get("url") or "").strip()

                if not title or not url:
                    continue

                values = _article_values(article, language, category, digest_id, generated_at)
                connection.execute(
                    """
                    INSERT INTO articles
                    (digest_id, language, category, title, url, source, summary, publishedAt, createdAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
    finally:
        connection.close()

    return generated_at
