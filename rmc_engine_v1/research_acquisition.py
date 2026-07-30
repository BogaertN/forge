"""Governed, source-preserving web evidence acquisition for Ask Forge.

This module is deliberately an evidence connector, not an answer authority.
It searches public web indexes, captures a small bounded set of pages, and
returns exact excerpts with source receipts.  Nothing fetched here becomes
stable or canonical RMC memory.  The operator interpreter may use the result
to build a *possible-answer manifest* and may retain that manifest in the
candidate namespace for later comparison, correction, or promotion.

The implementation is standard-library only.  It does not call an LLM, build
embeddings, query a vector database, execute shell commands, or follow a URL
to a loopback/private/link-local network address.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from html import unescape
from html.parser import HTMLParser
import ipaddress
import json
import re
import socket
from typing import Callable, Final, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


RESEARCH_ACQUISITION_VERSION: Final[str] = (
    "aiweb-forge-governed-research-acquisition-v1"
)
SEARCH_ENDPOINT: Final[str] = "https://lite.duckduckgo.com/lite/"
MAX_SEARCH_RESULTS: Final[int] = 6
MAX_FETCHED_PAGES: Final[int] = 3
MAX_RESPONSE_BYTES: Final[int] = 450_000
MAX_EXCERPT_CODE_POINTS: Final[int] = 900
DEFAULT_TIMEOUT_SECONDS: Final[float] = 8.0

_SPACE = re.compile(r"\s+")
_WORD = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE)
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_STOP_FORMS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "can",
        "could",
        "did",
        "do",
        "does",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "of",
        "on",
        "or",
        "should",
        "the",
        "this",
        "to",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "would",
        "you",
    }
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _stable_id(prefix: str, value: object) -> str:
    digest = hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _fold(value: str) -> str:
    return _SPACE.sub(" ", value.casefold()).strip()


def _concept_forms(value: str) -> frozenset[str]:
    forms: set[str] = set()
    for match in _WORD.finditer(value):
        form = _fold(match.group(0))
        if len(form) <= 1 or form in _STOP_FORMS:
            continue
        forms.add(form)
        # Small declared inflection projections improve exact source-form
        # resonance without creating subword IDs or a probabilistic tokenizer.
        # The exact spelling remains present alongside every projected form.
        if len(form) > 4 and form.endswith("ies"):
            forms.add(form[:-3] + "y")
        elif len(form) > 3 and form.endswith("s") and not form.endswith("ss"):
            forms.add(form[:-1])
        if len(form) > 4 and form.endswith("ed"):
            forms.add(form[:-2])
            forms.add(form[:-1])
        if len(form) > 5 and form.endswith("ing"):
            forms.add(form[:-3])
            forms.add(form[:-3] + "e")
        if form in {"defined", "defines", "defining", "definition", "definitions"}:
            forms.add("define")
    return frozenset(forms)


def research_acquisition_boundary() -> dict[str, object]:
    return {
        "version": RESEARCH_ACQUISITION_VERSION,
        "role": "candidate_evidence_connector",
        "forge_governs": True,
        "network_access_possible": True,
        "network_access_bounded": True,
        "public_http_https_only": True,
        "private_network_targets_blocked": True,
        "redirect_targets_revalidated": True,
        "calls_llm": False,
        "model_tokenization_performed": False,
        "embedding_performed": False,
        "vector_retrieval_performed": False,
        "executes_shell": False,
        "writes_files": False,
        "writes_stable_memory": False,
        "writes_canonical_memory": False,
        "source_is_truth_authority": False,
        "candidate_manifest_required": True,
    }


def _public_addresses(hostname: str, port: int) -> tuple[str, ...]:
    try:
        records = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise ValueError("research_host_resolution_failed") from error
    addresses: list[str] = []
    for record in records:
        raw = str(record[4][0]).split("%", 1)[0]
        try:
            address = ipaddress.ip_address(raw)
        except ValueError as error:
            raise ValueError("research_host_address_invalid") from error
        if not address.is_global:
            raise ValueError("research_private_or_non_global_target_blocked")
        rendered = str(address)
        if rendered not in addresses:
            addresses.append(rendered)
    if not addresses:
        raise ValueError("research_host_has_no_public_address")
    return tuple(addresses)


def _validate_public_url(url: str) -> str:
    parsed = urlparse(str(url).strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("research_url_must_be_public_http_or_https")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("research_url_credentials_blocked")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    _public_addresses(parsed.hostname, port)
    return parsed.geturl()


class _ValidatedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        resolved = urljoin(req.full_url, newurl)
        _validate_public_url(resolved)
        return super().redirect_request(req, fp, code, msg, headers, resolved)


def _fetch(
    url: str,
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    accept: str = "text/html,application/xhtml+xml,text/plain;q=0.8",
) -> tuple[str, str, str]:
    validated = _validate_public_url(url)
    request = Request(
        validated,
        headers={
            "User-Agent": "AI.Web-Forge/1.0 (governed evidence acquisition)",
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.8",
        },
    )
    opener = build_opener(_ValidatedRedirectHandler())
    with opener.open(request, timeout=timeout_seconds) as response:
        final_url = _validate_public_url(response.geturl())
        content_type = str(response.headers.get("Content-Type", ""))
        lowered_type = content_type.casefold()
        if not any(
            admitted in lowered_type
            for admitted in ("text/html", "application/xhtml+xml", "text/plain")
        ):
            raise ValueError("research_content_type_not_admitted")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("research_response_size_limit_exceeded")
        charset = response.headers.get_content_charset() or "utf-8"
        text = raw.decode(charset, errors="replace")
        return final_url, content_type, text


def _fetch_json(url: str, *, timeout_seconds: float) -> object:
    validated = _validate_public_url(url)
    request = Request(
        validated,
        headers={
            "User-Agent": "AI.Web-Forge/1.0 (governed evidence acquisition)",
            "Accept": "application/json",
        },
    )
    opener = build_opener(_ValidatedRedirectHandler())
    with opener.open(request, timeout=timeout_seconds) as response:
        _validate_public_url(response.geturl())
        content_type = str(response.headers.get("Content-Type", "")).casefold()
        if "application/json" not in content_type:
            raise ValueError("research_json_content_type_not_admitted")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("research_response_size_limit_exceeded")
        return json.loads(raw.decode("utf-8", errors="strict"))


def _unwrap_search_url(href: str) -> str:
    raw = unescape(href).strip()
    if raw.startswith("//"):
        raw = "https:" + raw
    resolved = urljoin(SEARCH_ENDPOINT, raw)
    parsed = urlparse(resolved)
    if parsed.hostname and parsed.hostname.endswith("duckduckgo.com"):
        query = parse_qs(parsed.query)
        if query.get("uddg"):
            return unquote(query["uddg"][0])
    return resolved


def _plain_fragment(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return _SPACE.sub(" ", unescape(without_tags)).strip()


class _SearchResultParser(HTMLParser):
    """Collect only individual DuckDuckGo result anchors.

    A regular expression can accidentally bridge multiple anchors when an
    unrelated link precedes the result class.  This parser keeps href/title
    custody inside one exact element.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._active_href: str | None = None
        self._active_parts: list[str] = []
        self.results: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.casefold() != "a" or self._active_href is not None:
            return
        values = {str(key).casefold(): str(value or "") for key, value in attrs}
        classes = frozenset(values.get("class", "").split())
        href = values.get("href", "")
        if "result-link" not in classes or not href:
            return
        self._active_href = href
        self._active_parts = []

    def handle_data(self, data: str) -> None:
        if self._active_href is not None and data.strip():
            self._active_parts.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "a" or self._active_href is None:
            return
        title = _SPACE.sub(" ", " ".join(self._active_parts)).strip()
        self.results.append((self._active_href, title))
        self._active_href = None
        self._active_parts = []


