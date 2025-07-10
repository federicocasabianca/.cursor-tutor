import requests
import spacy
from spacy.matcher import PhraseMatcher
from taxonomy.loader import load_taxonomy_terms

# Load spaCy German model
nlp = spacy.load('de_core_news_sm')

# Load taxonomy terms
TAXONOMY_TERMS = load_taxonomy_terms()

# Setup PhraseMatchers for each intent
PHRASE_MATCHERS = {}
for intent, terms in TAXONOMY_TERMS.items():
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(term) for term in terms if term]
    if patterns:
        matcher.add(intent, patterns)
    PHRASE_MATCHERS[intent] = matcher

def call_intent_api(query: str):
    """Call the external intent detection API and return detected categories and grade levels with confidence."""
    url = "https://srch-main.api.eduki.info/api/v3/query-intent/predict"
    headers = {"Content-Type": "application/json"}
    payload = {"text": query}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()
        return result.get('tags', {})
    except Exception as e:
        print(f"Intent API error: {e}")
        return {}

def detect_intents_spacy(query):
    doc = nlp(query)
    detected = set()
    for intent, matcher in PHRASE_MATCHERS.items():
        matches = matcher(doc)
        if matches:
            detected.add(intent)
    return list(detected)
