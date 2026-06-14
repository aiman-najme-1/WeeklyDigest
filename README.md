# WeeklyDigest MVP

WeeklyDigest is a university-project MVP for weekly news digests.

The app has:

- Frontend: React + Vite
- Backend: FastAPI
- Languages: Russian, English, Arabic
- Categories: Sports, Economy, Science, Technology
- RSS news sources
- Optional GitHub Models summarization
- Fallback summaries when `GITHUB_TOKEN` is missing
- SQLite cache for generated digests
- Simple personal account with register/login, preferences, and saved articles

## Backend

```powershell
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

Digest endpoint format:

```text
GET /api/{language}/{category}/digest
```

Supported examples:

```text
/api/ru/sports/digest
/api/ru/economy/digest
/api/ru/science/digest
/api/ru/technology/digest
/api/en/sports/digest
/api/en/economy/digest
/api/en/science/digest
/api/en/technology/digest
/api/ar/sports/digest
/api/ar/economy/digest
/api/ar/science/digest
/api/ar/technology/digest
```

To ignore the 7-day cache and generate a new digest:

```text
/api/ru/sports/digest?refresh=true
```

## Environment

Put your GitHub Models token in `backend/.env` if you want AI summaries:

```env
GITHUB_TOKEN=your_token_here
GITHUB_MODEL=openai/gpt-4.1-mini
GITHUB_MODELS_BASE_URL=https://models.github.ai/inference
AUTH_SECRET=change_this_simple_secret_for_local_tokens
```

If the token is missing or set to the placeholder, the backend still works and
creates a simple fallback digest from RSS titles and descriptions.

RSS URLs can also be changed in `backend/.env`. See `backend/.env.example` for all available variables.

Auth endpoints:

```text
POST /api/auth/register
POST /api/auth/login
GET /api/me
GET /api/me/preferences
PUT /api/me/preferences
GET /api/me/saved-articles
POST /api/me/saved-articles
DELETE /api/me/saved-articles/{id}
```

After login/register, protected endpoints use a simple bearer token:

```text
Authorization: Bearer your_token_here
```

## Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

If port `5173` is busy, run:

```powershell
npm run dev -- --host 127.0.0.1 --port 5174
```

If the backend runs on a different URL, create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Notes

- The backend stores cached digests in `backend/data/weekly_digest.db`.
- Cached digests are reused for 7 days unless `refresh=true` is used.
- Login/register is included for a simple personal cabinet.
- Users can save preferred language/category and save article links.
- Do not commit `backend/.env`, `backend/.venv`, `frontend/node_modules`, `frontend/dist`, or `backend/data/*.db`.
- RSS availability depends on the external news websites.
- AI output depends on the configured GitHub Models token and model access.
