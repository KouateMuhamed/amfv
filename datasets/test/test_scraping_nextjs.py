"""Tests for reusable Next.js scraping helpers."""

import json

from amfv_datasets.scraping.nextjs import script_json_by_id


def test_script_json_by_id_parses_json_independent_of_attribute_order() -> None:
    """Script payload parsing uses HTML structure, not fragile script markup text."""
    payload = {"props": {"pageProps": {"value": 1}}}
    html_text = f"<script type='application/json' data-build='1' id='__NEXT_DATA__'>{json.dumps(payload)}</script>"

    assert script_json_by_id(html_text, "__NEXT_DATA__") == payload
