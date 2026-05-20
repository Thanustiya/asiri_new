"""
BML College NLP Engine
Uses TF-IDF + SVM for fast, accurate intent classification
No external AI API needed - fully local, sub-millisecond inference
"""

import json
import numpy as np
import pickle
import os
import re
import random
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
for resource in ['punkt', 'wordnet', 'stopwords', 'averaged_perceptron_tagger', 'punkt_tab']:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

logger = logging.getLogger(__name__)


class ConversationContext:
    """Track conversation context for multi-turn conversations."""
    def __init__(self):
        self.last_intent = None
        self.last_topic = None
        self.turn_count = 0
        self.history = []

    def update(self, user_msg: str, intent: str, response: str):
        self.last_intent = intent
        self.turn_count += 1
        self.history.append({
            "user": user_msg,
            "intent": intent,
            "bot": response
        })
        # Keep last 10 turns for context
        if len(self.history) > 10:
            self.history.pop(0)


class NLPEngine:
    """
    Intent classification engine using TF-IDF + SVM pipeline.
    Trains in < 2 seconds, infers in < 5ms. No external API required.
    """

    def __init__(self, intents_file: str = "intents.json", model_path: str = "model.pkl"):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english')) - {
            'not', 'no', 'when', 'where', 'what', 'how', 'which', 'who', 'why'
        }
        self.intents = []
        self.pipeline = None
        self.label_encoder = LabelEncoder()
        self.model_path = model_path
        self.intents_file = intents_file
        self.intent_map = {}

        self._load_intents()
        self._build_intent_map()

        if os.path.exists(self.model_path):
            try:
                self._load_model()
                logger.info("Loaded pre-trained model from disk")
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Re-training...")
                self.train()
        else:
            self.train()

    def _load_intents(self):
        with open(self.intents_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.intents = data['intents']
        logger.info(f"Loaded {len(self.intents)} intents")

    def _build_intent_map(self):
        """Build a fast lookup dict: tag -> intent data."""
        for intent in self.intents:
            self.intent_map[intent['tag']] = intent

    def preprocess(self, text: str) -> str:
        """Clean, tokenize, and lemmatize text."""
        text = text.lower().strip()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        try:
            tokens = word_tokenize(text)
            tokens = [
                self.lemmatizer.lemmatize(t)
                for t in tokens
                if t not in self.stop_words and len(t) > 1
            ]
            return ' '.join(tokens) if tokens else text
        except Exception:
            return text

    def train(self):
        """Train TF-IDF + SVM pipeline on intent patterns."""
        X, y = [], []
        for intent in self.intents:
            for pattern in intent['patterns']:
                X.append(self.preprocess(pattern))
                y.append(intent['tag'])

        y_encoded = self.label_encoder.fit_transform(y)

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=8000,
                min_df=1,
                sublinear_tf=True,
                analyzer='word'
            )),
            ('clf', SVC(
                kernel='linear',
                probability=True,
                C=1.5,
                class_weight='balanced'
            ))
        ])

        self.pipeline.fit(X, y_encoded)
        self._save_model()

        # Quick accuracy check
        scores = cross_val_score(self.pipeline, X, y_encoded, cv=3, scoring='accuracy')
        logger.info(f"Model trained! Cross-val accuracy: {np.mean(scores):.2%}")

    def _save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'pipeline': self.pipeline,
                'label_encoder': self.label_encoder
            }, f)

    def _load_model(self):
        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
        self.pipeline = data['pipeline']
        self.label_encoder = data['label_encoder']

    def predict_intent(self, text: str, threshold: float = 0.25) -> tuple[str, float]:
        """
        Predict intent from text.
        Returns (tag, confidence). Falls back to 'fallback' if confidence < threshold.
        """
        processed = self.preprocess(text)
        if not processed.strip():
            return 'fallback', 0.0

        proba = self.pipeline.predict_proba([processed])[0]
        max_proba = float(np.max(proba))

        if max_proba < threshold:
            return 'fallback', max_proba

        label_idx = int(np.argmax(proba))
        tag = self.label_encoder.inverse_transform([label_idx])[0]
        return tag, max_proba

    def get_response_data(self, tag: str) -> dict:
        """Get response data for a given intent tag."""
        intent = self.intent_map.get(tag)
        if not intent:
            intent = self.intent_map.get('fallback', {})

        return {
            'response': random.choice(intent.get('responses', ["I'm here to help! Please choose an option below."])),
            'options': intent.get('options', []),
            'action': intent.get('action', None),
            'tag': tag
        }

    def process_message(self, text: str, context: ConversationContext = None) -> dict:
        """
        Full pipeline: text → intent → response.
        Returns dict with response, options, action, confidence.
        """
        # Handle empty input
        if not text or not text.strip():
            return self.get_response_data('fallback')

        # Detect human agent requests regardless of confidence
        agent_keywords = ['human', 'agent', 'person', 'staff', 'speak to someone',
                          'talk to', 'real person', 'advisor', 'live chat']
        if any(kw in text.lower() for kw in agent_keywords):
            result = self.get_response_data('human_agent')
            result['confidence'] = 1.0
            return result

        tag, confidence = self.predict_intent(text)
        result = self.get_response_data(tag)
        result['confidence'] = confidence

        # Context-aware: if following up on a topic, stay relevant
        if context and confidence < 0.4 and context.last_intent:
            # Try to stay in the same topic area
            topic_hint = context.last_intent
            result['context_hint'] = topic_hint

        return result

    def retrain(self):
        """Force retrain (useful after adding new intents)."""
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
        self._load_intents()
        self._build_intent_map()
        self.train()
        logger.info("Model retrained successfully")


# Singleton instance
_engine_instance = None

def get_engine(intents_file: str = "intents.json") -> NLPEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NLPEngine(intents_file=intents_file)
    return _engine_instance