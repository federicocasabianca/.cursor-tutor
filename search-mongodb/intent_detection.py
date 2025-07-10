import json
import sys
from intents.service import detect_intents_spacy
from typing import Dict, List, Tuple

SEARCHES_PATH = './search-mongodb/searches/searches.json'

def detect_intents_with_confidence(query: str) -> List[Tuple[str, float]]:
    """
    Detect intents from a query and return them with confidence scores.
    Confidence is calculated based on:
    1. Number of matches for each intent
    2. Position of matches in the query (earlier matches get higher confidence)
    3. Length of matched terms (longer matches get higher confidence)
    
    Returns a list of tuples (intent, confidence) sorted by confidence in descending order.
    """
    doc = nlp(query.lower())
    intent_scores: Dict[str, float] = {}
    
    for intent, matcher in PHRASE_MATCHERS.items():
        matches = matcher(doc)
        if matches:
            # Calculate confidence for this intent
            total_score = 0.0
            for _, start, end in matches:
                # Get the matched text
                matched_text = doc[start:end].text
                
                # Base score from match length (longer matches are more significant)
                length_score = len(matched_text) / len(query)
                
                # Position score (earlier matches are more significant)
                position_score = 1.0 - (start / len(doc))
                
                # Combine scores
                match_score = (length_score + position_score) / 2
                total_score += match_score
            
            # Normalize score to 0-1 range
            intent_scores[intent] = min(1.0, total_score)
    
    # If no intents detected, return unknown with low confidence
    if not intent_scores:
        return [('unknown', 0.1)]
    
    # Sort intents by confidence score
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_intents

def run_batch_detection(n=30):
    with open(SEARCHES_PATH, encoding='utf-8') as f:
        searches = json.load(f)
    for entry in searches[:n]:
        query = entry['search_keyword']
        intents_with_confidence = detect_intents_with_confidence(query)
        print(f"Query: {query}")
        print("Detected intents with confidence:")
        for intent, confidence in intents_with_confidence:
            print(f"  - {intent}: {confidence:.2f}")
        print()

def run_interactive():
    print("Enter a search query (or 'exit' to quit):")
    while True:
        query = input('> ').strip()
        if query.lower() in {'exit', 'quit'}:
            break
        intents_with_confidence = detect_intents_with_confidence(query)
        print("Detected intents with confidence:")
        for intent, confidence in intents_with_confidence:
            print(f"  - {intent}: {confidence:.2f}")
        print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            run_interactive()
        else:
            # If a query is provided as an argument, process it directly
            query = ' '.join(sys.argv[1:])
            intents_with_confidence = detect_intents_with_confidence(query)
            print(f"Query: {query}")
            print("Detected intents with confidence:")
            for intent, confidence in intents_with_confidence:
                print(f"  - {intent}: {confidence:.2f}")
    else:
        run_batch_detection() 