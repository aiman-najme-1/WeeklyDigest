import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests


MAX_ARTICLE_AGE_DAYS = 7


class RssServiceError(Exception):
    """Raised when an RSS feed cannot be fetched or parsed."""


def _clean_text(value):
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _error_message(language, category):
    if language == "ru":
        return f"Не удалось загрузить RSS-ленту для категории: {category}."

    return f"Could not load RSS feed for category: {category}."


def _empty_message(language, category):
    if language == "ru":
        return f"В RSS-ленте для категории {category} не найдено подходящих новостей."

    return f"No suitable news was found in the {category} RSS feed."


def _normalize_sources(rss_sources):
    if isinstance(rss_sources, str):
        return [{"name": "Unknown source", "url": rss_sources}]

    if isinstance(rss_sources, dict):
        return [rss_sources]

    return list(rss_sources)


def _article_key(article):
    url_key = article.get("url", "").split("#", 1)[0].split("?", 1)[0].rstrip("/")
    title_key = article.get("title", "").strip().lower()
    return url_key or title_key


def _parse_entry_datetime(entry):
    for parsed_key in ("published_parsed", "updated_parsed"):
        parsed_value = entry.get(parsed_key)
        if parsed_value:
            try:
                return datetime(*parsed_value[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError, IndexError, OverflowError):
                continue

    for text_key in ("published", "updated", "created"):
        text_value = entry.get(text_key)
        if not text_value:
            continue

        try:
            parsed = parsedate_to_datetime(text_value)
        except (TypeError, ValueError, IndexError, OverflowError):
            continue

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    return None


def _is_recent_article(published_at):
    if not published_at:
        return False

    now = datetime.now(timezone.utc)
    oldest_allowed = now - timedelta(days=MAX_ARTICLE_AGE_DAYS)
    newest_allowed = now + timedelta(days=1)
    return oldest_allowed <= published_at <= newest_allowed


def _deduplicate_article_groups(article_groups):
    unique_groups = []
    seen = set()

    for source_name, source_articles in article_groups:
        unique_articles = []

        for article in source_articles:
            key = _article_key(article)

            if key and key in seen:
                continue

            if key:
                seen.add(key)

            unique_articles.append(article)

        if unique_articles:
            unique_groups.append((source_name, unique_articles))

    return unique_groups


def _select_balanced_articles(article_groups, limit):
    selected = []
    positions = [0 for _source_name, _articles in article_groups]

    while len(selected) < limit:
        added_this_round = False

        for index, (_source_name, source_articles) in enumerate(article_groups):
            while positions[index] < len(source_articles):
                article = source_articles[positions[index]]
                positions[index] += 1

                selected.append(article)
                added_this_round = True
                break

            if len(selected) >= limit:
                break

        if not added_this_round:
            break

    return selected


def _fetch_source_articles(rss_source, category, language, limit):
    source_name = rss_source.get("name") or "Unknown source"
    rss_url = rss_source.get("url", "").strip()

    if not rss_url:
        return []

    try:
        response = requests.get(
            rss_url,
            timeout=12,
            headers={"User-Agent": "WeeklyDigest MVP/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RssServiceError(_error_message(language, category)) from exc

    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise RssServiceError(_error_message(language, category))

    articles = []
    fetched_count = 0
    entry_limit = max(limit * 4, 24)

    for entry in feed.entries[:entry_limit]:
        title = _clean_text(entry.get("title", ""))
        url = entry.get("link", "").strip()
        published_at = entry.get("published", entry.get("updated", "")).strip()
        summary = _clean_text(entry.get("summary", entry.get("description", "")))
        parsed_date = _parse_entry_datetime(entry)

        if title and url:
            fetched_count += 1

        if title and url and _is_recent_article(parsed_date):
            articles.append(
                {
                    "title": title,
                    "url": url,
                    "source": source_name,
                    "published": published_at,
                    "publishedAt": published_at,
                    "summary": summary,
                }
            )

    articles = articles[:limit]
    print(
        "WeeklyDigest RSS source: "
        f"language={language} category={category} source={source_name} "
        f"fetched={fetched_count} after_date_filter={len(articles)}",
        flush=True,
    )

    return articles


def fetch_articles(rss_sources, category="sports", language="ru", limit=12):
    sources = _normalize_sources(rss_sources)
    if not sources:
        raise RssServiceError(_error_message(language, category))

    article_groups = []
    errors = []

    for rss_source in sources:
        source_name = rss_source.get("name", "Unknown source")
        try:
            source_articles = _fetch_source_articles(
                rss_source,
                category=category,
                language=language,
                limit=limit,
            )

            if source_articles:
                article_groups.append((source_name, source_articles))
        except RssServiceError as exc:
            print(
                "WeeklyDigest RSS source error: "
                f"language={language} category={category} source={source_name} error={exc}",
                flush=True,
            )
            errors.append(str(exc))

    after_date_filter_count = sum(len(articles) for _source_name, articles in article_groups)
    unique_groups = _deduplicate_article_groups(article_groups)
    after_duplicate_filter_count = sum(len(articles) for _source_name, articles in unique_groups)
    articles = _select_balanced_articles(unique_groups, limit)
    sources_used = sorted({article.get("source", "Unknown source") for article in articles})

    print(
        "WeeklyDigest RSS summary: "
        f"language={language} category={category} "
        f"after_date_filter={after_date_filter_count} "
        f"after_duplicate_filter={after_duplicate_filter_count} "
        f"final_selected={len(articles)} sources_used={', '.join(sources_used) or 'none'}",
        flush=True,
    )

    if not articles:
        if errors:
            raise RssServiceError(errors[0])

        raise RssServiceError(_empty_message(language, category))

    return articles


def fetch_sports_articles(rss_url, limit=12):
    return fetch_articles(rss_url, category="sports", language="ru", limit=limit)
