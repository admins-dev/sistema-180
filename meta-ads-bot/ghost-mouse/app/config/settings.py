"""
Ghost Mouse V2 — Centralized Configuration.

Uses pydantic-settings for strict validation at startup.
If a critical key is missing in PROD mode, the system crashes with a clear error.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunMode(str, Enum):
    """System execution modes."""
    DEV = "DEV"
    DRY_RUN = "DRY_RUN"
    PROD = "PROD"
    SAFE_MODE = "SAFE_MODE"


class Settings(BaseSettings):
    """Central configuration — validated at import time."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Core ──────────────────────────────
    gm_mode: RunMode = Field(default=RunMode.DRY_RUN, alias="GM_MODE")
    gm_db_path: str = Field(default="ghost_mouse.db", alias="GM_DB_PATH")

    # ── LLM Keys ──────────────────────────
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # ── Email ─────────────────────────────
    brevo_api_key: str = Field(default="", alias="BREVO_API_KEY")
    email_from: str = Field(default="ghost@yourdomain.com", alias="EMAIL_FROM")
    email_domain: str = Field(default="yourdomain.com", alias="EMAIL_DOMAIN")

    # ── Scraping ──────────────────────────
    outscraper_api_key: str = Field(default="", alias="OUTSCRAPER_API_KEY")
    google_maps_api_key: str = Field(default="", alias="GOOGLE_MAPS_API_KEY")
    scrape_delay_min: float = Field(default=2.0, alias="SCRAPE_DELAY_MIN")
    scrape_delay_max: float = Field(default=5.0, alias="SCRAPE_DELAY_MAX")
    scrape_max_concurrency: int = Field(default=3, alias="SCRAPE_MAX_CONCURRENCY")
    scrape_batch_size: int = Field(default=50, alias="SCRAPE_BATCH_SIZE")

    # ── Feature Flags ─────────────────────
    ff_enable_email_outreach: bool = Field(default=False, alias="FF_ENABLE_EMAIL_OUTREACH")
    ff_enable_dm_outreach: bool = Field(default=False, alias="FF_ENABLE_DM_OUTREACH")
    ff_enable_web_enrichment: bool = Field(default=True, alias="FF_ENABLE_WEB_ENRICHMENT")
    ff_enable_llm_scoring: bool = Field(default=False, alias="FF_ENABLE_LLM_SCORING")

    # ── Logging ───────────────────────────
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="console", alias="LOG_FORMAT")

    # ── Computed ──────────────────────────

    @property
    def db_path(self) -> Path:
        """Absolute path to the SQLite database."""
        return Path(self.gm_db_path).resolve()

    @property
    def is_dry_run(self) -> bool:
        return self.gm_mode == RunMode.DRY_RUN

    @property
    def is_prod(self) -> bool:
        return self.gm_mode == RunMode.PROD

    @field_validator("gm_mode", mode="before")
    @classmethod
    def _uppercase_mode(cls, v: str) -> str:
        return v.upper() if isinstance(v, str) else v

    def validate_for_prod(self) -> None:
        """Crash hard if critical keys are missing in PROD."""
        if not self.is_prod:
            return
        missing: list[str] = []
        if not self.groq_api_key and not self.gemini_api_key:
            missing.append("GROQ_API_KEY or GEMINI_API_KEY (at least one LLM required)")
        if self.ff_enable_email_outreach and not self.brevo_api_key:
            missing.append("BREVO_API_KEY (required when email outreach is enabled)")
        if missing:
            raise ValueError(
                f"PROD mode requires these env vars:\n"
                + "\n".join(f"  - {m}" for m in missing)
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings instance. Validates once, caches forever."""
    settings = Settings()
    settings.validate_for_prod()
    return settings
