from app.services.matching import analyze_match, calculate_match_score


def test_full_match():
    score = calculate_match_score(
        "Python, FastAPI, PostgreSQL, Docker",
        "Python FastAPI PostgreSQL Docker",
    )
    assert score == 100.0


def test_aliases_are_normalized():
    result = analyze_match("Python, Postgres, JS", "Python PostgreSQL JavaScript")
    assert result["score"] == 100.0
    assert set(result["matched_skills"]) == {"python", "postgresql", "javascript"}


def test_short_aliases_do_not_corrupt_canonical_names():
    result = analyze_match("Python PostgreSQL", "Python PostgreSQL")
    assert set(result["profile_skills"]) == {"python", "postgresql"}
    assert result["score"] == 100.0


def test_missing_skills_are_explained():
    result = analyze_match("Python, FastAPI", "Python FastAPI Docker AWS")
    assert result["score"] == 50.0
    assert set(result["missing_skills"]) == {"docker", "aws"}


def test_empty_job_text():
    result = analyze_match("Python", "")
    assert result["score"] == 0.0
    assert result["required_skills"] == []
