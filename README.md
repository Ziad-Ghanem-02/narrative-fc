# Story-Teller

A Django REST backend that runs an agentic pipeline to generate data-backed stories
about FIFA Men's World Cups. The pipeline uses an OpenAI-compatible LLM and reads
football data from the configured Neon PostgreSQL database.

## Project structure

```text
config/                 Django configuration
stories/                REST endpoint and request validation
story_pipeline/         Agent graph, PostgreSQL access, LLM client, and agents
manage.py               Django command entry point
Procfile                Render/Railway web process
render.yaml             Render blueprint
```

## Requirements

- Python 3.11 or newer
- A Neon PostgreSQL connection string
- An OpenAI-compatible API key and base URL

## Configuration

Create a `.env` file in the repository root:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-llm-provider.example/v1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
```

`DATABASE_URL` must point to PostgreSQL. The backend does not use SQLite or
`Database/worldcup.db`. Set `DJANGO_ALLOWED_HOSTS` to the comma-separated hostnames
used by your deployment.

## Install and run

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run Django:

```powershell
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000`.

## Generate a story

Send a `POST` request to `/api/stories/` with a research question:

```powershell
$body = @{
    question = "Has the competitive gap between traditional football powerhouses and underdog teams decreased in recent FIFA Men's World Cups?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/stories/" `
    -ContentType "application/json" `
    -Body $body
```

The response contains the generated SQL queries, query results, evidence report,
story plan, final story, and frontend-ready chart datasets. No charts are generated
or stored on the server.

```json
{
  "question": "Has the competitive gap decreased?",
  "queries": [{"purpose": "Goals scored comparison", "sql": "SELECT ..."}],
  "results": [{
    "purpose": "Goals scored comparison",
    "sql": "SELECT ...",
    "columns": ["year", "big_teams_goals", "underdogs_goals"],
    "data": [{"year": 2022, "big_teams_goals": 80, "underdogs_goals": 92}]
  }],
  "evidence": "...",
  "plan": "...",
  "story": "...",
  "charts": [{
    "title": "Goals scored comparison",
    "columns": ["year", "big_teams_goals", "underdogs_goals"],
    "data": [{"year": 2022, "big_teams_goals": 80, "underdogs_goals": 92}]
  }]
}
```

## Revise a saved story

Each generated story is persisted in PostgreSQL. The generation response includes
its `id`. Submit a user instruction to create a new revision from the saved
evidence and latest story:

```powershell
$body = @{
    instruction = "Make the tone more optimistic and focus more on the 2014, 2018, and 2022 World Cups."
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/stories/STORY_ID/revisions/" `
    -ContentType "application/json" `
    -Body $body
```

The response includes the revised story, its revision number, and its ID. Retrieve
the latest story and its full revision history with:

```text
GET /api/stories/STORY_ID/
```

## Deploy to Render or Railway

Both platforms detect the included `Procfile` and start the service with Gunicorn.

1. Push the repository to GitHub.
2. Create a new **Web Service** on Render, or a new **Service** on Railway, from
   that repository.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `gunicorn config.wsgi:application`.
5. Configure these environment variables in the platform dashboard:

   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
   OPENAI_API_KEY=your-api-key
   OPENAI_BASE_URL=https://your-llm-provider.example/v1
   DJANGO_SECRET_KEY=a-long-random-secret
   DJANGO_DEBUG=false
   DJANGO_ALLOWED_HOSTS=your-service.onrender.com
   ```

   On Railway, set `DJANGO_ALLOWED_HOSTS` to the public Railway domain. On Render,
   you can alternatively create the service from `render.yaml`; set
   `DJANGO_ALLOWED_HOSTS` to its generated public hostname after the first deploy.

6. Deploy, then send requests to `https://YOUR-DOMAIN/api/stories/`.

## Database migrations and tests

Apply database migrations after deploying:

```powershell
python manage.py migrate
```

Run the test suite against Neon with `--keepdb`. This keeps the temporary PostgreSQL
test database, avoiding connection-pool cleanup conflicts:

```powershell
python manage.py test stories --keepdb
```
