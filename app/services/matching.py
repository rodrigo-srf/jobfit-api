import re

STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "with", "for", "in", "on",
    "de", "da", "do", "das", "dos", "e", "ou", "com", "para", "em", "um", "uma",
}

ALIASES = {
    "postgres": "postgresql",
    "postgre": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "aws bedrock": "bedrock",
    "amazon bedrock": "bedrock",
    "restful": "rest",
    "rest api": "rest",
    "rest apis": "rest",
    "ci/cd": "cicd",
    "ci-cd": "cicd",
    "machine-learning": "machinelearning",
    "machine learning": "machinelearning",
}

TECH_SKILLS = {
    "python", "fastapi", "django", "flask", "sql", "postgresql", "mysql", "sqlite",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git", "github", "rest",
    "graphql", "javascript", "typescript", "node.js", "nodejs", "react", "next.js", "nextjs",
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "mlflow",
    "machinelearning", "ai", "llm", "bedrock", "mqtt", "esp32", "redis", "celery",
    "pytest", "cicd", "terraform", "spark", "airflow", "mongodb", "sqlalchemy",
}


def normalize(text: str) -> set[str]:
    text = (text or "").lower()
    # Match aliases as complete terms. Plain string replacement turned
    # "postgresql" into "postgresqlql" and "python" into "pythonthon" because
    # shorter aliases such as "postgres" and "py" also occurred inside the
    # canonical skill names.
    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = rf"(?<![a-z0-9+#.\-]){re.escape(alias)}(?![a-z0-9+#.\-])"
        text = re.sub(pattern, canonical, text)
    tokens = re.findall(r"[a-z0-9+#.\-]+", text)
    return {token for token in tokens if len(token) > 1 and token not in STOPWORDS}


def extract_skills(text: str) -> set[str]:
    tokens = normalize(text)
    technical = {token for token in tokens if token in TECH_SKILLS}
    return technical or tokens


def analyze_match(profile_skills: str, job_text: str) -> dict:
    profile = extract_skills(profile_skills)
    required = extract_skills(job_text)

    if not required:
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "profile_skills": sorted(profile),
            "required_skills": [],
        }

    matched = profile & required
    missing = required - profile
    score = round(min((len(matched) / len(required)) * 100, 100.0), 2)

    return {
        "score": score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "profile_skills": sorted(profile),
        "required_skills": sorted(required),
    }


def calculate_match_score(profile_skills: str, job_text: str) -> float:
    return analyze_match(profile_skills, job_text)["score"]
