from app.routers.discovery import _dedupe, _matches_query, _sort_jobs


def test_matches_query_requires_all_terms():
    job = {
        "title": "Python Backend Developer",
        "company": "Example",
        "description": "Build APIs",
        "requirements": "FastAPI PostgreSQL",
        "category": "Software",
    }
    assert _matches_query(job, "python fastapi") is True
    assert _matches_query(job, "python java") is False


def test_dedupe_uses_title_and_company():
    jobs = [
        {"title": "Backend Developer", "company": "ACME"},
        {"title": " backend developer ", "company": "acme"},
        {"title": "Backend Developer", "company": "Other"},
    ]
    assert len(_dedupe(jobs)) == 2


def test_sort_jobs_by_company():
    jobs = [
        {"title": "B", "company": "Zulu", "published_at": "2026-01-02"},
        {"title": "A", "company": "Alpha", "published_at": "2026-01-01"},
    ]
    assert _sort_jobs(jobs, "company")[0]["company"] == "Alpha"
