import numpy as np
import re
from html import unescape
from html.parser import HTMLParser
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from datetime import datetime
import xml.etree.ElementTree as ET

eigen_tool = {
    "type": "function",
    "name": "get_eigenvalues",
    "description": "Get eigenvalues of a matrix",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            }
        },
        "required": ["a"],
        "additionalProperties": False,
    }
}

next_devotional_tool = {
    "type": "function",
    "name": "get_next_devotional",
    "description": "Get the next upcoming BYU devotional speaker from the Devotionals and Forums calendar.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
}

find_lds_quote_tool = {
    "type": "function",
    "name": "find_lds_quote",
    "description": "Search LDS General Conference talks to find an exact quote based on a paraphrased quote and speaker name. Returns the exact quote and a link to the talk.",
    "parameters": {
        "type": "object",
        "properties": {
            "paraphrased_quote": {
                "type": "string",
                "description": "A paraphrased or partial version of the quote you're looking for"
            },
            "speaker_name": {
                "type": "string",
                "description": "The name of the speaker who gave the talk"
            }
        },
        "required": ["paraphrased_quote", "speaker_name"],
        "additionalProperties": False,
    }
}

def _to_json_value(value):
    if np.iscomplexobj(value):
        complex_value = complex(value)
        if np.isclose(complex_value.imag, 0.0):
            return float(complex_value.real)
        return {
            "real": float(complex_value.real),
            "imag": float(complex_value.imag),
        }
    return float(value)

def get_eigenvalues(a):
    eigenvalues = np.linalg.eigvals(a)
    return [_to_json_value(value) for value in eigenvalues]

def get_next_devotional():
    with urlopen("https://calendar.byu.edu/api/Events?categories=7", timeout=10) as response:
        root = ET.fromstring(response.read())

    now = datetime.now()
    next_event = None

    for item in root.findall("item"):
        title = (item.findtext("Title") or "").strip()
        start_text = (item.findtext("StartDateTime") or "").strip()

        if not title.startswith("Devotional:"):
            continue
        if not start_text:
            continue

        start_at = datetime.strptime(start_text, "%Y-%m-%d %H:%M:%S")
        if start_at < now:
            continue

        speaker = title.removeprefix("Devotional:").strip()
        candidate = {
            "speaker": speaker,
            "title": title,
            "date": start_at.strftime("%A, %B %d, %Y"),
            "time": start_at.strftime("%I:%M %p"),
            "location": (item.findtext("LocationName") or "").strip(),
            "url": (item.findtext("FullUrl") or "").strip(),
            "description": (item.findtext("ShortDescription") or "").strip(),
            "start_at": start_at,
        }

        if next_event is None or start_at < next_event["start_at"]:
            next_event = candidate

    if next_event is None:
        return {"message": "No upcoming devotional with a listed speaker was found."}

    next_event.pop("start_at")
    return next_event


_GC_BASE_URL = "https://www.churchofjesuschrist.org"
_GC_SPEAKER_URL = f"{_GC_BASE_URL}/study/general-conference/speakers"
_REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}
_BLOCK_TAGS = {"p", "li", "blockquote", "h2", "h3", "h4"}


