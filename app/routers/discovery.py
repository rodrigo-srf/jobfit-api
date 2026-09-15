import asyncio
import re
from datetime import datetime, timezone
from html import unescape

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/discover", tags=["discovery"])

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"


def _plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _matches_query(job: dict, q: str) -> bool:
    if not q:
        return True
    haystack = " ".join(
        [
            job.get("title", ""),
            job.get("company", ""),
            job.get("description", ""),
            job.get("requirements", ""),
            job.get("category", ""),
        ]
    ).lower()
    return all(term in haystack for term in q.lower().split())


def _dedupe(jobs: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    result = []
    for job in jobs:
        key = (_normalize(job.get("title", "")), _normalize(job.get("company", "")))
        if key in seen:
            continue
        seen.add(key)
        result.append(job)
    return result


def _sort_jobs(jobs: list[dict], sort: str) -> list[dict]:
    if sort == "company":
        return sorted(jobs, key=lambda j: _normalize(j.get("company", "")))
    if sort == "title":
        return sorted(jobs, key=lambda j: _normalize(j.get("title", "")))
    return sorted(jobs, key=lambda j: j.get("published_at") or "", reverse=True)


async def _fetch_remotive(client: httpx.AsyncClient, q: str) -> list[dict]:
    response = await client.get(REMOTIVE_API_URL, params={"search": q or "remote"})
    response.raise_for_status()
    jobs = []
    for item in response.json().get("jobs", []):
        jobs.append(
            {
                "external_id": f"remotive:{item.get('id')}",
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "location": item.get("candidate_required_location") or "Remote",
                "description": _plain_text(item.get("description", ""))[:2200],
                "requirements": ", ".join(item.get("tags") or []),
                "salary": item.get("salary") or "",
                "job_type": item.get("job_type") or "",
                "category": item.get("category") or "",
                "published_at": item.get("publication_date"),
                "url": item.get("url"),
                "source": "Remotive",
                "remote": True,
            }
        )
    return jobs


async def _fetch_arbeitnow(client: httpx.AsyncClient) -> list[dict]:
    response = await client.get(ARBEITNOW_API_URL)
    response.raise_for_status()
    jobs = []
    for item in response.json().get("data", []):
        created_at = item.get("created_at")
        published = None
        if created_at:
            try:
                published = datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()
            except (TypeError, ValueError, OSError):
                published = None
        tags = item.get("tags") or []
        job_types = item.get("job_types") or []
        jobs.append(
            {
                "external_id": f"arbeitnow:{item.get('slug')}",
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "location": item.get("location") or ("Remote" if item.get("remote") else ""),
                "description": _plain_text(item.get("description", ""))[:2200],
                "requirements": ", ".join(tags),
                "salary": "",
                "job_type": ", ".join(job_types),
                "category": ", ".join(tags),
                "published_at": published,
                "url": item.get("url"),
                "source": "Arbeitnow",
                "remote": bool(item.get("remote")),
            }
        )
    return jobs


@router.get("/jobs")
async def discover_jobs(
    q: str = Query("python", min_length=0, max_length=80),
    source: str = Query("all", pattern="^(all|remotive|arbeitnow)$"),
    location: str = Query("", max_length=80),
    category: str = Query("", max_length=80),
    job_type: str = Query("", max_length=80),
    remote_only: bool = Query(True),
    sort: str = Query("recent", pattern="^(recent|company|title)$"),
    limit: int = Query(18, ge=1, le=50),
):
    try:
        async with httpx.AsyncClient(timeout=14.0, follow_redirects=True) as client:
            tasks = []
            if source in {"all", "remotive"}:
                tasks.append(_fetch_remotive(client, q))
            if source in {"all", "arbeitnow"}:
                tasks.append(_fetch_arbeitnow(client))
            batches = await asyncio.gather(*tasks, return_exceptions=True)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Job providers are temporarily unavailable") from exc

    jobs: list[dict] = []
    provider_errors = []
    for batch in batches:
        if isinstance(batch, Exception):
            provider_errors.append(type(batch).__name__)
            continue
        jobs.extend(batch)

    if not jobs and provider_errors:
        raise HTTPException(status_code=502, detail="All job providers are temporarily unavailable")

    filtered = []
    for job in jobs:
        if not _matches_query(job, q):
            continue
        if remote_only and not job.get("remote"):
            continue
        if location and location.lower() not in (job.get("location") or "").lower():
            continue
        if category and category.lower() not in (job.get("category") or "").lower():
            continue
        if job_type and job_type.lower() not in (job.get("job_type") or "").lower():
            continue
        filtered.append(job)

    filtered = _sort_jobs(_dedupe(filtered), sort)[:limit]
    return {
        "query": q,
        "count": len(filtered),
        "source": source,
        "providers": ["Remotive", "Arbeitnow"] if source == "all" else [source.title()],
        "provider_errors": provider_errors,
        "jobs": filtered,
    }
