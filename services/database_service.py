# -*- coding: utf-8 -*-
"""
Database Service
Handles all PostgreSQL/pgvector operations
"""
import logging
import psycopg2
from psycopg2 import pool, sql
from typing import List, Dict, Optional, Tuple
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, config=None):
        """Initialize database service with connection pool"""
        if config is None:
            config = get_config()
        
        self.config = config
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.config.PG_MIN_CONNECTIONS,
                self.config.PG_MAX_CONNECTIONS,
                host=self.config.PG_HOST,
                port=self.config.PG_PORT,
                database=self.config.PG_DATABASE,
                user=self.config.PG_USER,
                password=self.config.PG_PASSWORD
            )
            logger.info(f"Database connection pool initialized ({self.config.PG_MIN_CONNECTIONS}-{self.config.PG_MAX_CONNECTIONS} connections)")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self.connection_pool is None:
            self._initialize_pool()
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def check_documents_exist(self) -> Tuple[bool, int]:
        """Check if any documents are ingested in the database"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, [self.config.PG_TABLE])
                
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    return False, 0
                
                # Count distinct documents
                cur.execute(sql.SQL("""
                    SELECT COUNT(DISTINCT file_path) FROM {};
                """).format(sql.Identifier(self.config.PG_TABLE)))
                
                count = cur.fetchone()[0]
                return count > 0, count
                
        except Exception as e:
            logger.error(f"Error checking documents: {e}")
            return False, 0
        finally:
            if conn:
                self.return_connection(conn)
    
    def list_documents(self) -> List[Dict]:
        """Get list of all ingested documents with metadata"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    SELECT DISTINCT ON (file_path)
                        file_name,
                        file_path,
                        file_type,
                        file_size,
                        created_at,
                        (SELECT COUNT(*) FROM {} d2 WHERE d2.file_path = d1.file_path) as chunk_count
                    FROM {} d1
                    ORDER BY file_path, created_at DESC;
                """).format(
                    sql.Identifier(self.config.PG_TABLE),
                    sql.Identifier(self.config.PG_TABLE)
                ))
                
                documents = []
                for row in cur.fetchall():
                    # Format file size
                    file_size = row[3]
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.2f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.2f} MB"
                    
                    documents.append({
                        'file_name': row[0],
                        'file_path': row[1],
                        'file_type': row[2],
                        'file_size': file_size,
                        'file_size_formatted': size_str,
                        'chunk_count': row[5],
                        'ingested_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
                    })
                
                # Sort by file name
                documents.sort(key=lambda x: x['file_name'].lower())
                return documents
                
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        top_k: int = 10, 
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """Search for similar document chunks using vector similarity"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    SELECT 
                        file_name,
                        file_path,
                        chunk_index,
                        chunk_content,
                        content_preview,
                        file_type,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM {}
                    WHERE (1 - (embedding <=> %s::vector)) >= %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """).format(sql.Identifier(self.config.PG_TABLE)),
                [query_embedding, query_embedding, min_similarity, query_embedding, top_k])
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        'file_name': row[0],
                        'file_path': row[1],
                        'chunk_index': row[2],
                        'content': row[3],
                        'preview': row[4],
                        'file_type': row[5],
                        'similarity': float(row[6])
                    })
                
                logger.info(f"Retrieved {len(results)} chunks with similarity >= {min_similarity}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def delete_all_documents(self) -> Tuple[bool, int]:
        """Delete all documents from the database"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(sql.SQL("DELETE FROM {};").format(sql.Identifier(self.config.PG_TABLE)))
                deleted_count = cur.rowcount
                conn.commit()
            
            logger.info(f"Deleted {deleted_count} document chunks")
            return True, deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            if conn:
                conn.rollback()
            return False, 0
        finally:
            if conn:
                self.return_connection(conn)
    
    def ingest_document(
        self,
        file_path,
        chunks: List[str],
        embeddings: List[List[float]],
        modified_time: float
    ) -> bool:
        """Ingest document chunks with embeddings into database
        
        Args:
            file_path: Path to the document
            chunks: List of text chunks
            embeddings: List of embedding vectors
            modified_time: File modification timestamp
            
        Returns:
            True if successful, False otherwise
        """
        conn = None
        try:
            conn = self.get_connection()
            
            # Get file stats
            import os
            file_size = os.path.getsize(file_path)
            
            with conn.cursor() as cur:
                # Delete old chunks for this file
                cur.execute(sql.SQL("DELETE FROM {} WHERE file_path = %s;").format(
                    sql.Identifier(self.config.PG_TABLE)
                ), (str(file_path),))
                
                # Insert new chunks
                for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    cur.execute(sql.SQL("""
                        INSERT INTO {} 
                        (file_path, chunk_index, file_name, file_type, content_preview, 
                         chunk_content, file_size, modified_time, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """).format(sql.Identifier(self.config.PG_TABLE)), (
                        str(file_path),
                        chunk_idx,
                        file_path.name,
                        file_path.suffix.lstrip('.'),
                        chunk[:200],  # Preview
                        chunk,
                        file_size,
                        modified_time,
                        embedding
                    ))
            
            conn.commit()
            logger.info(f"Ingested {len(chunks)} chunks for {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")
    
    def get_document_chunks(self, file_path: str, limit: int = 5) -> List[Dict]:
        """Get chunks for a specific document
        
        Args:
            file_path: Path to the document
            limit: Maximum number of chunks to return
            
        Returns:
            List of chunk dictionaries
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    SELECT chunk_index, chunk_content, content_preview
                    FROM {}
                    WHERE file_path = %s
                    ORDER BY chunk_index
                    LIMIT %s;
                """).format(sql.Identifier(self.config.PG_TABLE)),
                [file_path, limit])
                
                chunks = []
                for row in cur.fetchall():
                    chunks.append({
                        'chunk_index': row[0],
                        'content': row[1],
                        'preview': row[2]
                    })
                
                return chunks
                
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
