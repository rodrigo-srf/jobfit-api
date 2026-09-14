import re

STOPWORDS = {"and","or","the","a","an","to","of","with","for","in","de","da","do","e","ou","com","para","em"}
ALIASES = {"postgres":"postgresql","postgre":"postgresql","js":"javascript","py":"python","aws bedrock":"bedrock","amazon bedrock":"bedrock"}

def normalize(text: str) -> set[str]:
    text = text.lower()
    for alias, canonical in ALIASES.items():
        text = text.replace(alias, canonical)
    tokens = re.findall(r"[a-z0-9+#.\-]+", text)
    return {t for t in tokens if len(t) > 1 and t not in STOPWORDS}

def calculate_match_score(profile_skills: str, job_text: str) -> float:
    profile = normalize(profile_skills)
    job = normalize(job_text)
    if not job:
        return 0.0
    return round(min((len(profile & job) / len(job)) * 100, 100.0), 2)
