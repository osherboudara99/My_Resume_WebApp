"""Cached GitHub repos proxy.

Keeps the GitHub token server-side (avoids the 60/hr unauthenticated limit and
never exposes the token to the browser) and caches the assembled repo list so we
don't hammer the GitHub API on every page load.
"""

import threading
import time
from datetime import datetime, timedelta, timezone

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
                        "homepage": repo.get("homepage") or None,
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


# Event types that count as "real work" for the streak — pushes (to any
# branch, unlike the profile contribution calendar which only counts a
# repo's default branch), PR activity, and issue activity. Deliberately
# excludes noise like WatchEvent (starring a repo) or ForkEvent.
_ACTIVITY_EVENT_TYPES = {
    "PushEvent",
    "PullRequestEvent",
    "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent",
    "IssuesEvent",
    "IssueCommentEvent",
    "CreateEvent",
}

_CONTRIB_QUERY = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def _account_created_date(client: httpx.Client, username: str):
    resp = client.get(f"https://api.github.com/users/{username}", headers=_headers())
    resp.raise_for_status()
    created = resp.json()["created_at"]
    return datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").date()


def _contribution_days(client: httpx.Client, start, end) -> dict[str, int]:
    """Day -> contributionCount for [start, end] (must be <= 1 year), via
    GraphQL. Only counts default-branch commits plus PR/issue activity —
    used solely as a deep-history fallback once the events feed runs out.
    """
    resp = client.post(
        "https://api.github.com/graphql",
        json={
            "query": _CONTRIB_QUERY,
            "variables": {
                "from": f"{start.isoformat()}T00:00:00Z",
                "to": f"{end.isoformat()}T23:59:59Z",
            },
        },
        headers={"Authorization": f"Bearer {settings.github_key}"},
    )
    resp.raise_for_status()
    weeks = resp.json()["data"]["viewer"]["contributionsCollection"]["contributionCalendar"][
        "weeks"
    ]
    return {day["date"]: day["contributionCount"] for week in weeks for day in week["contributionDays"]}


def _extend_streak_past_year(client: httpx.Client, username: str, day) -> int:
    """Continues a streak walk backward from `day` using the GraphQL
    contribution calendar, a year at a time, until a zero-activity day or
    the account's creation date. Only called once the trailing-year window
    is exhausted and the streak is still unbroken at that edge.
    """
    created = _account_created_date(client, username)
    extra = 0
    window_end = day
    while window_end >= created:
        window_start = max(created, window_end - timedelta(days=364))
        counts = _contribution_days(client, window_start, window_end)
        d = window_end
        while d >= window_start:
            if counts.get(d.isoformat(), 0) <= 0:
                return extra
            extra += 1
            d -= timedelta(days=1)
        window_end = window_start - timedelta(days=1)
    return extra


def get_stats() -> dict:
    """Current streak of days with GitHub activity, across every repo the
    token can see — public, private, and org.

    A day counts as active if EITHER of two sources says so: the
    authenticated /users/{username}/events feed (catches pushes to any
    branch, unlike the profile contribution calendar which only counts a
    repo's default branch) or the GraphQL contribution calendar (catches
    activity the events feed misses — testing showed GitHub's events feed
    isn't fully complete even within its own retention window, so it can't
    be trusted alone). The calendar covers a full trailing year in one
    call; anything older falls back to _extend_streak_past_year, a year at
    a time, only once a streak walk actually reaches that edge unbroken.
    """
    with _lock:
        entry = _cache.get("stats")
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]

    username = settings.github_username
    result = {"current_streak": 0}
    try:
        with httpx.Client(timeout=20) as client:
            active_days: set[str] = set()

            for page in range(1, 4):  # 3 x 100 = GitHub's 300-event cap
                resp = client.get(
                    f"https://api.github.com/users/{username}/events",
                    params={"per_page": 100, "page": page},
                    headers=_headers(),
                )
                resp.raise_for_status()
                events = resp.json()
                if not events:
                    break
                for event in events:
                    if event.get("type") in _ACTIVITY_EVENT_TYPES:
                        active_days.add(event["created_at"][:10])

            today = datetime.now(timezone.utc).date()
            year_start = today - timedelta(days=364)
            if settings.github_key:
                calendar = _contribution_days(client, year_start, today)
                active_days.update(d for d, count in calendar.items() if count > 0)

            streak = 0
            day = today
            if day.isoformat() not in active_days:
                day -= timedelta(days=1)  # today doesn't break the streak yet
            while day >= year_start and day.isoformat() in active_days:
                streak += 1
                day -= timedelta(days=1)

            if day < year_start and settings.github_key:
                streak += _extend_streak_past_year(client, username, day)

            result = {"current_streak": streak}
    except Exception:
        with _lock:
            prev = _cache.get("stats")
        return prev["value"] if prev else result

    with _lock:
        _cache["stats"] = {"value": result, "ts": time.monotonic()}
    return result