def _search_wikipedia(
    query: str,
    *,
    limit: int,
    timeout_seconds: float,
) -> tuple[dict[str, object], ...]:
    params = urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": limit,
            "prop": "info",
            "inprop": "url",
            "format": "json",
            "formatversion": 2,
        }
    )
    data = _fetch_json(
        f"https://en.wikipedia.org/w/api.php?{params}",
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(data, dict):
        return ()
    query_data = data.get("query")
    pages = query_data.get("pages") if isinstance(query_data, dict) else None
    if not isinstance(pages, list):
        return ()
    rows: list[dict[str, object]] = []
    for page in pages:
        if not isinstance(page, dict) or not page.get("fullurl"):
            continue
        body = {
            "rank": len(rows) + 1,
            "url": str(page["fullurl"]),
            "title": str(page.get("title") or page["fullurl"])[:240],
            "page_title": str(page.get("title") or ""),
            "search_provider": "wikipedia_mediawiki",
            "search_rank_is_truth_authority": False,
        }
        rows.append(
            {
                "search_result_id": _stable_id("web_search_result", body),
                **body,
            }
        )
    return tuple(rows)


def _declared_public_source_candidates(query: str) -> tuple[dict[str, object], ...]:
    """Return narrow official-source candidates for declared technical domains.

    This registry selects a public evidence source; it does not supply an
    answer, declare the source true, or bypass excerpt/Echo/candidate gates.
    """

    forms = _concept_forms(query)
    declared: list[tuple[str, str, str]] = []
    if "python" in forms:
        if forms & {"function", "define", "argument", "parameter"}:
            declared.append(
                (
                    "python_functions_tutorial",
                    "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
                    "Python tutorial — Defining Functions",
                )
            )
        else:
            declared.append(
                (
                    "python_tutorial",
                    "https://docs.python.org/3/tutorial/index.html",
                    "The Python Tutorial",
                )
            )
    if forms & {"javascript", "js"} and "function" in forms:
        declared.append(
            (
                "mdn_javascript_functions",
                "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions",
                "MDN JavaScript Guide — Functions",
            )
        )
    if "css" in forms:
        declared.append(
            (
                "mdn_css_reference",
                "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference",
                "MDN CSS Reference",
            )
        )
    if "html" in forms:
        declared.append(
            (
                "mdn_html_reference",
                "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference",
                "MDN HTML Reference",
            )
        )
    rows: list[dict[str, object]] = []
    for key, url, title in declared:
        body = {
            "rank": len(rows) + 1,
            "url": url,
            "title": title,
            "search_provider": "forge_declared_public_source_registry",
            "source_registry_key": key,
            "search_rank_is_truth_authority": False,
        }
        rows.append(
            {
                "search_result_id": _stable_id("web_search_result", body),
                **body,
            }
        )
    return tuple(rows)


def search_public_web(
    query: str,
    *,
    limit: int = MAX_SEARCH_RESULTS,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[dict[str, object], ...]:
    """Return bounded public search results without treating rank as truth."""

    source = str(query).strip()
    if not source:
        return ()
    limit = max(1, min(MAX_SEARCH_RESULTS, int(limit)))
    declared_rows = list(_declared_public_source_candidates(source))
    url = f"{SEARCH_ENDPOINT}?q={quote_plus(source)}"
    try:
        _, _, html_text = _fetch(url, timeout_seconds=timeout_seconds)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        html_text = ""
    parser = _SearchResultParser()
    parser.feed(html_text)
    rows: list[dict[str, object]] = declared_rows
    seen: set[str] = {str(row["url"]) for row in declared_rows}
    for href, raw_title in parser.results:
        try:
            target = _validate_public_url(_unwrap_search_url(href))
        except (ValueError, TypeError):
            continue
        if target in seen:
            continue
        seen.add(target)
        title = _plain_fragment(raw_title)[:240] or target
        body = {
            "rank": len(rows) + 1,
            "url": target,
            "title": title,
            "search_provider": "duckduckgo_lite",
            "search_rank_is_truth_authority": False,
        }
        rows.append(
            {
                "search_result_id": _stable_id("web_search_result", body),
                **body,
            }
        )
        if len(rows) >= limit:
            break
    if parser.results:
        return tuple(rows)
    try:
        wikipedia_rows = _search_wikipedia(
            source,
            limit=limit,
            timeout_seconds=timeout_seconds,
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        if rows:
            return tuple(rows[:limit])
        raise
    for row in wikipedia_rows:
        if str(row.get("url")) in seen or len(rows) >= limit:
            continue
        adjusted = dict(row)
        adjusted["rank"] = len(rows) + 1
        identity_body = {
            key: value
            for key, value in adjusted.items()
            if key != "search_result_id"
        }
        adjusted["search_result_id"] = _stable_id(
            "web_search_result", identity_body
        )
        rows.append(adjusted)
    return tuple(rows[:limit])


class _PageTextExtractor(HTMLParser):
    _BLOCKED = frozenset({"script", "style", "svg", "noscript", "template"})
    _TEXT_BLOCKS = frozenset(
        {"p", "li", "pre", "code", "h1", "h2", "h3", "h4", "td"}
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._blocked_depth = 0
        self._title_depth = 0
        self._block_depth = 0
        self._current: list[str] = []
        self._section_stack: list[str | None] = []
        self.title_parts: list[str] = []
        self.blocks: list[str] = []
        self.block_sections: list[str | None] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        lowered = tag.casefold()
        if lowered in self._BLOCKED:
            self._blocked_depth += 1
            return
        if self._blocked_depth:
            return
        if lowered == "section":
            values = {str(key).casefold(): str(value or "") for key, value in attrs}
            inherited = self._section_stack[-1] if self._section_stack else None
            self._section_stack.append(values.get("id") or inherited)
        if lowered == "title":
            self._title_depth += 1
        if lowered in self._TEXT_BLOCKS:
            if self._block_depth == 0:
                self._current = []
            self._block_depth += 1

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in self._BLOCKED:
            self._blocked_depth = max(0, self._blocked_depth - 1)
            return
        if self._blocked_depth:
            return
        if lowered == "title":
            self._title_depth = max(0, self._title_depth - 1)
        if lowered in self._TEXT_BLOCKS and self._block_depth:
            self._block_depth -= 1
            if self._block_depth == 0:
                text = _SPACE.sub(" ", " ".join(self._current)).strip()
                if len(text) >= 24:
                    self.blocks.append(text)
                    self.block_sections.append(
                        self._section_stack[-1] if self._section_stack else None
                    )
                self._current = []
        if lowered == "section" and self._section_stack:
            self._section_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._blocked_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._title_depth:
            self.title_parts.append(text)
        if self._block_depth:
            self._current.append(text)


def _relevant_excerpt(query: str, blocks: Iterable[str]) -> tuple[str, float, tuple[str, ...]]:
    query_forms = _concept_forms(query)
    query_words = frozenset(
        _fold(match.group(0)) for match in _WORD.finditer(query)
    )
    procedure_requested = "how" in query_words or "define" in query_forms
    candidates: list[tuple[float, int, str, tuple[str, ...]]] = []
    ordinal = 0
    for block in blocks:
        for sentence in _SENTENCE.split(block):
            exact = _SPACE.sub(" ", sentence).strip()
            if len(exact) < 35:
                continue
            forms = _concept_forms(exact)
            overlap = tuple(sorted(query_forms & forms))
            coverage = len(overlap) / max(1, len(query_forms))
            density = len(overlap) / max(4, len(forms))
            leading_concept = next(
                (
                    folded
                    for folded in (
                        _fold(match.group(0)) for match in _WORD.finditer(exact)
                    )
                    if folded not in _STOP_FORMS and len(folded) > 1
                ),
                "",
            )
            is_question_like = "?" in exact or bool(
                re.match(r"^[\"'“‘]?(?:what|why|how|when|where|who|which)\b", exact, re.I)
            )
            definition_signal = bool(
                leading_concept in query_forms
                and (
                    re.search(
                        r"\b(?:means|refers to|is defined as|are defined as)\b",
                        exact,
                        re.I,
                    )
                    or re.match(
                        r"^[\"'“‘]?(?:the\s+)?[^.!?]{1,80}\s+(?:is|are)\s+"
                        r"(?!(?:used|related|said|shown|listed|included)\b)",
                        exact,
                        re.I,
                    )
                )
            )
            definition_bonus = 0.16 if not is_question_like and definition_signal else 0.0
            procedure_bonus = (
                0.16
                if procedure_requested
                and re.search(
                    r"\b(?:the\s+)?keyword\s+"
                    r"(?:def|class|function|const|let|var|return)\b"
                    r"|\bmust\b|\bsyntax\b|\bstatement\b|\bfollowed by\b",
                    exact,
                    re.I,
                )
                else 0.0
            )
            position_bonus = max(0.0, 0.13 - 0.0025 * ordinal)
            length_bonus = min(0.06, max(0.0, (len(exact) - 45) / 900))
            question_penalty = 0.26 if is_question_like else 0.0
            reference_noise_penalty = (
                0.18
                if exact.startswith(("↑", "ISBN", "Retrieved "))
                or (exact.startswith(("\"", "“")) and len(exact) < 90)
                else 0.0
            )
            navigation_penalty = (
                0.4
                if " toggle " in f" {_fold(exact)} "
                and " subsection" in _fold(exact)
                else 0.0
            )
            score = max(
                0.0,
                min(
                    1.0,
                    0.66 * coverage
                    + 0.14 * density
                    + definition_bonus
                    + procedure_bonus
                    + position_bonus
                    + length_bonus
                    - question_penalty
                    - reference_noise_penalty
                    - navigation_penalty,
                ),
            )
            candidates.append((score, -ordinal, exact, overlap))
            ordinal += 1
    if not candidates:
        return "", 0.0, ()
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    score, _, best, overlap = candidates[0]
    return best[:MAX_EXCERPT_CODE_POINTS], round(score, 6), overlap


def _source_and_rank_priors(
    final_url: str,
    search_result: dict[str, object],
    resonance_score: float,
) -> tuple[float, float, float]:
    hostname = (urlparse(final_url).hostname or "").casefold()
    source_quality_prior = 0.0
    if hostname.endswith("wikipedia.org"):
        source_quality_prior = 0.12
    elif hostname.endswith(".gov") or hostname.endswith(".edu"):
        source_quality_prior = 0.14
    elif hostname in {
        "docs.python.org",
        "developer.mozilla.org",
        "docs.rust-lang.org",
        "go.dev",
    }:
        source_quality_prior = 0.15
    try:
        search_rank = max(1, int(search_result.get("rank", 1)))
    except (TypeError, ValueError):
        search_rank = 1
    search_rank_prior = max(0.0, 0.08 - 0.02 * (search_rank - 1))
    evidence_rank_score = min(
        1.0,
        0.82 * resonance_score + source_quality_prior + search_rank_prior,
    )
    return source_quality_prior, search_rank_prior, evidence_rank_score


def _capture_wikipedia_extract(
    query: str,
    search_result: dict[str, object],
    *,
    timeout_seconds: float,
) -> dict[str, object]:
    page_title = str(search_result.get("page_title") or search_result.get("title") or "").strip()
    if not page_title:
        raise ValueError("research_wikipedia_page_title_missing")
    params = urlencode(
        {
            "action": "query",
            "prop": "extracts|info",
            "explaintext": 1,
            "exintro": 1,
            "titles": page_title,
            "inprop": "url",
            "format": "json",
            "formatversion": 2,
        }
    )
    retrieval_url = f"https://en.wikipedia.org/w/api.php?{params}"
    data = _fetch_json(retrieval_url, timeout_seconds=timeout_seconds)
    query_data = data.get("query") if isinstance(data, dict) else None
    pages = query_data.get("pages") if isinstance(query_data, dict) else None
    if not isinstance(pages, list) or not pages or not isinstance(pages[0], dict):
        raise ValueError("research_wikipedia_extract_missing")
    page = pages[0]
    extract = str(page.get("extract") or "").strip()
    if not extract:
        raise ValueError("research_wikipedia_extract_empty")
    final_url = _validate_public_url(
        str(page.get("fullurl") or search_result.get("url") or "")
    )
    excerpt, score, overlap = _relevant_excerpt(query, (extract,))
    source_quality_prior, search_rank_prior, evidence_rank_score = (
        _source_and_rank_priors(final_url, search_result, score)
    )
    body_record = {
        "search_result_ref": search_result.get("search_result_id"),
        "requested_url": str(search_result.get("url", "")),
        "retrieval_url": retrieval_url,
        "final_url": final_url,
        "title": str(page.get("title") or page_title)[:240],
        "content_type": "application/json; profile=mediawiki-plaintext-extract",
        "content_sha256": _sha256_text(extract),
        "excerpt": excerpt,
        "excerpt_sha256": _sha256_text(excerpt),
        "resonance_score": score,
        "source_quality_prior": source_quality_prior,
        "search_rank_prior": search_rank_prior,
        "evidence_rank_score": round(evidence_rank_score, 6),
        "matched_source_forms": overlap,
        "exact_excerpt_from_source": bool(excerpt),
        "candidate_evidence_only": True,
        "canonical": False,
    }
    return {
        "source_receipt_id": _stable_id("web_source_receipt", body_record),
        **body_record,
    }


def capture_public_page_evidence(
    query: str,
    search_result: dict[str, object],
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    requested_url = str(search_result.get("url", ""))
    final_url, content_type, body = _fetch(
        requested_url,
        timeout_seconds=timeout_seconds,
    )
    extractor = _PageTextExtractor()
    if "html" in content_type.casefold():
        extractor.feed(body)
        title = _SPACE.sub(" ", " ".join(extractor.title_parts)).strip()
        blocks = extractor.blocks
        requested_fragment = urlparse(requested_url).fragment
        if requested_fragment:
            anchored = [
                block
                for block, section_ref in zip(
                    extractor.blocks,
                    extractor.block_sections,
                )
                if section_ref == requested_fragment
            ]
            if anchored:
                blocks = anchored
    else:
        title = str(search_result.get("title", ""))
        blocks = [body]
    excerpt, score, overlap = _relevant_excerpt(query, blocks)
    source_quality_prior, search_rank_prior, evidence_rank_score = (
        _source_and_rank_priors(final_url, search_result, score)
    )
    body_record = {
        "search_result_ref": search_result.get("search_result_id"),
        "requested_url": requested_url,
        "final_url": final_url,
        "title": (title or str(search_result.get("title", "")))[:240],
        "content_type": content_type[:160],
        "content_sha256": _sha256_text(body),
        "excerpt": excerpt,
        "excerpt_sha256": _sha256_text(excerpt),
        "resonance_score": score,
        "source_quality_prior": source_quality_prior,
        "search_rank_prior": search_rank_prior,
        "evidence_rank_score": round(evidence_rank_score, 6),
        "matched_source_forms": overlap,
        "exact_excerpt_from_source": bool(excerpt),
        "candidate_evidence_only": True,
        "canonical": False,
    }
    return {
        "source_receipt_id": _stable_id("web_source_receipt", body_record),
        **body_record,
    }


def capture_public_source_evidence(
    query: str,
    search_result: dict[str, object],
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    """Capture through the provider-specific bounded source contract."""

    if (
        search_result.get("search_provider") == "wikipedia_mediawiki"
        and search_result.get("page_title")
    ):
        return _capture_wikipedia_extract(
            query,
            search_result,
            timeout_seconds=timeout_seconds,
        )
    return capture_public_page_evidence(
        query,
        search_result,
        timeout_seconds=timeout_seconds,
    )


@dataclass(frozen=True, slots=True)
class ResearchProvider:
    """Injectable connector contract used by the operator interpreter."""

    search: Callable[[str], tuple[dict[str, object], ...]]
    capture: Callable[[str, dict[str, object]], dict[str, object]]
    provider_id: str = "public_web_bounded_v1"


def default_research_provider() -> ResearchProvider:
    return ResearchProvider(
        search=lambda query: search_public_web(query),
        capture=lambda query, row: capture_public_source_evidence(query, row),
    )


def acquire_research_evidence(
    query: str,
    *,
    provider: ResearchProvider | None = None,
    max_pages: int = MAX_FETCHED_PAGES,
) -> dict[str, object]:
    """Search and capture candidate evidence with partial-failure receipts."""

    effective = provider or default_research_provider()
    errors: list[dict[str, str]] = []
    try:
        search_results = effective.search(str(query))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        search_results = ()
        errors.append(
            {
                "stage": "search",
                "reason_code": type(error).__name__,
                "detail": str(error)[:240],
            }
        )
    evidence: list[dict[str, object]] = []
    for row in search_results[: max(1, min(MAX_FETCHED_PAGES, int(max_pages)))]:
        try:
            captured = effective.capture(str(query), dict(row))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            errors.append(
                {
                    "stage": "capture",
                    "reason_code": type(error).__name__,
                    "detail": str(error)[:240],
                }
            )
            continue
        if captured.get("excerpt"):
            evidence.append(captured)

    evidence.sort(
        key=lambda row: float(
            row.get("evidence_rank_score", row.get("resonance_score", 0.0))
        ),
        reverse=True,
    )
    body = {
        "provider_id": effective.provider_id,
        "query_sha256": _sha256_text(str(query)),
        "search_result_refs": tuple(
            str(row.get("search_result_id")) for row in search_results
        ),
        "source_receipt_refs": tuple(
            str(row.get("source_receipt_id")) for row in evidence
        ),
        "search_result_count": len(search_results),
        "evidence_count": len(evidence),
        "error_count": len(errors),
        "candidate_evidence_only": True,
        "canonical": False,
    }
    return {
        "acquisition_id": _stable_id("research_acquisition", body),
        "status": "EVIDENCE_CAPTURED" if evidence else "NO_EVIDENCE_CAPTURED",
        **body,
        "search_results": [dict(row) for row in search_results],
        "evidence": evidence,
        "errors": errors,
        "boundary": research_acquisition_boundary(),
    }


__all__ = (
    "RESEARCH_ACQUISITION_VERSION",
    "ResearchProvider",
    "acquire_research_evidence",
    "capture_public_page_evidence",
    "capture_public_source_evidence",
    "default_research_provider",
    "research_acquisition_boundary",
    "search_public_web",
)
