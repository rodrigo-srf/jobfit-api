from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_complete_jobfit_flow():
    register = client.post(
        "/auth/register",
        json={
            "email": "portfolio@example.com",
            "password": "strongpass123",
            "full_name": "Portfolio User",
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "portfolio@example.com", "password": "strongpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = auth_headers(token)

    profile = client.put(
        "/profile",
        headers=headers,
        json={
            "skills": "Python, FastAPI, PostgreSQL, Docker, AWS",
            "summary": "Backend developer",
        },
    )
    assert profile.status_code == 200

    job = client.post(
        "/jobs",
        headers=headers,
        json={
            "title": "Python Backend Developer",
            "company": "Example Tech",
            "description": "Build REST APIs with Python and FastAPI.",
            "requirements": "Python FastAPI PostgreSQL Docker AWS",
            "location": "Remote",
            "salary_min": 5000,
            "salary_max": 8000,
        },
    )
    assert job.status_code == 201
    job_data = job.json()
    assert job_data["match_score"] == 100.0

    analysis = client.get(f"/jobs/{job_data['id']}/analysis", headers=headers)
    assert analysis.status_code == 200
    assert analysis.json()["missing_skills"] == []

    application = client.post(
        "/applications",
        headers=headers,
        json={"job_id": job_data["id"], "stage": "applied", "notes": "Submitted"},
    )
    assert application.status_code == 201
    application_id = application.json()["id"]

    update = client.patch(
        f"/applications/{application_id}",
        headers=headers,
        json={"stage": "interview"},
    )
    assert update.status_code == 200
    assert update.json()["stage"] == "interview"

    stats = client.get("/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["jobs"] == 1
    assert stats.json()["applications"] == 1
    assert stats.json()["interviews"] == 1
