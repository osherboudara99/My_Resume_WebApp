"""Cached GitHub repos proxy.

Keeps the GitHub token server-side (avoids the 60/hr unauthenticated limit and
never exposes the token to the browser) and caches the assembled repo list so we
don't hammer the GitHub API on every page load.
"""

import threading
import time
from datetime import datetime, timezone

import httpx
from dateutil import relativedelta

from .config import get_settings

settings = get_settings()

_CACHE_TTL = 3600  # 1 hour
_lock = threading.Lock()
_cache: dict[str, dict] = {}


def _headers() -> dict[str, str]:
    return {"Authorization": f"token {settings.github_key}"} if settings.github_key else {}


def _humanize(ts: str) -> tuple[str, str]:
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    human = dt.strftime("%B %d, %Y")
    delta = relativedelta.relativedelta(datetime.now(timezone.utc), dt)
    if delta.years:
        rel = f"{delta.years} year{'s' if delta.years > 1 else ''} ago"
    elif delta.months:
        rel = f"{delta.months} month{'s' if delta.months > 1 else ''} ago"
    elif delta.days:
        rel = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.hours:
        rel = f"{delta.hours} hour{'s' if delta.hours > 1 else ''} ago"
    elif delta.minutes:
        rel = f"{delta.minutes} minute{'s' if delta.minutes > 1 else ''} ago"
    else:
        rel = "just now"
    return human, rel


def _fetch_languages(client: httpx.Client, owner: str, repo: str) -> list[str]:
    try:
        resp = client.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages", headers=_headers()
        )
        if resp.status_code == 200:
            return list(resp.json().keys())
    except Exception:
        pass
    return []


def get_repos() -> list[dict]:
    with _lock:
        entry = _cache.get("repos")
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]

    username = settings.github_username
    result: list[dict] = []
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(
                f"https://api.github.com/users/{username}/repos"
                "?per_page=100&sort=updated",
                headers=_headers(),
            )
            resp.raise_for_status()
            for repo in resp.json():
                created_human, created_rel = _humanize(repo["created_at"])
                updated_human, updated_rel = _humanize(repo["updated_at"])
                result.append(
                    {
                        "name": repo["name"],
                        "html_url": repo["html_url"],
                        "description": repo["description"],
                        "language": _fetch_languages(client, username, repo["name"]),
                        "fork": repo["fork"],
                        "stargazers_count": repo["stargazers_count"],
                        "forks_count": repo["forks_count"],
                        "created_at": repo["created_at"],
                        "updated_at": repo["updated_at"],
                        "created_human": created_human,
                        "created_relative": created_rel,
                        "updated_human": updated_human,
                        "updated_relative": updated_rel,
                    }
                )
    except Exception:
        # On failure, serve last-known-good if we have it; else empty.
        with _lock:
            prev = _cache.get("repos")
        return prev["value"] if prev else []

    with _lock:
        _cache["repos"] = {"value": result, "ts": time.monotonic()}
    return result


def _commit_count(client: httpx.Client, username: str, token: str | None) -> int:
    headers = {"Authorization": f"token {token}"} if token else {}
    resp = client.get(
        "https://api.github.com/search/commits",
        params={"q": f"author:{username}"},
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json().get("total_count", 0)


def get_stats() -> dict:
    """Lifetime commit count across every repo the configured token(s) can see.

    Uses the commit search API's `total_count`. A token with only public
    access only counts public commits — give it `repo` scope so private-repo
    commits are included too. If GITHUB_WORK_KEY is set, its account's
    commits are summed in alongside the primary account's.
    """
    with _lock:
        entry = _cache.get("stats")
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]

    result = {"total_commits": 0}
    try:
        with httpx.Client(timeout=20) as client:
            total = _commit_count(client, settings.github_username, settings.github_key)
            if settings.github_work_key:
                total += _commit_count(
                    client, settings.github_work_username, settings.github_work_key
                )
            result = {"total_commits": total}
    except Exception:
        with _lock:
            prev = _cache.get("stats")
        return prev["value"] if prev else result

    with _lock:
        _cache["stats"] = {"value": result, "ts": time.monotonic()}
    return result
