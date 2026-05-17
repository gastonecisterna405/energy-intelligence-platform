"""NLTK-based text analysis for analyst comments and energy snippets."""

from __future__ import annotations

from collections import Counter

import pandas as pd

POSITIVE_TERMS = {"stable", "supports", "reliability", "resilience", "improve", "predictable", "low-carbon", "reduce"}
NEGATIVE_TERMS = {"risk", "high", "volatility", "outages", "concerns", "dependency", "pressure", "intermittency"}


def _stopwords() -> set[str]:
    try:
        from nltk.corpus import stopwords

        return set(stopwords.words("english"))
    except Exception:
        return {
            "a",
            "an",
            "and",
            "are",
            "as",
            "be",
            "by",
            "can",
            "during",
            "for",
            "in",
            "is",
            "may",
            "of",
            "or",
            "the",
            "to",
            "with",
        }


def tokenize_comments(comments: pd.DataFrame) -> list[str]:
    """Tokenize comments, lowercase and remove stopwords."""
    try:
        from nltk.tokenize import wordpunct_tokenize
    except Exception as exc:
        raise RuntimeError("NLTK must be installed for the NLP module.") from exc

    stop_words = _stopwords()
    tokens: list[str] = []
    for text in comments["comment"].fillna(""):
        for token in wordpunct_tokenize(str(text).lower()):
            if token.isalpha() and token not in stop_words and len(token) > 2:
                tokens.append(token)
    return tokens


def analyze_energy_text(comments: pd.DataFrame, top_n: int = 20) -> dict:
    """Convert unstructured analyst text into simple keyword and sentiment signals."""
    tokens = tokenize_comments(comments)
    frequencies = Counter(tokens)
    positive_hits = sum(frequencies.get(term, 0) for term in POSITIVE_TERMS)
    negative_hits = sum(frequencies.get(term, 0) for term in NEGATIVE_TERMS)
    sentiment_score = (positive_hits - negative_hits) / max(positive_hits + negative_hits, 1)
    top_terms = pd.DataFrame(frequencies.most_common(top_n), columns=["term", "frequency"])
    label_summary = comments.groupby("label", as_index=False).size() if "label" in comments.columns else pd.DataFrame()
    return {
        "tokens": tokens,
        "top_terms": top_terms,
        "sentiment_score": float(sentiment_score),
        "positive_term_hits": int(positive_hits),
        "negative_term_hits": int(negative_hits),
        "label_summary": label_summary,
    }
