# JobFit API 🚀

Production-style backend for tracking job opportunities, applications, and profile-to-job compatibility.

Built with **FastAPI, SQLAlchemy, PostgreSQL, JWT, Docker, pytest, and GitHub Actions**.

## Features

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

## Architecture

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── security.py
├── dependencies.py
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

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Docker + PostgreSQL

```bash
docker compose up --build
```

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
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
- frontend dashboard
- email import
- refresh tokens

## What this demonstrates

Backend API design, authentication, authorization, relational modeling, business logic, testing, containerization, CI/CD fundamentals, and applied text matching.

## Author

Rodrigo Serafim  
https://github.com/rodrigo-srf
