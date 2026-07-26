"""Live content fetch for the resume and aboutme.

The resume (and optionally aboutme) is pulled fresh from Google Docs so the site
always reflects the latest version. Results are held in a short TTL cache; if a
fetch fails or returns empty we fall back to the last-known-good value, and
finally to the bundled copy under assets/. This keeps the site live without
re-downloading on every request and without ever breaking mid-edit.
"""

import threading
import time

import httpx

from .config import get_settings

settings = get_settings()

_lock = threading.Lock()
# key -> {"value": str | bytes, "ts": float}
_store: dict[str, dict] = {}


def _export_url(base: str, fmt: str) -> str:
    return f"{base.rstrip('/')}/export?format={fmt}"


def _read_fallback_text(name: str) -> str:
    path = settings.assets_path / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_fallback_bytes(name: str) -> bytes:
    path = settings.assets_path / name
    return path.read_bytes() if path.exists() else b""


def _is_fresh(key: str) -> bool:
    entry = _store.get(key)
    return bool(entry) and (time.monotonic() - entry["ts"]) < settings.content_ttl_seconds


def _fetch(url: str, as_bytes: bool):
    resp = httpx.get(url, follow_redirects=True, timeout=20)
    resp.raise_for_status()
    return resp.content if as_bytes else resp.text


def _cached(key: str, url: str | None, fallback_name: str, as_bytes: bool):
    with _lock:
        if _is_fresh(key):
            return _store[key]["value"]

    value = None
    if url:
        try:
            fetched = _fetch(url, as_bytes)
            if as_bytes:
                value = fetched or None
            else:
                value = fetched if fetched and fetched.strip() else None
        except Exception:
            value = None

    if value is None:
        # last-known-good, then bundled fallback
        prev = _store.get(key)
        if prev and prev["value"]:
            value = prev["value"]
        else:
            value = (
                _read_fallback_bytes(fallback_name)
                if as_bytes
                else _read_fallback_text(fallback_name)
            )

    with _lock:
        _store[key] = {"value": value, "ts": time.monotonic()}
    return value


def get_resume_markdown() -> str:
    return _cached(
        "resume_md",
        _export_url(settings.google_doc_resume_url, "md"),
        "resume.md",
        as_bytes=False,
    )


def get_resume_pdf() -> bytes:
    return _cached(
        "resume_pdf",
        _export_url(settings.google_doc_resume_url, "pdf"),
        "resume.pdf",
        as_bytes=True,
    )


def get_aboutme() -> str:
    url = (
        _export_url(settings.google_doc_aboutme_url, "txt")
        if settings.google_doc_aboutme_url
        else None
    )
    return _cached("aboutme", url, "aboutme.txt", as_bytes=False)


def get_corpus() -> str:
    """Combined knowledge base handed to the agent as context."""
    resume = get_resume_markdown().strip()
    aboutme = get_aboutme().strip()
    return f"# RESUME\n\n{resume}\n\n# ADDITIONAL BACKGROUND\n\n{aboutme}"


def refresh() -> None:
    with _lock:
        _store.clear()
