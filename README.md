# JobFit API 🚀

Production-style backend for tracking job opportunities, applications, and profile-to-job compatibility.

Built with **FastAPI, SQLAlchemy, PostgreSQL, JWT, Docker, pytest, GitHub Actions, and an interactive web dashboard**.

## Features

- Interactive browser dashboard at `/`
- JWT registration and login
- Technical profile with skills
- Job opportunity CRUD
- Automatic profile-to-job match score
- Application pipeline tracking
- PostgreSQL or SQLite
- Docker Compose
- Automated tests
- GitHub Actions CI
- Swagger/OpenAPI documentation

## Why this project

Job seekers often lose track of applications and apply blindly to roles that do not match their current skills. JobFit centralizes opportunities and gives each saved job a deterministic compatibility score based on the user's technical profile.

The project now includes a visual dashboard so recruiters and reviewers can understand the core idea immediately without needing to start with raw API requests.

## Architecture

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── security.py
├── dependencies.py
├── static/
│   └── index.html
├── routers/
│   ├── auth.py
│   ├── profile.py
│   ├── jobs.py
│   └── applications.py
└── services/
    └── matching.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:

- Dashboard: `http://localhost:8000/`
- Swagger API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Interactive dashboard

The root page provides a simple visual demonstration of the profile-to-job matching concept. Enter a skill set and a job's requirements, then calculate an explainable compatibility score directly in the browser.

The backend remains available through the REST API for authentication, persistent job storage, application tracking, and database operations.

## Docker + PostgreSQL

```bash
docker compose up --build
```

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Interactive dashboard |
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Receive JWT |
| GET/PUT | `/profile` | Read/update profile |
| POST/GET | `/jobs` | Save/list jobs |
| POST | `/jobs/{id}/rescore` | Recalculate fit |
| POST/GET | `/applications` | Create/list applications |
| PATCH | `/applications/{id}` | Update application stage |
| GET | `/health` | Health check |

## Match engine

The first version intentionally uses deterministic token matching instead of a paid LLM. Skills and job text are normalized and aliases such as `Postgres → PostgreSQL` are handled before overlap is calculated.

That makes the service cheap, explainable, and easy to test. A later version can add embeddings or an LLM explanation layer.

## Tests

```bash
pytest -q
```

## Roadmap

- Alembic migrations
- semantic embeddings
- LLM explanation of match score
- filters by salary, seniority, and remote location
- follow-up reminders
- CSV export
- richer dashboard connected to authenticated user data
- email import
- refresh tokens

## What this demonstrates

Backend API design, authentication, authorization, relational modeling, business logic, testing, containerization, CI/CD fundamentals, applied text matching, and a lightweight interactive frontend.

## Author

Rodrigo Serafim  
https://github.com/rodrigo-srf