class _TalkHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.author_parts = []
        self.paragraphs = []
        self._in_author = False
        self._in_body = False
        self._body_depth = 0
        self._skip_depth = 0
        self._block_depth = 0
        self._current_block = []

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        classes = set((attr_map.get("class") or "").split())

        if tag == "p" and "author-name" in classes:
            self._in_author = True

        if tag == "div" and "body" in classes and not self._in_body:
            self._in_body = True
            self._body_depth = 1
            return

        if self._in_body and tag == "div":
            self._body_depth += 1

        if not self._in_body:
            return

        if tag in {"script", "style", "sup"}:
            self._skip_depth += 1
            return

        if tag in _BLOCK_TAGS:
            if self._block_depth == 0:
                self._current_block = []
            self._block_depth += 1

    def handle_endtag(self, tag):
        if self._in_author and tag == "p":
            self._in_author = False

        if self._in_body and tag in {"script", "style", "sup"} and self._skip_depth > 0:
            self._skip_depth -= 1
            return

        if self._in_body and tag in _BLOCK_TAGS and self._block_depth > 0:
            self._block_depth -= 1
            if self._block_depth == 0:
                block_text = _clean_text("".join(self._current_block))
                if block_text:
                    self.paragraphs.append(block_text)
                self._current_block = []

        if self._in_body and tag == "div":
            self._body_depth -= 1
            if self._body_depth == 0:
                self._in_body = False

    def handle_data(self, data):
        if self._in_author:
            self.author_parts.append(data)

        if self._in_body and self._skip_depth == 0:
            self._current_block.append(data)

    @property
    def author(self):
        return _clean_text("".join(self.author_parts))


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _normalize_text(text: str) -> str:
    normalized = unescape(text).lower()
    normalized = normalized.replace("\u2019", "'")
    normalized = normalized.replace("\u2018", "'")
    normalized = normalized.replace("\u201c", '"')
    normalized = normalized.replace("\u201d", '"')
    normalized = normalized.replace("\u2013", "-")
    normalized = normalized.replace("\u2014", "-")
    normalized = re.sub(r"[^a-z0-9\s']", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _fetch_html(url: str) -> str:
    request = Request(url, headers=_REQUEST_HEADERS)
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _speaker_slug(name: str) -> str:
    slug = _normalize_text(name)
    slug = slug.replace("'", "")
    return slug.replace(" ", "-")


def _extract_talk_links_from_speaker_page(page_html: str) -> list[str]:
    links = re.findall(r'(/study/general-conference/\d{4}/\d{2}/[^"?#\\s]+)', page_html)
    unique_links = []
    seen = set()
    for link in links:
        full_url = urljoin(_GC_BASE_URL, link)
        if full_url in seen:
            continue
        seen.add(full_url)
        unique_links.append(full_url)
    return unique_links


def _extract_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _find_exact_match(paragraphs: list[str], query: str) -> str | None:
    normalized_query = _normalize_text(query).strip(" '")
    if not normalized_query:
        return None

    for paragraph in paragraphs:
        paragraph_sentences = _extract_sentences(paragraph)
        for sentence in paragraph_sentences:
            if normalized_query in _normalize_text(sentence):
                return sentence

    for paragraph in paragraphs:
        if normalized_query in _normalize_text(paragraph):
            return paragraph

    return None


def _similarity_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_lds_quote(paraphrased_quote: str, speaker_name: str):
    try:
        speaker_page_url = f"{_GC_SPEAKER_URL}/{_speaker_slug(speaker_name)}?lang=eng"
        speaker_page_html = _fetch_html(speaker_page_url)
        talk_links = _extract_talk_links_from_speaker_page(speaker_page_html)

        if not talk_links:
            return {
                "error": f"Could not find a General Conference speaker page for {speaker_name}."
            }

        exact_match = None
        best_match = None
        best_similarity = 0.0
        query_keywords = {
            word for word in _normalize_text(paraphrased_quote).split() if len(word) > 3
        }

        for talk_url in talk_links:
            try:
                parser = _TalkHTMLParser()
                parser.feed(_fetch_html(talk_url))

                if not parser.paragraphs:
                    continue

                exact_quote = _find_exact_match(parser.paragraphs, paraphrased_quote)
                if exact_quote:
                    exact_match = {
                        "exact_quote": exact_quote,
                        "talk_url": talk_url,
                        "speaker": parser.author or speaker_name,
                    }
                    break

                sentences = []
                for paragraph in parser.paragraphs:
                    sentences.extend(_extract_sentences(paragraph))

                for sentence in sentences:
                    normalized_sentence = _normalize_text(sentence)
                    keyword_overlap = len(query_keywords & set(normalized_sentence.split()))
                    similarity = _similarity_ratio(_normalize_text(paraphrased_quote), normalized_sentence)

                    if query_keywords:
                        keyword_score = keyword_overlap / len(query_keywords)
                    else:
                        keyword_score = 0.0

                    composite_score = max(similarity, keyword_score)
                    if composite_score > best_similarity:
                        best_similarity = composite_score
                        best_match = {
                            "exact_quote": sentence,
                            "talk_url": talk_url,
                            "speaker": parser.author or speaker_name,
                        }

            except Exception:
                continue

        if exact_match:
            return exact_match

        if best_match and best_similarity >= 0.55:
            return best_match

        return {
            "error": f"Could not find a matching quote from {speaker_name} in general conference talks."
        }

    except Exception as error:
        return {
            "error": f"Error searching for LDS conference talks: {error}"
        }