const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const SUPPORTED_LANGUAGES = new Set(["ru", "en", "ar"]);
const SUPPORTED_CATEGORIES = new Set([
  "sports",
  "economy",
  "science",
  "technology",
]);

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = "Request failed. Please try again later.";

    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      }
    } catch {
      message = "Could not connect to the server.";
    }

    throw new Error(message);
  }

  return response.json();
}

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function fetchDigest(language, category) {
  const digestLanguage = SUPPORTED_LANGUAGES.has(language) ? language : "ru";
  const digestCategory = SUPPORTED_CATEGORIES.has(category)
    ? category
    : "sports";

  const response = await fetch(
    `${API_BASE_URL}/api/${digestLanguage}/${digestCategory}/digest`,
  );

  if (!response.ok) {
    let message = "Failed to create digest. Please try again later.";

    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      }
    } catch {
      message = "Could not connect to the digest server.";
    }

    throw new Error(message);
  }

  return response.json();
}

export function fetchSportsDigest(language) {
  return fetchDigest(language, "sports");
}

export function fetchRussianSportsDigest() {
  return fetchDigest("ru", "sports");
}

export function registerUser(data) {
  return requestJson("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function loginUser(data) {
  return requestJson("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function fetchMe(token) {
  return requestJson("/api/me", {
    headers: authHeaders(token),
  });
}

export function fetchPreferences(token) {
  return requestJson("/api/me/preferences", {
    headers: authHeaders(token),
  });
}

export function updatePreferences(token, data) {
  return requestJson("/api/me/preferences", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
}

export function fetchSavedArticles(token) {
  return requestJson("/api/me/saved-articles", {
    headers: authHeaders(token),
  });
}

export function saveArticle(token, article) {
  return requestJson("/api/me/saved-articles", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(article),
  });
}

export function deleteSavedArticle(token, articleId) {
  return requestJson(`/api/me/saved-articles/${articleId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}
