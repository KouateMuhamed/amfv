"""Tests for NICE scraping helpers."""

import json

import httpx

from amfv_datasets.scraping.html import LinkMode
from amfv_datasets.scraping.nice import (
    BASE_URL,
    GuidanceListingPage,
    GuidanceRef,
    build_guideline_text,
    guidance_ref_from_url,
    list_published_guidance,
)


def test_list_published_guidance_parses_next_data_listing() -> None:
    """NICE listing payloads are parsed from Next.js page data."""
    payload = {
        "props": {
            "pageProps": {
                "results": {
                    "resultCount": 6,
                    "documents": [
                        {
                            "guidanceRef": "NG235",
                            "title": "Cardiovascular disease",
                            "pathAndQuery": "/guidance/ng235",
                        },
                        {
                            "guidanceRef": "TA999",
                            "title": "Technology appraisal",
                            "pathAndQuery": "/guidance/ta999",
                        },
                        {
                            "guidanceRef": "QS1",
                            "title": "Quality standard",
                            "pathAndQuery": "/guidance/qs1",
                        },
                        {
                            "guidanceRef": "MIB323",
                            "title": "Medtech innovation briefing",
                            "pathAndQuery": "/guidance/mib323",
                        },
                        {
                            "guidanceRef": "ES41",
                            "title": "Evidence summary",
                            "pathAndQuery": "/guidance/es41",
                        },
                        {
                            "guidanceRef": "CSG8",
                            "title": "Legacy cancer service guidance",
                            "pathAndQuery": "/guidance/csg8",
                        },
                    ],
                }
            }
        }
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/guidance/published"
        assert request.url.params["sp"] == "on"
        assert "ps" not in request.url.params
        assert "ndt" not in request.url.params
        assert "ngt" not in request.url.params
        html = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script>'
        return httpx.Response(200, text=html)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE_URL)

    listing_page = list_published_guidance(client)

    assert listing_page == GuidanceListingPage(
        total=6,
        refs=[
            GuidanceRef(
                ref="NG235",
                slug="ng235",
                title="Cardiovascular disease",
                page_url="https://www.nice.org.uk/guidance/ng235",
            ),
            GuidanceRef(
                ref="TA999",
                slug="ta999",
                title="Technology appraisal",
                page_url="https://www.nice.org.uk/guidance/ta999",
            ),
            GuidanceRef(
                ref="QS1",
                slug="qs1",
                title="Quality standard",
                page_url="https://www.nice.org.uk/guidance/qs1",
            ),
            GuidanceRef(
                ref="MIB323",
                slug="mib323",
                title="Medtech innovation briefing",
                page_url="https://www.nice.org.uk/advice/mib323",
            ),
            GuidanceRef(
                ref="ES41",
                slug="es41",
                title="Evidence summary",
                page_url="https://www.nice.org.uk/advice/es41",
            ),
        ],
    )


def test_guidance_ref_from_url_normalizes_chapter_url() -> None:
    """NICE guidance URLs are normalized to overview refs."""
    assert guidance_ref_from_url("https://www.nice.org.uk/guidance/TA1138/chapter/4-Implementation") == GuidanceRef(
        ref="TA1138",
        slug="ta1138",
        title="TA1138",
        page_url="https://www.nice.org.uk/guidance/ta1138",
    )


def test_guidance_ref_from_url_accepts_advice_url() -> None:
    """NICE advice URLs are normalized to advice overview refs."""
    assert guidance_ref_from_url("https://www.nice.org.uk/advice/MIB323/chapter/Summary") == GuidanceRef(
        ref="MIB323",
        slug="mib323",
        title="MIB323",
        page_url="https://www.nice.org.uk/advice/mib323",
    )


