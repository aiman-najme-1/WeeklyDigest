import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4.1-mini").strip()
GITHUB_MODELS_BASE_URL = os.getenv(
    "GITHUB_MODELS_BASE_URL",
    "https://models.github.ai/inference",
).rstrip("/")
AUTH_SECRET = os.getenv("AUTH_SECRET", "weeklydigest-dev-secret").strip()
SPORTS_RU_RSS_URL = os.getenv(
    "SPORTS_RU_RSS_URL",
    "https://www.championat.com/rss/news/",
).strip()
SPORTS_RU_SPORTS_RU_RSS_URL = os.getenv(
    "SPORTS_RU_SPORTS_RU_RSS_URL",
    "https://www.sports.ru/rss/all_news.xml",
).strip()
SPORTS_EN_RSS_URL = os.getenv(
    "SPORTS_EN_RSS_URL",
    "https://feeds.bbci.co.uk/sport/rss.xml?edition=uk",
).strip()
SPORTS_EN_GUARDIAN_RSS_URL = os.getenv(
    "SPORTS_EN_GUARDIAN_RSS_URL",
    "https://www.theguardian.com/sport/rss",
).strip()
SPORTS_EN_YAHOO_RSS_URL = os.getenv(
    "SPORTS_EN_YAHOO_RSS_URL",
    "https://sports.yahoo.com/rss/",
).strip()
ECONOMY_RU_RSS_URL = os.getenv(
    "ECONOMY_RU_RSS_URL",
    "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
).strip()
ECONOMY_RU_KOMMERSANT_RSS_URL = os.getenv(
    "ECONOMY_RU_KOMMERSANT_RSS_URL",
    "https://www.kommersant.ru/RSS/section-economics.xml",
).strip()
ECONOMY_RU_VEDOMOSTI_RSS_URL = os.getenv(
    "ECONOMY_RU_VEDOMOSTI_RSS_URL",
    "https://www.vedomosti.ru/rss/rubric/economics",
).strip()
ECONOMY_EN_RSS_URL = os.getenv(
    "ECONOMY_EN_RSS_URL",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
).strip()
ECONOMY_EN_GUARDIAN_RSS_URL = os.getenv(
    "ECONOMY_EN_GUARDIAN_RSS_URL",
    "https://www.theguardian.com/business/rss",
).strip()
SCIENCE_RU_RSS_URL = os.getenv(
    "SCIENCE_RU_RSS_URL",
    "https://nplus1.ru/rss",
).strip()
SCIENCE_RU_INDICATOR_RSS_URL = os.getenv(
    "SCIENCE_RU_INDICATOR_RSS_URL",
    "https://indicator.ru/exports/rss",
).strip()
SCIENCE_EN_RSS_URL = os.getenv(
    "SCIENCE_EN_RSS_URL",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
).strip()
SCIENCE_EN_GUARDIAN_RSS_URL = os.getenv(
    "SCIENCE_EN_GUARDIAN_RSS_URL",
    "https://www.theguardian.com/science/rss",
).strip()
TECHNOLOGY_RU_RSS_URL = os.getenv(
    "TECHNOLOGY_RU_RSS_URL",
    "https://www.ixbt.com/export/news.rss",
).strip()
TECHNOLOGY_RU_HABR_RSS_URL = os.getenv(
    "TECHNOLOGY_RU_HABR_RSS_URL",
    "https://habr.com/ru/rss/news/?fl=ru",
).strip()
TECHNOLOGY_RU_3DNEWS_RSS_URL = os.getenv(
    "TECHNOLOGY_RU_3DNEWS_RSS_URL",
    "https://3dnews.ru/news/rss/",
).strip()
TECHNOLOGY_EN_RSS_URL = os.getenv(
    "TECHNOLOGY_EN_RSS_URL",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
).strip()
TECHNOLOGY_EN_GUARDIAN_RSS_URL = os.getenv(
    "TECHNOLOGY_EN_GUARDIAN_RSS_URL",
    "https://www.theguardian.com/technology/rss",
).strip()
AR_SPORTS_RSS = os.getenv(
    "AR_SPORTS_RSS",
    "https://arabic.cnn.com/api/v1/rss/rss.xml",
).strip()
AR_ECONOMY_RSS = os.getenv(
    "AR_ECONOMY_RSS",
    "https://arabic.cnn.com/api/v1/rss/rss.xml",
).strip()
AR_SCIENCE_RSS = os.getenv(
    "AR_SCIENCE_RSS",
    "https://arabic.cnn.com/api/v1/rss/rss.xml",
).strip()
AR_TECHNOLOGY_RSS = os.getenv(
    "AR_TECHNOLOGY_RSS",
    "https://arabic.cnn.com/api/v1/rss/rss.xml",
).strip()


def source(name, url):
    return {"name": name, "url": url}

RSS_FEEDS = {
    "ru": {
        "sports": [
            source("Championat", SPORTS_RU_RSS_URL),
            source("Sports.ru", SPORTS_RU_SPORTS_RU_RSS_URL),
        ],
        "economy": [
            source("RBC", ECONOMY_RU_RSS_URL),
            source("Kommersant", ECONOMY_RU_KOMMERSANT_RSS_URL),
            source("Vedomosti", ECONOMY_RU_VEDOMOSTI_RSS_URL),
        ],
        "science": [
            source("N+1", SCIENCE_RU_RSS_URL),
            source("Indicator", SCIENCE_RU_INDICATOR_RSS_URL),
        ],
        "technology": [
            source("iXBT", TECHNOLOGY_RU_RSS_URL),
            source("Habr", TECHNOLOGY_RU_HABR_RSS_URL),
            source("3DNews", TECHNOLOGY_RU_3DNEWS_RSS_URL),
        ],
    },
    "en": {
        "sports": [
            source("BBC Sport", SPORTS_EN_RSS_URL),
            source("Guardian Sport", SPORTS_EN_GUARDIAN_RSS_URL),
            source("Yahoo Sports", SPORTS_EN_YAHOO_RSS_URL),
        ],
        "economy": [
            source("BBC Business", ECONOMY_EN_RSS_URL),
            source("Guardian Business", ECONOMY_EN_GUARDIAN_RSS_URL),
        ],
        "science": [
            source("BBC Science", SCIENCE_EN_RSS_URL),
            source("Guardian Science", SCIENCE_EN_GUARDIAN_RSS_URL),
        ],
        "technology": [
            source("BBC Technology", TECHNOLOGY_EN_RSS_URL),
            source("Guardian Technology", TECHNOLOGY_EN_GUARDIAN_RSS_URL),
        ],
    },
    "ar": {
        "sports": [
            source("Arabic Sports", AR_SPORTS_RSS),
        ],
        "economy": [
            source("Arabic Economy", AR_ECONOMY_RSS),
        ],
        "science": [
            source("Arabic Science", AR_SCIENCE_RSS),
        ],
        "technology": [
            source("Arabic Technology", AR_TECHNOLOGY_RSS),
        ],
    },
}

FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


def has_github_token():
    return bool(
        GITHUB_TOKEN
        and GITHUB_TOKEN.strip()
        and GITHUB_TOKEN.strip() != "your_github_models_token_here"
    )
