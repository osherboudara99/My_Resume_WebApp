"""Streak walk tests.

The interesting cases are all about which day the walk is anchored to, so
these exercise the pure helpers directly rather than mocking the GitHub API.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app import github


PACIFIC = ZoneInfo("America/Los_Angeles")


@pytest.fixture(autouse=True)
def pacific_profile(monkeypatch):
    monkeypatch.setattr(github.settings, "github_timezone", "America/Los_Angeles")


def days_ending(last: date, count: int) -> set[str]:
    """The `count` consecutive active days ending on `last`."""
    return {(last - timedelta(days=n)).isoformat() for n in range(count)}


def test_evening_utc_rollover_keeps_streak():
    """5:28pm Pacific on the 27th is already the 28th in UTC. Anchoring to UTC
    burned the one-day grace step on the 28th, leaving the 26th unreachable and
    the streak at 0 -- the regression this guards.
    """
    active = days_ending(date(2026, 7, 26), 3)  # committed through yesterday

    streak, _ = github._walk_streak(active, date(2026, 7, 27), date(2025, 7, 29))

    assert streak == 3


def test_today_active_counts_toward_streak():
    active = days_ending(date(2026, 7, 27), 3)

    streak, _ = github._walk_streak(active, date(2026, 7, 27), date(2025, 7, 29))

    assert streak == 3


def test_gap_before_yesterday_breaks_streak():
    active = {"2026-07-24", "2026-07-23"}  # nothing on the 25th or 26th

    streak, _ = github._walk_streak(active, date(2026, 7, 27), date(2025, 7, 29))

    assert streak == 0


def test_walk_reports_first_unaccounted_day():
    active = days_ending(date(2026, 7, 26), 2)

    _, day = github._walk_streak(active, date(2026, 7, 27), date(2025, 7, 29))

    assert day == date(2026, 7, 24)


def test_walk_stops_at_floor():
    active = days_ending(date(2026, 7, 26), 400)
    floor = date(2026, 7, 20)

    streak, day = github._walk_streak(active, date(2026, 7, 27), floor)

    assert streak == 7
    assert day < floor  # signals the caller to keep walking older history


@pytest.mark.parametrize(
    "utc_ts,expected",
    [
        ("2026-07-26T21:10:31Z", "2026-07-26"),  # 2:10pm PDT, same day
        ("2026-07-28T00:28:00Z", "2026-07-27"),  # 5:28pm PDT, previous local day
        ("2026-07-27T06:59:59Z", "2026-07-26"),  # 11:59pm PDT, previous local day
        ("2026-07-27T07:00:00Z", "2026-07-27"),  # midnight PDT, day rolls over
    ],
)
def test_event_timestamps_bucket_into_local_days(utc_ts, expected):
    assert github._local_day(utc_ts) == expected


def test_today_uses_profile_timezone_not_utc(monkeypatch):
    """At 5:28pm Pacific, UTC is already the next day. _today() must report the
    Pacific date -- reporting the UTC one is what zeroed the streak every
    evening.
    """
    frozen_utc = datetime(2026, 7, 28, 0, 28, tzinfo=timezone.utc)

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return frozen_utc.astimezone(tz) if tz else frozen_utc

    monkeypatch.setattr(github, "datetime", FrozenDatetime)

    assert frozen_utc.date() == date(2026, 7, 28)  # what the old code used
    assert github._today() == date(2026, 7, 27)
