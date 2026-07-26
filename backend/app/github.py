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


_GRAPHQL_URL = "https://api.github.com/graphql"

_STREAK_QUERY = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def get_stats() -> dict:
    """Current daily contribution streak.

    Computed from the same contribution-calendar data behind GitHub's own
    profile page, via GraphQL (`viewer.contributionsCollection`) — so it
    always matches what a visitor would see checking the profile directly.
    Requires GITHUB_KEY (GraphQL has no unauthenticated access); returns 0
    without one.
    """
    with _lock:
        entry = _cache.get("stats")
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]

    result = {"current_streak": 0}
    if not settings.github_key:
        return result

    now = datetime.now(timezone.utc)
    one_year_ago = now - relativedelta.relativedelta(years=1)
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(
                _GRAPHQL_URL,
                json={
                    "query": _STREAK_QUERY,
                    "variables": {
                        "from": one_year_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "to": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                },
                headers={"Authorization": f"Bearer {settings.github_key}"},
            )
            resp.raise_for_status()
            weeks = resp.json()["data"]["viewer"]["contributionsCollection"][
                "contributionCalendar"
            ]["weeks"]
            days = [day for week in weeks for day in week["contributionDays"]]

            streak = 0
            i = len(days) - 1
            if days and days[i]["contributionCount"] == 0:
                i -= 1  # today doesn't break the streak until it's fully over
            while i >= 0 and days[i]["contributionCount"] > 0:
                streak += 1
                i -= 1
            result = {"current_streak": streak}
    except Exception:
        with _lock:
            prev = _cache.get("stats")
        return prev["value"] if prev else result

    with _lock:
        _cache["stats"] = {"value": result, "ts": time.monotonic()}
    return result
