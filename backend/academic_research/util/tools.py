# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared tools for academic research agents, e.g. URL fetching."""

from __future__ import annotations

import html
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Max content size to avoid overwhelming the LLM (chars).
_MAX_CONTENT_CHARS = 50000


def _html_to_text(html_str: str) -> str:
    """Extract readable text from HTML, stripping tags and normalizing whitespace."""
    # Remove script and style blocks.
    html_str = re.sub(
        r"<script[^>]*>.*?</script>", "", html_str, flags=re.DOTALL | re.IGNORECASE
    )
    html_str = re.sub(
        r"<style[^>]*>.*?</style>", "", html_str, flags=re.DOTALL | re.IGNORECASE
    )
    # Replace block elements with newlines to preserve structure.
    html_str = re.sub(r"</(p|div|br|tr|li|h[1-6])[^>]*>", "\n", html_str, flags=re.I)
    # Remove remaining tags.
    text = re.sub(r"<[^>]+>", " ", html_str)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def fetch_url(url: str, *, max_chars: int = _MAX_CONTENT_CHARS) -> str:
    """Fetch content from a URL for reading (e.g. paper abstracts, landing pages).

    Retrieves the raw response and, for HTML pages, extracts readable text.
    PDFs and other binary formats are not supported.

    Args:
        url: The full URL to fetch (http or https).
        max_chars: Maximum number of characters to return. Default 50000.

    Returns:
        The fetched content as text. For HTML, returns extracted text. Truncated
        if longer than max_chars. On error, returns an error message string.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"Error: Only http/https URLs are supported. Got scheme: {parsed.scheme}"

    headers: dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; AcademicResearchBot/1.0; +https://github.com)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/json,text/plain,*/*",
    }
    req = Request(url, headers=headers)

    try:
        with urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            raw = resp.read().decode("utf-8", errors="replace")

        if "application/pdf" in content_type:
            return "Error: PDF content is not supported. Use the URL for an HTML or text page instead."

        if "text/html" in content_type or "application/xhtml" in content_type:
            text = _html_to_text(raw)
        else:
            text = raw

        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... truncated ...]"
        return text

    except HTTPError as e:
        return f"Error fetching URL: HTTP {e.code} {e.reason}"
    except URLError as e:
        return f"Error fetching URL: {e.reason}"
    except Exception as e:
        return f"Error fetching URL: {e}"
