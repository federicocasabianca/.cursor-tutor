import os
import sys
from typing import List, Dict, Any, Optional
from .model import LTRModel


class RankingService:
    """Service for re-ranking search results using Learning-to-Rank model"""
    
    def __init__(self, model_path: str = 'models/ltr_model.pkl'):
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained LTR model"""
        try:
            self.model = LTRModel(self.model_path)
            if self.model.is_trained():
                self.model.load_model()
                print("LTR ranking service initialized successfully")
            else:
                print("Warning: No trained LTR model found. Using MongoDB scores only.")
                self.model = None
        except Exception as e:
            print(f"Error loading LTR model: {e}")
            print("Falling back to MongoDB scores only")
            self.model = None
    
    def re_rank_results(self, query: str, documents: List[Dict[str, Any]], 
                       mongodb_scores: List[float]) -> List[Dict[str, Any]]:
        """
        Re-rank search results using the LTR model
        
        Args:
            query: Search query
            documents: List of documents from MongoDB search
            mongodb_scores: List of original MongoDB scores
            
        Returns:
            Re-ranked list of documents with updated scores
        """
        if not self.model or not documents:
            return documents
        
        try:
            # Get predicted scores from LTR model
            ltr_scores = self.model.predict_scores(query, documents, mongodb_scores)
            
            # Create document-score pairs
            doc_score_pairs = list(zip(documents, ltr_scores))
            
            # Sort by LTR score descending
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Update documents with new scores
            re_ranked_documents = []
            for doc, ltr_score in doc_score_pairs:
                # Create a copy of the document
                doc_copy = doc.copy()
                # Update the score with LTR prediction
                doc_copy['score'] = round(ltr_score, 2)
                # Keep original MongoDB score for reference
                doc_copy['mongodb_score'] = doc.get('score', 0.0)
                re_ranked_documents.append(doc_copy)
            
            return re_ranked_documents
            
        except Exception as e:
            print(f"Error in LTR re-ranking: {e}")
            # Fall back to original documents
            return documents
    
    def get_ranking_info(self) -> Dict[str, Any]:
        """Get information about the ranking service"""
        return {
            'model_loaded': self.model is not None,
            'model_path': self.model_path,
            'features': self.model.feature_names if self.model else []
        }


# Global ranking service instance
_ranking_service = None


def get_ranking_service() -> RankingService:
    """Get the global ranking service instance"""
    global _ranking_service
    if _ranking_service is None:
        _ranking_service = RankingService()
    return _ranking_service


def re_rank_search_results(query: str, search_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Re-rank search results using the LTR model
    
    Args:
        query: Search query
        search_results: Results from MongoDB search
        
    Returns:
        Updated search results with re-ranked documents
    """
    ranking_service = get_ranking_service()
    
    # Extract documents and scores
    documents = search_results.get('results', [])
    mongodb_scores = [doc.get('score', 0.0) for doc in documents]
    
    # Re-rank documents
    re_ranked_documents = ranking_service.re_rank_results(query, documents, mongodb_scores)
    
    # Update search results
    updated_results = search_results.copy()
    updated_results['results'] = re_ranked_documents
    
    # Add ranking info
    updated_results['ranking_info'] = ranking_service.get_ranking_info()
    
    return updated_results 