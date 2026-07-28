from functools import lru_cache
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # protected_namespaces=() silences the pydantic warning for the anthropic_*
    # fields; env_file lets local dev load backend/.env.
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", protected_namespaces=()
    )

    # --- Anthropic ---
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY", None)
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    max_tokens: int = int(os.getenv("MAX_TOKENS", 700))

    # --- GitHub ---
    github_key: str | None = os.getenv("GITHUB_KEY", None)
    github_username: str = os.getenv("GITHUB_USERNAME", "osherboudara99")
    # IANA zone the contribution streak is measured in. Must match the GitHub
    # profile's timezone, since that's the boundary GitHub buckets contribution
    # days on -- and it's the day boundary a human reading the stat means.
    github_timezone: str = os.getenv("GITHUB_TIMEZONE", "America/Los_Angeles")

    # --- Live content sources ---
    # The resume is pulled fresh from Google Docs so the site always reflects
    # the latest version. aboutme is optional: if a Google Doc URL is set it is
    # pulled live too, otherwise the bundled fallback in assets/ is used.
    google_doc_resume_url: str = os.getenv(
        "GOOGLE_DOC_RESUME_URL", "https://docs.google.com/document/d/1gql8n7U8WHkdLEu6R6wFI41tLWpnY5QiKQCwdsKMlQA/"
    )
    google_doc_aboutme_url: str = os.getenv("GOOGLE_DOC_ABOUTME_URL", "")
    content_ttl_seconds: int = int(os.getenv("CONTENT_TTL_SECONDS", 300))
    # Absolute path to the fallback assets dir. Empty -> repo-root/assets.
    assets_dir: str = ""

    # --- Server / CORS / limits ---
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    chat_rate_limit: str = os.getenv("CHAT_RATE_LIMIT", "20/minute")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def assets_path(self) -> Path:
        if self.assets_dir:
            return Path(self.assets_dir)
        # backend/app/config.py -> parents[2] == repo root
        return Path(__file__).resolve().parents[2] / "assets"


@lru_cache
def get_settings() -> Settings:
    return Settings()
