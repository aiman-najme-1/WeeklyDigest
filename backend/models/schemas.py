from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleSource(BaseModel):
    title: str
    url: str
    source: Optional[str] = "Unknown source"
    published: Optional[str] = ""
    publishedAt: Optional[str] = ""
    summary: Optional[str] = ""


class DigestResponse(BaseModel):
    category: str
    language: str
    generatedAt: Optional[str] = ""
    fromCache: Optional[bool] = None
    cacheAgeDays: Optional[float] = None
    cacheStatus: Optional[str] = ""
    articlesCount: Optional[int] = None
    sourcesUsed: List[str] = Field(default_factory=list)
    summarySource: Optional[str] = ""
    digest: str
    articles: List[ArticleSource]


class HealthResponse(BaseModel):
    status: str
    service: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class PreferencesRequest(BaseModel):
    language: str
    category: str


class PreferencesResponse(BaseModel):
    language: str
    category: str


class SavedArticleRequest(BaseModel):
    title: str
    url: str
    source: Optional[str] = "Unknown source"
    published_at: Optional[str] = ""
    publishedAt: Optional[str] = ""


class SavedArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    source: Optional[str] = "Unknown source"
    published_at: Optional[str] = ""
    created_at: str
