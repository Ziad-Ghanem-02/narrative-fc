# Story-Teller

Story-Teller is a full-stack World Cup data storytelling application. It compares an AI-generated **agentic story** with a **human-written story**, supports interactive evidence charts, and collects anonymous reader evaluations.

## Project Structure

```text
backend/    Django REST API, story pipeline, migrations, and worker
frontend/   Next.js application, story experiences, charts, and evaluations
```

## Features

- Agentic story generation through a queued Django job and OpenAI-compatible LLM.
- Human-written story with charts and references backed by hosted Neon PostgreSQL data.
- Interactive Recharts visualizations rendered from backend chart specifications.
- Story rewriting with persisted revisions.
- Anonymous ratings for clarity, trustworthiness, evidence, insightfulness, and engagement.
- `/reviews` page with aggregate ratings, preferences, and anonymous written feedback.
- World Cup map and country-level summary data.

## Requirements

- Python 3.11+
- Node.js and npm
- A hosted Neon PostgreSQL database
- An OpenAI-compatible API key and base URL

The application uses the hosted database configured by `DATABASE_URL`. It does not use the ignored `backend/Database/worldcup.db` SQLite artifact or any local football database.

## Environment

Create `backend/.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-llm-provider.example/v1
DJANGO_SECRET_KEY=development-secret
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
```

Create `frontend/.env.local` when the backend is not running at the default address:

```env
BACKEND_API_URL=http://127.0.0.1:8000
```

## Local Development

Run the backend API:

```powershell
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Run the story worker in a second terminal:

```powershell
cd backend
python manage.py process_story_jobs
```

Run the frontend in a third terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Routes

### Frontend

- `/` - landing page and World Cup map
- `/stories` - agentic and human-written story comparison with visuals
- `/evaluation` - anonymous evaluation form
- `/reviews` - aggregate ratings and anonymous reviews
- `/dev-chart-test` - chart renderer development page

### Backend API

- `POST /api/story-jobs/` - queue story generation
- `GET /api/story-jobs/<job_id>/` - poll a generation job
- `GET /api/stories/<story_id>/` - retrieve a saved story
- `POST /api/stories/<story_id>/revisions/` - rewrite a saved story
- `GET /api/world-cup/map-summary/` - retrieve map data
- `GET /api/world-cup/human-story-visuals/` - retrieve human-story visuals
- `POST /api/evaluations/` - submit an anonymous evaluation
- `GET /api/evaluations/results/` - retrieve aggregate ratings and anonymous reviews

The Next.js backend proxy exposes Django API routes under `/api/backend/*` to the browser.

## Database and Tests

Apply migrations whenever the backend schema changes:

```powershell
cd backend
python manage.py migrate
```

Run backend tests against the configured Neon database:

```powershell
cd backend
python manage.py test stories --keepdb
```

Build the frontend:

```powershell
cd frontend
npm run build
```

## Deployment

Render configuration is in `backend/render.yaml`. It runs migrations as a release command and defines separate web and worker services. The included `backend/Procfile` applies migrations before starting Gunicorn for platforms that use Procfiles.

Set `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` in both deployed backend services.

For a Vercel backend deployment, set these project environment variables before
redeploying:

```env
DJANGO_ALLOWED_HOSTS=story-teller-teal.vercel.app
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=a-long-random-secret
```

Vercel also provides `VERCEL_URL`; Django automatically adds that hostname to
`ALLOWED_HOSTS`. Keep `DJANGO_ALLOWED_HOSTS` configured explicitly for the
production hostname and any custom domain.