def test_build_guideline_text_scrapes_overview_chapters() -> None:
    """Overview chapter links are fetched and converted into markdown."""
    pages = {
        "https://www.nice.org.uk/guidance/ng235": """
            <html>
              <h1>Cardiovascular disease</h1>
              <h2>Overview</h2>
              <div>
                <p>Guideline summary.</p>
                <p><strong>Last reviewed:</strong> 01 January 2026</p>
                <p>Next review: This guidance will be reviewed if there is new evidence.</p>
                <p>How we prioritise updating our guidance</p>
                <h3>Recommendations</h3>
                <p>This guideline includes recommendations on:</p>
                <ul><li><a href="/guidance/ng235/chapter/recommendations#diagnosis">diagnosis</a></li></ul>
                <h3>Who is it for?</h3>
                <p>Healthcare professionals.</p>
                <h3>Guideline development process</h3>
                <p>How we develop NICE guidelines.</p>
              </div>
              <nav class="stacked-nav">
                <a href="/guidance/ng235/chapter/recommendations?tab=contents">Recommendations</a>
                <a href="/guidance/ng235/chapter/finding-more-information-and-committee-details">Details</a>
              </nav>
            </html>
        """,
        "https://www.nice.org.uk/guidance/ng235/chapter/recommendations": """
            <div class="chapter">
              <h2>1 Recommendation</h2>
              <p>Offer <a href="/guidance/ng235/evidence">treatment</a> [1].</p>
              <ul><li><p>Discuss benefits.</p></li></ul>
              <table><tr><th>Drug</th><th>Dose</th></tr><tr><td>A</td><td>5 mg</td></tr></table>
            </div>
        """,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=pages[str(request.url)])

    client = httpx.Client(transport=httpx.MockTransport(handler))

    content, section_count, title = build_guideline_text(
        client,
        GuidanceRef(
            ref="NG235",
            slug="ng235",
            title="NG235",
            page_url="https://www.nice.org.uk/guidance/ng235",
        ),
    )

    assert title == "Cardiovascular disease"
    assert section_count == 2
    assert content == (
        "## Overview\n\n"
        "Guideline summary.\n\n"
        "**Last reviewed:** 01 January 2026\n\n"
        "Next review: This guidance will be reviewed if there is new evidence.\n\n"
        "### Who is it for?\n\n"
        "Healthcare professionals.\n\n"
        "## Recommendation\n\n"
        "Offer [treatment](https://www.nice.org.uk/guidance/ng235/evidence) .\n\n"
        "- Discuss benefits.\n\n"
        "| Drug | Dose |\n| --- | --- |\n| A | 5 mg |"
    )

    stripped_content, _section_count, _title = build_guideline_text(
        client,
        GuidanceRef(
            ref="NG235",
            slug="ng235",
            title="NG235",
            page_url="https://www.nice.org.uk/guidance/ng235",
        ),
        link_mode=LinkMode.STRIP,
    )
    assert "Offer treatment ." in stripped_content
    assert "Last reviewed" in stripped_content
    assert "How we prioritise updating our guidance" not in stripped_content
    assert "This guideline includes recommendations on" not in stripped_content


def test_build_guideline_text_scrapes_advice_chapters() -> None:
    """NICE advice pages use advice chapter URLs."""
    pages = {
        "https://www.nice.org.uk/advice/mib323": """
            <html>
              <h1>Medical device</h1>
              <h2>Overview</h2>
              <div>
                <p>NICE has developed a medtech innovation briefing.</p>
                <p>What are MIBs?</p>
              </div>
              <nav class="stacked-nav">
                <a href="/advice/mib323/chapter/Summary">Summary</a>
              </nav>
            </html>
        """,
        "https://www.nice.org.uk/advice/mib323/chapter/Summary": """
            <div class="chapter">
              <h2>1 Summary</h2>
              <p>Use in specialist settings.</p>
            </div>
        """,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=pages[str(request.url)])

    client = httpx.Client(transport=httpx.MockTransport(handler))

    content, section_count, title = build_guideline_text(
        client,
        GuidanceRef(
            ref="MIB323",
            slug="mib323",
            title="MIB323",
            page_url="https://www.nice.org.uk/advice/mib323",
        ),
    )

    assert title == "Medical device"
    assert section_count == 1
    assert content == "## Summary\n\nUse in specialist settings."


def test_build_guideline_text_trims_quality_standard_overview_boilerplate() -> None:
    """Quality-standard overview boilerplate is removed while scope text is kept."""
    pages = {
        "https://www.nice.org.uk/guidance/qs1": """
            <html>
              <h1>Quality standard</h1>
              <h2>Overview</h2>
              <div>
                <p>This quality standard covers care for adults.</p>
                <p>Last reviewed: 01 January 2026</p>
                <h3>How to use NICE quality standards and how we develop them</h3>
                <p>Generic quality-standard usage text.</p>
              </div>
              <nav class="stacked-nav">
                <a href="/guidance/qs1/chapter/Quality-statements">Quality statements</a>
              </nav>
            </html>
        """,
        "https://www.nice.org.uk/guidance/qs1/chapter/Quality-statements": """
            <div class="chapter">
              <h2>1 Quality statements</h2>
              <p>Statement text.</p>
            </div>
        """,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=pages[str(request.url)])

    client = httpx.Client(transport=httpx.MockTransport(handler))

    content, section_count, title = build_guideline_text(
        client,
        GuidanceRef(
            ref="QS1",
            slug="qs1",
            title="QS1",
            page_url="https://www.nice.org.uk/guidance/qs1",
        ),
    )

    assert title == "Quality standard"
    assert section_count == 2
    assert content == (
        "## Overview\n\n"
        "This quality standard covers care for adults.\n\n"
        "Last reviewed: 01 January 2026\n\n"
        "## Quality statements\n\n"
        "Statement text."
    )
