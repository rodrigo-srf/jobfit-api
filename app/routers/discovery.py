import re
from html import unescape

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/discover", tags=["discovery"])

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


def _plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


@router.get("/jobs")
async def discover_jobs(
    q: str = Query("python", min_length=2, max_length=80),
    limit: int = Query(12, ge=1, le=30),
):
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(REMOTIVE_API_URL, params={"search": q})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Remote job provider is temporarily unavailable") from exc

    payload = response.json()
    jobs = []
    for item in payload.get("jobs", [])[:limit]:
        jobs.append(
            {
                "external_id": item.get("id"),
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "location": item.get("candidate_required_location") or "Remote",
                "description": _plain_text(item.get("description", ""))[:1800],
                "requirements": ", ".join(item.get("tags") or []),
                "salary": item.get("salary") or "",
                "job_type": item.get("job_type") or "",
                "category": item.get("category") or "",
                "published_at": item.get("publication_date"),
                "url": item.get("url"),
                "source": "Remotive",
            }
        )

    return {
        "query": q,
        "count": len(jobs),
        "source": "Remotive",
        "source_url": "https://remotive.com/",
        "jobs": jobs,
    }
