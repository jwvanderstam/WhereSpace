# -*- coding: utf-8 -*-
"""
RAG Evaluation Service
Handles evaluation of retrieval quality
"""
import logging
import statistics
from typing import List, Dict, Optional
from config import get_config

logger = logging.getLogger(__name__)

class EvaluationService:
    """Service for RAG evaluation"""
    
    def __init__(self, config=None):
        """Initialize evaluation service"""
        if config is None:
            config = get_config()
        
        self.config = config
        logger.info("Evaluation service initialized")
    
    def generate_test_queries(self, db_service, llm_service, sample_size: int = 3) -> List[Dict]:
        """Generate test queries from ingested documents
        
        Args:
            db_service: DatabaseService instance
            llm_service: LLMService instance
            sample_size: Number of test queries to generate
            
        Returns:
            List of test query dictionaries
        """
        test_queries = []
        
        try:
            # Get sample documents
            documents = db_service.list_documents()
            
            if not documents or len(documents) == 0:
                logger.warning("No documents available for test query generation")
                return []
            
            # Take sample of documents (limit to avoid long evaluation)
            import random
            sample_docs = random.sample(documents, min(sample_size, len(documents)))
            
            for doc in sample_docs:
                # Get a chunk from this document
                chunks = db_service.get_document_chunks(doc['file_path'], limit=1)
                
                if chunks and len(chunks) > 0:
                    # Use first chunk as basis for query
                    chunk_text = chunks[0]['content']
                    
                    # Extract first sentence or first N words as query
                    words = chunk_text.split()[:8]
                    query = ' '.join(words)
                    
                    if len(query) > 15:  # Meaningful query
                        test_queries.append({
                            'query': query,
                            'expected_file': doc['file_name'],
                            'source_file': doc['file_name']
                        })
            
            logger.info(f"Generated {len(test_queries)} test queries from {len(sample_docs)} documents")
            return test_queries
            
        except Exception as e:
            logger.error(f"Error generating test queries: {e}")
            return []
    
    def evaluate_retrieval(
        self,
        db_service,
        llm_service,
        test_queries: List[Dict] = None,
        top_k: int = 5
    ) -> Dict:
        """Evaluate retrieval quality
        
        Args:
            db_service: DatabaseService instance
            llm_service: LLMService instance
            test_queries: List of test queries (auto-generated if None)
            top_k: Number of results to retrieve per query
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Starting RAG evaluation...")
        
        # Auto-generate queries if not provided
        if not test_queries:
            test_queries = self.generate_test_queries(db_service, llm_service)
        
        if not test_queries:
            logger.warning("No test queries available")
            return {
                'hit_rate': 0,
                'mrr': 0,
                'avg_similarity': 0,
                'total_tests': 0,
                'hits': 0,
                'error': 'No test queries available'
            }
        
        hits = 0
        reciprocal_ranks = []
        similarities = []
        results_details = []
        
        for i, test in enumerate(test_queries, 1):
            query = test['query']
            expected_file = test.get('expected_file', '')
            
            logger.info(f"Testing query {i}/{len(test_queries)}: {query[:50]}...")
            
            # Generate embedding
            embedding = llm_service.generate_embedding(query)
            if not embedding:
                logger.warning(f"Failed to generate embedding for query: {query[:50]}")
                continue
            
            # Search for similar chunks
            results = db_service.search_similar_chunks(embedding, top_k=top_k)
            
            if not results:
                logger.warning(f"No results for query: {query[:50]}")
                continue
            
            # Check if expected file is in results
            found_rank = None
            for rank, result in enumerate(results, 1):
                similarities.append(result['similarity'])
                
                if expected_file and result['file_name'] == expected_file:
                    found_rank = rank
                    hits += 1
                    logger.info(f"  ? Found at rank {rank} with similarity {result['similarity']:.3f}")
                    break
            
            if found_rank:
                reciprocal_ranks.append(1.0 / found_rank)
            else:
                if expected_file:
                    logger.warning(f"  ? Expected file '{expected_file}' not in top {top_k}")
            
            # Store result details
            results_details.append({
                'query': query[:100],
                'found': found_rank is not None,
                'rank': found_rank,
                'top_result': results[0]['file_name'] if results else None,
                'top_similarity': results[0]['similarity'] if results else 0
            })
        
        # Calculate metrics
        total_tests = len(test_queries)
        hit_rate = (hits / total_tests * 100) if total_tests > 0 else 0
        mrr = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0
        avg_similarity = statistics.mean(similarities) if similarities else 0
        
        evaluation_result = {
            'hit_rate': round(hit_rate, 1),
            'mrr': round(mrr, 3),
            'avg_similarity': round(avg_similarity, 3),
            'total_tests': total_tests,
            'hits': hits,
            'failed': total_tests - hits,
            'results': results_details[:5]  # First 5 results for display
        }
        
        logger.info(f"Evaluation complete: Hit Rate={hit_rate:.1f}%, MRR={mrr:.3f}, Avg Similarity={avg_similarity:.3f}")
        
        return evaluation_result
    
    def get_performance_assessment(self, metrics: Dict) -> Dict:
        """Assess performance and provide recommendations
        
        Args:
            metrics: Evaluation metrics dictionary
            
        Returns:
            Assessment with level and recommendations
        """
        hit_rate = metrics.get('hit_rate', 0)
        avg_similarity = metrics.get('avg_similarity', 0)
        
        # Determine performance level
        if hit_rate >= 80:
            level = 'excellent'
            color = 'success'
            icon = '?'
            message = 'Excellent retrieval performance!'
        elif hit_rate >= 60:
            level = 'good'
            color = 'primary'
            icon = '??'
            message = 'Good retrieval quality with room for improvement'
        elif hit_rate >= 40:
            level = 'fair'
            color = 'warning'
            icon = '??'
            message = 'Fair performance - optimization recommended'
        else:
            level = 'poor'
            color = 'danger'
            icon = '?'
            message = 'Poor performance - action required'
        
        # Generate recommendations
        recommendations = []
        
        if hit_rate < 60:
            recommendations.append('Consider re-indexing with optimized chunk size')
            recommendations.append('Ensure documents contain relevant content')
        
        if avg_similarity < 0.5:
            recommendations.append('Low similarity scores - check embedding model')
            recommendations.append('Verify document content quality')
        
        if metrics.get('total_tests', 0) < 5:
            recommendations.append('More documents needed for reliable evaluation')
        
        if not recommendations:
            recommendations.append('System is performing well - no immediate actions needed')
        
        return {
            'level': level,
            'color': color,
            'icon': icon,
            'message': message,
            'recommendations': recommendations
        }
