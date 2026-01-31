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

"""Tools for academic web search, including Semantic Scholar API."""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"


def semanticscholar_search_bulk(
    query: str,
    limit: int = 20,
    fields: str = "title,url,abstract,venue,year",
    sort: str = "citationCount:desc",
    year: str = "",
    token: str = "",
    publication_types: str = "",
    open_access_pdf: bool = False,
    min_citation_count: int = 0,
    fields_of_study: str = "",
) -> str:
    """Search for academic papers via Semantic Scholar bulk search API.

    Uses the bulk endpoint for efficient retrieval of papers matching the query.
    Supports boolean logic in query: + (AND), | (OR), - (NOT), "phrase", etc.

    Args:
        query: Text query matched against title and abstract. Supports boolean
            syntax: + AND, | OR, - negate, "phrase", ( ) precedence.
        limit: Maximum number of papers to return. Default 20, max 100.
        token: Pagination token from previous response (optional, use empty string to skip).
        fields: Comma-separated fields to return. Default: title, url, abstract, venue, year.
        sort: Sort order, e.g. "citationCount:desc", "publicationDate:desc",
            "paperId:asc".
        year: Filter by year or range (optional), e.g. "2020", "2018-2024", "2020-", "-2015".
        publication_types: Comma-separated types: Review, JournalArticle,
            Conference, Dataset, etc.
        open_access_pdf: If True, restrict to papers with public PDF.
        min_citation_count: Minimum citation count filter (0 to skip).
        fields_of_study: Comma-separated fields: Computer Science, Medicine,
            Biology, Physics, etc.

    Returns:
        JSON string of response with total, token (if more results), and data
        array of papers.
    """
    params: dict[str, str] = {
        "query": query,
        "fields": fields,
        "sort": sort,
    }
    if token:
        params["token"] = token
    if year:
        params["year"] = year
    if publication_types:
        params["publicationTypes"] = publication_types
    if open_access_pdf:
        params["openAccessPdf"] = ""
    if min_citation_count > 0:
        params["minCitationCount"] = str(min_citation_count)
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    url = f"{SEMANTIC_SCHOLAR_API}?{urlencode(params)}"
    headers: dict[str, str] = {"Accept": "application/json"}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    # Truncate to at most limit papers (API returns up to 1000 per call).
    if "data" in data and isinstance(data["data"], list):
        max_papers = min(max(1, limit), 100)
        data["data"] = data["data"][:max_papers]

    return json.dumps(data, indent=2, ensure_ascii=False)
