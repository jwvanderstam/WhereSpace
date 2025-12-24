# -*- coding: utf-8 -*-
"""
RAG Evaluation Framework
========================

Enhanced evaluation tools for testing retrieval quality with automatic
diagnostics and improvement recommendations.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

try:
    import requests
except ImportError:
    logger.error("requests not installed. Run: pip install requests")
    sys.exit(1)

# Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "vectordb"
PG_USER = "postgres"
PG_PASSWORD = "Mutsmuts10"
PG_TABLE = "documents"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_EMBED_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for test query."""
    try:
        resp = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json().get("embedding")
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None


def get_database_stats() -> Dict:
    """Get statistics about indexed documents."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, database=PG_DATABASE,
            user=PG_USER, password=PG_PASSWORD
        )
        
        stats = {}
        
        with conn.cursor() as cur:
            # Total documents and chunks
            cur.execute(sql.SQL("""
                SELECT 
                    COUNT(DISTINCT file_path) as doc_count,
                    COUNT(*) as chunk_count,
                    AVG(LENGTH(chunk_content)) as avg_chunk_size
                FROM {};
            """).format(sql.Identifier(PG_TABLE)))
            
            row = cur.fetchone()
            stats['total_documents'] = row[0]
            stats['total_chunks'] = row[1]
            stats['avg_chunk_size'] = int(row[2]) if row[2] else 0
            
            # Document types
            cur.execute(sql.SQL("""
                SELECT file_type, COUNT(DISTINCT file_path) as count
                FROM {}
                GROUP BY file_type
                ORDER BY count DESC;
            """).format(sql.Identifier(PG_TABLE)))
            
            stats['file_types'] = {row[0]: row[1] for row in cur.fetchall()}
            
            # Sample documents - Fixed query
            cur.execute(sql.SQL("""
                SELECT file_name, MAX(created_at) as latest
                FROM {}
                GROUP BY file_name
                ORDER BY latest DESC
                LIMIT 10;
            """).format(sql.Identifier(PG_TABLE)))
            
            stats['sample_documents'] = [row[0] for row in cur.fetchall()]
        
        conn.close()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}


def search_similar_chunks(query_embedding: List[float], top_k: int = 10) -> List[Dict]:
    """Search for similar chunks with detailed results."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, database=PG_DATABASE,
            user=PG_USER, password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                SELECT 
                    file_name, 
                    file_type,
                    content_preview,
                    1 - (embedding <=> %s::vector) as similarity
                FROM {}
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """).format(sql.Identifier(PG_TABLE)),
            (query_embedding, query_embedding, top_k))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'file_name': row[0],
                    'file_type': row[1],
                    'preview': row[2][:100] if row[2] else '',
                    'similarity': float(row[3])
                })
        
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return []


def generate_test_queries_from_documents() -> List[Dict]:
    """Generate test queries based on actual document content."""
    logger.info("Generating test queries from your documents...")
    
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, database=PG_DATABASE,
            user=PG_USER, password=PG_PASSWORD
        )
        
        test_queries = []
        
        with conn.cursor() as cur:
            # Get sample content from different document types
            cur.execute(sql.SQL("""
                SELECT DISTINCT ON (file_type)
                    file_type,
                    content_preview,
                    file_name
                FROM {}
                WHERE content_preview IS NOT NULL
                ORDER BY file_type, RANDOM()
                LIMIT 5;
            """).format(sql.Identifier(PG_TABLE)))
            
            for row in cur.fetchall():
                file_type, preview, file_name = row
                
                # Extract first few words as query
                words = preview.split()[:5]
                query = ' '.join(words)
                
                if len(query) > 10:  # Only use if meaningful
                    test_queries.append({
                        'query': query,
                        'expected_types': [file_type],
                        'source_file': file_name,
                        'min_results': 1
                    })
        
        conn.close()
        
        logger.info(f"Generated {len(test_queries)} test queries from your documents")
        return test_queries
        
    except Exception as e:
        logger.error(f"Error generating test queries: {e}")
        return []


def evaluate_retrieval(test_cases: List[Dict], show_details: bool = True) -> Dict:
    """
    Evaluate retrieval quality on test queries with detailed diagnostics.
    
    Metrics:
    - Hit Rate: % of queries that retrieve at least one relevant document
    - MRR (Mean Reciprocal Rank): Average of 1/rank of first relevant result
    - Average Similarity: Mean similarity score of top results
    """
    logger.info("=" * 70)
    logger.info("RAG EVALUATION - DETAILED DIAGNOSTICS")
    logger.info("=" * 70)
    
    # First, show database statistics
    stats = get_database_stats()
    
    if stats:
        logger.info("\nDatabase Statistics:")
        logger.info(f"  Total Documents: {stats.get('total_documents', 0)}")
        logger.info(f"  Total Chunks: {stats.get('total_chunks', 0)}")
        logger.info(f"  Avg Chunk Size: {stats.get('avg_chunk_size', 0)} characters")
        
        if stats.get('file_types'):
            logger.info(f"\n  File Types:")
            for ftype, count in stats['file_types'].items():
                logger.info(f"    - {ftype}: {count} documents")
        
        if stats.get('sample_documents'):
            logger.info(f"\n  Sample Documents:")
            for doc in stats['sample_documents'][:5]:
                logger.info(f"    - {doc}")
    
    if not test_cases:
        logger.warning("\nNo test queries available!")
        logger.info("Generating queries from your documents...")
        test_cases = generate_test_queries_from_documents()
        
        if not test_cases:
            logger.error("Could not generate test queries")
            return {}
    
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING EVALUATION TESTS")
    logger.info("=" * 70)
    
    hits = 0
    reciprocal_ranks = []
    similarities = []
    failed_queries = []
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        expected_types = test["expected_types"]
        
        logger.info(f"\n[Test {i}/{len(test_cases)}] Query: '{query}'")
        if test.get('source_file'):
            logger.info(f"  Source: {test['source_file']}")
        
        # Generate embedding
        embedding = generate_embedding(query)
        if not embedding:
            logger.error("  X Failed to generate embedding")
            failed_queries.append((query, "Embedding generation failed"))
            continue
        
        # Search
        results = search_similar_chunks(embedding, top_k=10)
        
        if not results:
            logger.warning("  X No results found")
            failed_queries.append((query, "No results returned"))
            continue
        
        # Check if any result matches expected type
        found_relevant = False
        relevant_rank = None
        
        for rank, result in enumerate(results, 1):
            similarities.append(result['similarity'])
            
            if result['file_type'] in expected_types and not found_relevant:
                found_relevant = True
                relevant_rank = rank
                hits += 1
                logger.info(f"  OK Found relevant result at rank {rank}: {result['file_name']}")
                logger.info(f"     Similarity: {result['similarity']:.3f}")
                if show_details and result['preview']:
                    logger.info(f"     Preview: {result['preview']}")
                break
        
        if found_relevant and relevant_rank:
            reciprocal_ranks.append(1.0 / relevant_rank)
        else:
            logger.warning(f"  X No relevant results found in top 10")
            failed_queries.append((query, "No relevant results"))
        
        # Show top 3 results
        if show_details:
            logger.info("  Top 3 results:")
            for j, result in enumerate(results[:3], 1):
                marker = "  [MATCH]" if result['file_type'] in expected_types else ""
                logger.info(f"    {j}. {result['file_name']} ({result['file_type']}) - {result['similarity']:.3f}{marker}")
                if result['preview']:
                    logger.info(f"       Preview: {result['preview']}")
    
    # Calculate metrics
    hit_rate = (hits / len(test_cases)) * 100 if test_cases else 0
    mrr = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0
    avg_similarity = statistics.mean(similarities) if similarities else 0
    
    logger.info("\n" + "=" * 70)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 70)
    logger.info(f"Hit Rate:          {hit_rate:.1f}% ({hits}/{len(test_cases)} queries)")
    logger.info(f"MRR:               {mrr:.3f}")
    logger.info(f"Avg Similarity:    {avg_similarity:.3f}")
    logger.info("=" * 70)
    
    # Performance interpretation with specific recommendations
    if hit_rate >= 80:
        logger.info("\nOK Excellent retrieval performance!")
    elif hit_rate >= 60:
        logger.info("\n~ Good retrieval, but room for improvement")
    else:
        logger.info("\nX Poor retrieval - action required")
    
    # Detailed recommendations based on results
    logger.info("\n" + "=" * 70)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 70)
    
    if hit_rate < 60:
        logger.info("\n1. IMMEDIATE ACTIONS:")
        logger.info("   - Your test queries may not match your document content")
        logger.info("   - Try using actual phrases from your documents")
        logger.info("   - Use the generated queries based on your documents")
        
        if avg_similarity < 0.5:
            logger.info("\n2. LOW SIMILARITY SCORES:")
            logger.info("   - Re-index with better chunk size (current default: 512)")
            logger.info("   - Ensure Ollama embedding model is correct (nomic-embed-text)")
            logger.info("   - Check if documents have meaningful content")
    
    if stats.get('total_documents', 0) < 10:
        logger.info("\n3. LOW DOCUMENT COUNT:")
        logger.info("   - Index more documents for better coverage")
        logger.info("   - Current: {} documents".format(stats.get('total_documents', 0)))
        logger.info("   - Recommended: 20+ documents for meaningful evaluation")
    
    if failed_queries:
        logger.info(f"\n4. FAILED QUERIES ({len(failed_queries)}):")
        for query, reason in failed_queries[:5]:
            logger.info(f"   - '{query[:50]}...': {reason}")
    
    logger.info("\n" + "=" * 70)
    logger.info("NEXT STEPS")
    logger.info("=" * 70)
    logger.info("\n1. Try auto-generated queries:")
    logger.info("   python evaluate_rag.py --auto-queries")
    logger.info("\n2. View indexed documents:")
    logger.info("   python check_ingested_documents.py")
    logger.info("\n3. Re-index with optimized settings:")
    logger.info("   python main.py -> Option 2 (Indexeer documenten)")
    logger.info("\n4. Test specific documents:")
    logger.info("   Create custom queries based on actual document content")
    
    return {
        'hit_rate': hit_rate,
        'mrr': mrr,
        'avg_similarity': avg_similarity,
        'total_tests': len(test_cases),
        'hits': hits,
        'failed_queries': len(failed_queries),
        'stats': stats
    }


def main():
    """Run evaluation with auto-detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate RAG performance')
    parser.add_argument('--auto-queries', action='store_true',
                       help='Generate test queries from indexed documents')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal output without details')
    
    args = parser.parse_args()
    
    try:
        if args.auto_queries:
            test_queries = generate_test_queries_from_documents()
        else:
            # Check if database has documents
            stats = get_database_stats()
            
            if stats.get('total_documents', 0) == 0:
                logger.error("\nNo documents in database!")
                logger.info("Please index documents first:")
                logger.info("  python main.py -> Option 2")
                return
            
            # Use auto-generated queries if available
            logger.info("\nNo predefined test queries match your documents.")
            logger.info("Generating custom queries from your indexed content...\n")
            test_queries = generate_test_queries_from_documents()
        
        results = evaluate_retrieval(test_queries, show_details=not args.minimal)
        
    except KeyboardInterrupt:
        logger.info("\nEvaluation interrupted")
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
