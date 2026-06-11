from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_ORIGINS, RSS_FEEDS, has_github_token
from database import init_db
from models.schemas import (
    AuthResponse,
    DigestResponse,
    HealthResponse,
    LoginRequest,
    PreferencesRequest,
    PreferencesResponse,
    RegisterRequest,
    SavedArticleRequest,
    SavedArticleResponse,
    UserResponse,
)
from services.article_repository import get_cached_digest, save_digest_with_articles
from services.auth_service import create_token, hash_password, read_token, verify_password
from services.rss_service import RssServiceError, fetch_articles
from services.summarizer_service import create_digest_with_status
from services.user_repository import (
    create_user,
    delete_saved_article,
    get_preferences,
    get_saved_articles,
    get_user_by_email,
    get_user_by_id,
    save_article,
    update_preferences,
)


app = FastAPI(
    title="WeeklyDigest MVP",
    description="Weekly news digest MVP powered by RSS and optional GitHub Models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def log_startup_configuration():
    init_db()
    status = "configured" if has_github_token() else "missing, using fallback summaries"
    print(f"WeeklyDigest startup: GITHUB_TOKEN is {status}.", flush=True)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "service": "WeeklyDigest MVP"}


def _validate_language_category(language, category):
    if language not in RSS_FEEDS:
        raise HTTPException(status_code=400, detail="Unsupported language.")

    if category not in RSS_FEEDS[language]:
        raise HTTPException(status_code=400, detail="Unsupported category.")


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized.")

    token = authorization.replace("Bearer ", "", 1).strip()
    user_id = read_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    return user


@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(payload: RegisterRequest):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required.")

    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    user = create_user(username, email, hash_password(password))
    if not user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    return {"token": create_token(user["id"]), "user": user}


@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(payload: LoginRequest):
    user_row = get_user_by_email(payload.email)

    if not user_row or not verify_password(payload.password, user_row["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong email or password.")

    user = {
        "id": user_row["id"],
        "username": user_row["username"],
        "email": user_row["email"],
        "created_at": user_row["created_at"],
    }
    return {"token": create_token(user["id"]), "user": user}


@app.get("/api/me", response_model=UserResponse)
def read_me(user=Depends(get_current_user)):
    return user


@app.get("/api/me/preferences", response_model=PreferencesResponse)
def read_preferences(user=Depends(get_current_user)):
    return get_preferences(user["id"])


@app.put("/api/me/preferences", response_model=PreferencesResponse)
def save_preferences(payload: PreferencesRequest, user=Depends(get_current_user)):
    language = payload.language.lower()
    category = payload.category.lower()
    _validate_language_category(language, category)
    return update_preferences(user["id"], language, category)


@app.get("/api/me/saved-articles", response_model=list[SavedArticleResponse])
def read_saved_articles(user=Depends(get_current_user)):
    return get_saved_articles(user["id"])


@app.post("/api/me/saved-articles", response_model=SavedArticleResponse)
def add_saved_article(payload: SavedArticleRequest, user=Depends(get_current_user)):
    if not payload.title.strip() or not payload.url.strip():
        raise HTTPException(status_code=400, detail="Article title and URL are required.")

    return save_article(user["id"], payload.model_dump())


@app.delete("/api/me/saved-articles/{article_id}")
def remove_saved_article(article_id: int, user=Depends(get_current_user)):
    if not delete_saved_article(user["id"], article_id):
        raise HTTPException(status_code=404, detail="Saved article not found.")

    return {"status": "deleted"}


def _articles_for_response(articles):
    return [
        {
            "title": article["title"],
            "url": article["url"],
            "source": article.get("source", "Unknown source"),
            "published": article.get("published", ""),
            "publishedAt": article.get("publishedAt", article.get("published", "")),
            "summary": article.get("summary", ""),
        }
        for article in articles
    ]


def _sources_used(articles):
    sources = []

    for article in articles:
        source = article.get("source") or "Unknown source"
        if source not in sources:
            sources.append(source)

    return sources


@app.get("/api/{language}/{category}/digest", response_model=DigestResponse)
def get_digest(language: str, category: str, refresh: bool = False):
    language = language.lower()
    category = category.lower()
    print(
        "WeeklyDigest request: "
        f"language={language} category={category} refresh={refresh}",
        flush=True,
    )

    if language not in RSS_FEEDS:
        raise HTTPException(status_code=404, detail="Unsupported language.")

    rss_sources = RSS_FEEDS[language].get(category)
    if not rss_sources:
        raise HTTPException(status_code=404, detail="Unsupported category.")

    if not refresh:
        cached_digest = get_cached_digest(language, category)
        if cached_digest:
            sources_used = _sources_used(cached_digest["articles"])
            print(
                "WeeklyDigest response: "
                f"language={language} category={category} cache=used "
                f"articles={len(cached_digest['articles'])} "
                f"sources={', '.join(sources_used) or 'none'}",
                flush=True,
            )
            return {
                "category": cached_digest["category"],
                "language": cached_digest["language"],
                "generatedAt": cached_digest["generatedAt"],
                "fromCache": True,
                "cacheAgeDays": cached_digest["cacheAgeDays"],
                "cacheStatus": "loaded_from_cache",
                "articlesCount": len(cached_digest["articles"]),
                "sourcesUsed": sources_used,
                "summarySource": "cached",
                "digest": cached_digest["digest"],
                "articles": cached_digest["articles"],
            }

    try:
        articles = fetch_articles(
            rss_sources,
            category=category,
            language=language,
            limit=12,
        )
    except RssServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    digest, summary_source = create_digest_with_status(
        articles,
        language=language,
        category=category,
    )
    source_articles = _articles_for_response(articles)
    generated_at = save_digest_with_articles(language, category, digest, source_articles)
    sources_used = _sources_used(source_articles)

    print(
        "WeeklyDigest response: "
        f"language={language} category={category} cache=not_used "
        f"articles={len(source_articles)} sources={', '.join(sources_used) or 'none'} "
        f"summary_source={summary_source}",
        flush=True,
    )

    return {
        "category": category,
        "language": language,
        "generatedAt": generated_at,
        "fromCache": False,
        "cacheAgeDays": None,
        "cacheStatus": "freshly_generated",
        "articlesCount": len(source_articles),
        "sourcesUsed": sources_used,
        "summarySource": summary_source,
        "digest": digest,
        "articles": source_articles,
    }
