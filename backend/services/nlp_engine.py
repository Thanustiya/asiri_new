# backend/services/nlp_engine.py
"""
NLP Engine for BML College Chatbot
Tier 1: Keyword/phrase matching (instant)
Tier 2: TF-IDF cosine similarity (fast)
Tier 3: Ollama phi3 (complex queries)
"""

import re
import logging
from typing import Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fuzzywuzzy import fuzz
from services.knowledge_base import COLLEGE_KNOWLEDGE, QUICK_REPLY_MAP

logger = logging.getLogger(__name__)


class NLPEngine:
    """Fast intent classifier with multi-tier matching."""

    CONFIDENCE_THRESHOLD_HIGH = 70   # Use KB response directly
    CONFIDENCE_THRESHOLD_LOW = 40    # Suggest but mention uncertainty

    def __init__(self):
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_matrix = None
        self._intent_list: list = []
        self._build_index()

    # ── Build TF-IDF index ─────────────────────────────────────────────────
    def _build_index(self):
        """Build TF-IDF index from knowledge base keywords."""
        corpus = []
        intents = []

        for intent_name, data in COLLEGE_KNOWLEDGE.items():
            if intent_name in ("fallback", "welcome"):
                continue
            if "keywords" in data:
                text = " ".join(data["keywords"])
                corpus.append(text)
                intents.append(intent_name)

        if corpus:
            self._vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                analyzer="word",
                stop_words="english"
            )
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
            self._intent_list = intents
            logger.info(f"✅ TF-IDF index built with {len(corpus)} intents")

    # ── Normalise input ────────────────────────────────────────────────────
    @staticmethod
    def _clean(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    # ── Tier 1: Quick-reply exact match ───────────────────────────────────
    def _quick_reply_match(self, text: str) -> Optional[str]:
        t = self._clean(text)
        return QUICK_REPLY_MAP.get(t)

    # ── Tier 2: Keyword fuzzy match ────────────────────────────────────────
    def _keyword_match(self, text: str) -> Tuple[Optional[str], int]:
        t = self._clean(text)
        best_intent = None
        best_score = 0

        for intent_name, data in COLLEGE_KNOWLEDGE.items():
            if "keywords" not in data:
                continue
            for kw in data["keywords"]:
                # Exact substring match
                if kw in t or t in kw:
                    score = 90
                    if score > best_score:
                        best_score = score
                        best_intent = intent_name
                        break
                # Fuzzy partial match
                score = fuzz.partial_ratio(kw, t)
                if score > best_score and score >= 75:
                    best_score = score
                    best_intent = intent_name

        return best_intent, best_score

    # ── Tier 3: TF-IDF cosine similarity ──────────────────────────────────
    def _tfidf_match(self, text: str) -> Tuple[Optional[str], int]:
        if self._vectorizer is None:
            return None, 0
        t = self._clean(text)
        try:
            vec = self._vectorizer.transform([t])
            sims = cosine_similarity(vec, self._tfidf_matrix).flatten()
            best_idx = int(np.argmax(sims))
            best_score = int(sims[best_idx] * 100)
            if best_score >= self.CONFIDENCE_THRESHOLD_LOW:
                return self._intent_list[best_idx], best_score
        except Exception as e:
            logger.warning(f"TF-IDF error: {e}")
        return None, 0

    # ── Main classify method ───────────────────────────────────────────────
    def classify(self, text: str) -> Tuple[str, int, bool]:
        """
        Returns: (intent_name, confidence_0_100, needs_ollama)
        """
        # Tier 1: quick reply exact
        qr_intent = self._quick_reply_match(text)
        if qr_intent:
            return qr_intent, 95, False

        # Tier 2: keyword fuzzy
        kw_intent, kw_conf = self._keyword_match(text)
        if kw_conf >= self.CONFIDENCE_THRESHOLD_HIGH:
            return kw_intent, kw_conf, False

        # Tier 3: TF-IDF
        tfidf_intent, tfidf_conf = self._tfidf_match(text)
        if tfidf_conf >= self.CONFIDENCE_THRESHOLD_HIGH:
            return tfidf_intent, tfidf_conf, False

        # Merge: take the higher confidence result
        if kw_conf >= tfidf_conf and kw_conf >= self.CONFIDENCE_THRESHOLD_LOW:
            return kw_intent, kw_conf, False
        if tfidf_conf >= self.CONFIDENCE_THRESHOLD_LOW:
            return tfidf_intent, tfidf_conf, False

        # Low confidence → send to Ollama if it's a real question
        if len(text.split()) >= 4:
            return "fallback", 0, True  # needs_ollama = True

        return "fallback", 0, False

    # ── Get response from knowledge base ──────────────────────────────────
    def get_response(self, intent: str) -> Tuple[str, list]:
        """Get response text and quick replies for an intent."""
        data = COLLEGE_KNOWLEDGE.get(intent, COLLEGE_KNOWLEDGE["fallback"])
        response = data.get("response", COLLEGE_KNOWLEDGE["fallback"]["response"])
        quick_replies = data.get("quick_replies", [])
        return response, quick_replies

    # ── Detect human agent request ────────────────────────────────────────
    def is_human_request(self, text: str) -> bool:
        t = self._clean(text)
        triggers = [
            "human", "agent", "person", "staff", "real person", "speak to someone",
            "talk to someone", "live chat", "not robot", "not a bot", "live agent",
            "customer service", "support team", "advisor", "counsellor", "transfer"
        ]
        return any(t in t_lower or t_lower in t for t_lower in triggers) or \
               any(fuzz.partial_ratio(tr, t) >= 80 for tr in triggers)

    # ── Detect farewell ───────────────────────────────────────────────────
    def is_farewell(self, text: str) -> bool:
        t = self._clean(text)
        farewells = ["bye", "goodbye", "see you", "farewell", "take care", "end chat", "done"]
        return any(f in t for f in farewells)


# Singleton
nlp_engine = NLPEngine()