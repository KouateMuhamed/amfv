"""Helpers for data embedded in Next.js pages."""

from __future__ import annotations

import json
from typing import Any

from lxml import html as lxml_html

from amfv_datasets.scraping.base import ScrapeError


def script_json_by_id(html_text: str, script_id: str) -> dict[str, Any]:
    """Parse JSON from a script tag with the given id.

    Args:
        html_text: HTML page text containing the script tag.
        script_id: Script element id to read.
    """
    doc = lxml_html.fromstring(html_text)
    scripts = doc.xpath("//script[@id=$script_id]/text()", script_id=script_id)
    if not scripts:
        raise ScrapeError(f"Page markup changed (no {script_id} script)")
    try:
        value = json.loads(scripts[0])
    except ValueError as exc:
        raise ScrapeError(f"Could not parse {script_id} JSON") from exc
    if not isinstance(value, dict):
        raise ScrapeError(f"{script_id} JSON was not an object")
    return value


__all__ = ["script_json_by_id"]
