import re
from datetime import UTC, datetime, timedelta
from email import policy
from email.message import Message
from email.parser import BytesParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup

from jobalert.models import Job

TRACKING_KEYS = ("url", "dest", "destination", "redirect", "redirectUrl")


def _html(message: Message) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/html":
                return part.get_content()
    return message.get_content() if message.get_content_type() == "text/html" else ""


def _clean_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in TRACKING_KEYS:
        if query.get(key):
            candidate = unquote(query[key][0])
            if candidate.startswith("http"):
                return candidate
    return url


def _source(sender: str) -> str:
    sender = sender.lower()
    if "linkedin" in sender:
        return "LinkedIn"
    if "indeed" in sender:
        return "Indeed"
    if "naukri" in sender:
        return "Naukri"
    return "Other"


def _received(message: Message) -> datetime:
    from email.utils import parsedate_to_datetime

    value = message.get("Date")
    parsed = parsedate_to_datetime(value) if value else datetime.now(UTC)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_message(message: Message) -> list[Job]:
    soup = BeautifulSoup(_html(message), "html.parser")
    received = _received(message)
    source = _source(message.get("From", ""))
    jobs: list[Job] = []
    seen: set[str] = set()
    for link in soup.find_all("a", href=True):
        title = " ".join(link.get_text(" ", strip=True).split())
        url = _clean_url(link["href"])
        if len(title) < 4 or not url.startswith("http") or url in seen:
            continue
        context = " ".join(link.parent.get_text(" ", strip=True).split())
        if not re.search(
            r"(?i)devops|site reliability|\bsre\b|cloud engineer|platform engineer|"
            r"infrastructure|kubernetes|build.{0,5}release",
            title + " " + context,
        ):
            continue
        seen.add(url)
        company = link.get("data-company", "Not mentioned")
        location = link.get("data-location", "Not mentioned")
        experience_match = re.search(
            r"(?i)(\d+)\s*(?:-|to)\s*(\d+)\s*years?|(?:experience\s*:?)\s*(\d+)\+?\s*years?",
            context,
        )
        experience = experience_match.group(0) if experience_match else "Not mentioned"
        posted_match = re.search(r"(?i)(\d+)\s*hours?\s*ago", context)
        posted = received - timedelta(hours=int(posted_match.group(1))) if posted_match else None
        jobs.append(
            Job(
                title,
                company,
                location,
                url,
                source,
                received,
                experience,
                context,
                posted,
                bool(posted),
            )
        )
    return jobs


def parse_eml(path: Path) -> list[Job]:
    with path.open("rb") as handle:
        return parse_message(BytesParser(policy=policy.default).parse(handle))
