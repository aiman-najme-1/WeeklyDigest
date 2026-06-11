import requests

from config import GITHUB_MODEL, GITHUB_MODELS_BASE_URL, GITHUB_TOKEN, has_github_token


class MissingGitHubTokenError(Exception):
    """Raised when the GitHub Models token is not configured."""


class SummarizerServiceError(Exception):
    """Raised when the GitHub Models API cannot produce a digest."""


CATEGORY_NAMES = {
    "ru": {
        "sports": "спорт",
        "economy": "экономика",
        "science": "наука",
        "technology": "технологии",
    },
    "en": {
        "sports": "sports",
        "economy": "economy",
        "science": "science",
        "technology": "technology",
    },
    "ar": {
        "sports": "الرياضة",
        "economy": "الاقتصاد",
        "science": "العلوم",
        "technology": "التكنولوجيا",
    },
}

LANGUAGE_NAMES = {
    "ru": "Russian",
    "en": "English",
    "ar": "Arabic",
}

SOURCE_ONLY_RULE = (
    "Create a weekly news digest using only the articles provided below. "
    "Do not add facts that are not present in the articles. "
    "Do not use your own knowledge. "
    "If information is not in the articles, do not mention it."
)


def _category_name(language, category):
    return CATEGORY_NAMES.get(language, CATEGORY_NAMES["en"]).get(category, category)


def _short_text(value, max_length=260):
    if not value:
        return ""

    if len(value) <= max_length:
        return value

    return value[:max_length].rsplit(" ", 1)[0] + "..."


def _build_user_prompt(articles, language, category):
    news_blocks = []

    for index, article in enumerate(articles, start=1):
        if language == "en":
            date_label = "Date"
            source_label = "Source"
            brief_label = "Brief"
            no_date = "not specified"
            no_summary = "description is missing"
        elif language == "ar":
            date_label = "التاريخ"
            source_label = "المصدر"
            brief_label = "ملخص"
            no_date = "غير محدد"
            no_summary = "لا يوجد وصف"
        else:
            date_label = "Дата"
            source_label = "Источник"
            brief_label = "Кратко"
            no_date = "не указана"
            no_summary = "описание отсутствует"

        news_blocks.append(
            "\n".join(
                [
                    f"{index}. {article['title']}",
                    f"{source_label}: {article.get('source') or 'Unknown source'}",
                    f"{date_label}: {article.get('published') or no_date}",
                    f"{brief_label}: {article.get('summary') or no_summary}",
                ]
            )
        )

    category_name = _category_name(language, category)

    if language == "en":
        task = (
            f"Using the following {category_name} news, write a coherent weekly digest "
            "in English only. Write naturally in paragraphs, not as a dry list. "
            "Highlight the most important events and keep the tone clear for a student demo. "
            "Length: about 220-350 words."
        )
    elif language == "ar":
        task = (
            f"باستخدام الأخبار التالية عن {category_name}، اكتب ملخصا أسبوعيا واضحا "
            "باللغة العربية فقط. اكتب بشكل طبيعي في فقرات قصيرة، وليس كقائمة جافة. "
            "ركز على أهم الأحداث واجعل الأسلوب مناسبا لعرض جامعي. الطول: حوالي 220-350 كلمة."
        )
    else:
        task = (
            f"На основе следующих новостей по теме «{category_name}» составь связный "
            "еженедельный дайджест на русском языке. Пиши естественно, абзацами, "
            "без сухого списка. Выдели самые важные события и сохрани понятный тон "
            "для студенческой демо-презентации. Объем: примерно 220-350 слов."
        )

    return SOURCE_ONLY_RULE + "\n\n" + task + "\n\n" + "\n\n".join(news_blocks)


def _build_system_prompt(language, category):
    category_name = _category_name(language, category)

    if language == "en":
        return (
            f"You write short, clear weekly {category_name} news digests in English. "
            "Use only the articles provided by the user."
        )

    if language == "ar":
        return (
            f"You write short, clear weekly {category_name} news digests in Arabic. "
            "Use only the articles provided by the user."
        )

    return (
        f"Ты пишешь короткие и понятные еженедельные дайджесты по теме "
        f"«{category_name}» на русском языке. Используй только статьи, "
        "которые предоставил пользователь."
    )


def create_fallback_digest(articles, language="ru", category="sports"):
    category_name = _category_name(language, category)
    selected_articles = articles[:7]

    if language == "en":
        intro = (
            f"This is a simple weekly {category_name} digest based only on the "
            "provided RSS headlines and article descriptions."
        )
        pieces = []
        for article in selected_articles:
            title = article["title"]
            summary = _short_text(article.get("summary"))
            pieces.append(f"{title}. {summary}" if summary else title)

        return intro + "\n\n" + " ".join(pieces)

    if language == "ar":
        intro = (
            f"هذا ملخص أسبوعي بسيط عن {category_name}، مبني فقط على عناوين "
            "وأوصاف الأخبار من RSS."
        )
        pieces = []
        for article in selected_articles:
            title = article["title"]
            summary = _short_text(article.get("summary"))
            pieces.append(f"{title}. {summary}" if summary else title)

        return intro + "\n\n" + " ".join(pieces)

    intro = (
        f"Это простой еженедельный дайджест по теме «{category_name}», "
        "подготовленный только по заголовкам и описаниям RSS-новостей."
    )
    pieces = []
    for article in selected_articles:
        title = article["title"]
        summary = _short_text(article.get("summary"))
        pieces.append(f"{title}. {summary}" if summary else title)

    return intro + "\n\n" + " ".join(pieces)


def _create_ai_digest(articles, language, category):
    url = f"{GITHUB_MODELS_BASE_URL}/chat/completions"
    payload = {
        "model": GITHUB_MODEL,
        "messages": [
            {
                "role": "system",
                "content": _build_system_prompt(language, category),
            },
            {
                "role": "user",
                "content": _build_user_prompt(articles, language, category),
            },
        ],
        "temperature": 0.4,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=40,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise SummarizerServiceError(
            "Could not get a response from GitHub Models API."
        ) from exc
    except ValueError as exc:
        raise SummarizerServiceError(
            "GitHub Models API returned an unexpected response format."
        ) from exc

    try:
        digest = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise SummarizerServiceError(
            "GitHub Models API did not return digest text."
        ) from exc

    if not digest:
        raise SummarizerServiceError("GitHub Models API returned an empty digest.")

    return digest


def create_digest_with_status(articles, language="ru", category="sports"):
    if not has_github_token():
        return (
            create_fallback_digest(articles, language=language, category=category),
            "fallback_missing_token",
        )

    try:
        return _create_ai_digest(articles, language=language, category=category), "ai"
    except SummarizerServiceError as exc:
        print(f"WeeklyDigest: AI summary failed, using fallback. {exc}", flush=True)
        return (
            create_fallback_digest(articles, language=language, category=category),
            "fallback_ai_error",
        )


def create_digest(articles, language="ru", category="sports"):
    digest, _summary_source = create_digest_with_status(
        articles,
        language=language,
        category=category,
    )
    return digest


def create_sports_digest(articles, language="ru"):
    return create_digest(articles, language=language, category="sports")
