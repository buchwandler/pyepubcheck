"""Localization helpers."""

from __future__ import annotations

DEFAULT_LOCALE = "en-EN"
SUCCESS_MESSAGES = {
    "en-en": "No errors or warnings detected.",
    "fr-fr": "Aucune erreur ou avertissement detecte.",
}


def normalize_locale(locale: str | None) -> str:
    if not locale:
        return DEFAULT_LOCALE
    return locale.replace("_", "-")


def success_message(locale: str | None) -> str:
    normalized = normalize_locale(locale).lower()
    return SUCCESS_MESSAGES.get(normalized, SUCCESS_MESSAGES[DEFAULT_LOCALE.lower()])
