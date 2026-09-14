from app.services.matching import calculate_match_score

def test_positive_score():
    assert calculate_match_score("python fastapi postgresql docker aws", "Python FastAPI PostgreSQL backend") > 0

def test_zero_score_without_overlap():
    assert calculate_match_score("python fastapi", "java spring kafka") == 0
