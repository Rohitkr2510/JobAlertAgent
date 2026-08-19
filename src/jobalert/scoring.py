import re
from datetime import UTC, datetime, timedelta

from jobalert.config import Config
from jobalert.models import Job


def score_job(job: Job, config: Config, now: datetime | None = None) -> Job:
    now = now or datetime.now(UTC)
    haystack = f"{job.title} {job.text}".lower()
    reasons: list[str] = []
    score = 0
    if any(term in haystack for term in config.role_keywords):
        score += 30
        reasons.append("role match")
    job.skills = [skill for skill in config.skill_keywords if skill in haystack]
    skill_points = 25 if len(job.skills) >= 3 else min(20, len(job.skills) * 7)
    score += skill_points
    if skill_points:
        reasons.append(f"{len(job.skills)} matching skills")
    years = [int(value) for value in re.findall(r"\d+", job.experience)]
    if not years:
        reasons.append("experience unverified")
    elif max(years) > config.maximum_experience_years:
        score -= 40
        reasons.append("experience above limit")
    elif min(years) <= 3 <= max(years):
        score += 20
        reasons.append("experience fit")
    reference = job.posted_at or job.email_received_at
    if reference >= now - timedelta(hours=config.hours):
        score += 15
        reasons.append("within 24 hours" if job.date_verified else "recent email; date unverified")
    if any(place in job.location.lower() for place in config.preferred_locations):
        score += 10
        reasons.append("preferred location")
    job.score = max(0, min(100, score))
    job.priority = (
        "High Priority"
        if job.score >= config.high_priority_score
        else "Medium Priority"
        if job.score >= config.minimum_score
        else "Needs Review"
    )
    job.reason = ", ".join(reasons)
    return job
