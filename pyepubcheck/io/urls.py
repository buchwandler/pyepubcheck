"""URI and fragment helpers."""

from __future__ import annotations

from urllib.parse import urldefrag, urlparse


def is_remote_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def is_data_url(value: str) -> bool:
    return value.startswith("data:")


def split_fragment(value: str) -> tuple[str, str]:
    return urldefrag(value)
