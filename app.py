# -*- coding: utf-8 -*-
"""
WhereSpace - Unified Application
Main entry point for the integrated web application
"""
import logging
from flask import Flask, render_template, jsonify, request, Response
import json
from config import get_config
from services import DatabaseService, LLMService, ModelService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
db_service = None
llm_service = None
model_service = None

def create_app(config_name='development'):
    """Application factory pattern"""
    global db_service, llm_service, model_service
    
    # Get configuration
    config = get_config(config_name)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize services
    try:
        db_service = DatabaseService(config)
        llm_service = LLMService(config)
        model_service = ModelService(config)
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
    
    # Register blueprints (we'll create these)
    # from routes import chat_bp, documents_bp, models_bp, system_bp
    # app.register_blueprint(chat_bp, url_prefix='/api/chat')
    # app.register_blueprint(documents_bp, url_prefix='/api/documents')
    # app.register_blueprint(models_bp, url_prefix='/api/models')
    # app.register_blueprint(system_bp, url_prefix='/api/system')
    
    # ============================================================================
    # Main Routes (using new unified layout)
    # ============================================================================
    
    @app.route('/')
    def index():
        """Dashboard homepage - redirect to ingest"""
        from flask import redirect, url_for
        return redirect(url_for('ingest'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/chat')
    def chat():
        """Chat page (for dedicated chat view)"""
        from flask import redirect, url_for
        # Redirect to dashboard - chat.html doesn't exist
        # Use the chat panel (topbar button) for chat functionality
        return redirect(url_for('index'))
    
    @app.route('/architecture')
    def architecture():
        """System architecture page"""
        return render_template('architecture.html')
    
    @app.route('/models')
    def models():
        """Model management page"""
        return render_template('models.html')
    
    @app.route('/evaluation')
    def evaluation():
        """RAG evaluation page"""
        return render_template('evaluation.html')
    
    @app.route('/settings')
    def settings():
        """Settings page"""
        return render_template('settings.html')
    
    @app.route('/ingest')
    def ingest():
        """Document ingestion page"""
        return render_template('ingest.html')
    
    @app.route('/storage')
    def storage():
        """Storage analysis page"""
        return render_template('storage.html')
    
    # ============================================================================
    # API Routes (using services)
    # ============================================================================
    
    @app.route('/api/status')
    def api_status():
        """System status endpoint"""
        docs_exist, doc_count = db_service.check_documents_exist()
        ollama_available = llm_service.check_ollama_available()
        current_model = model_service.get_current_model()
        
        return jsonify({
            'success': True,
            'document_count': doc_count,
            'documents_exist': docs_exist,
            'current_model': current_model,
            'ollama_available': ollama_available
        })
    
    @app.route('/api/models')
    def api_models():
        """Get available models"""
        models = llm_service.get_available_models()
        current_model = model_service.get_current_model()
        
        # If no models found, return defaults
        if not models:
            models = [
                {'id': 'llama3.1', 'name': 'Llama 3.1', 'full_name': 'llama3.1:latest'},
                {'id': 'mistral', 'name': 'Mistral', 'full_name': 'mistral:latest'},
            ]
        
        return jsonify({
            'success': True,
            'models': models,
            'current_model': current_model,
            'count': len(models)
        })
    
    @app.route('/api/set_model', methods=['POST'])
    def api_set_model():
        """Set the active LLM model"""
        data = request.json
        model_id = data.get('model', '').strip()
        
        if not model_id:
            return jsonify({'error': 'No model specified'}), 400
        
        success = model_service.set_current_model(model_id)
        
        if success:
            return jsonify({
                'success': True,
                'model': model_id,
                'message': f'Model switched to {model_id}'
            })
        else:
            return jsonify({'error': 'Failed to set model'}), 500
    
    @app.route('/api/query_stream', methods=['POST'])
    def api_query_stream():
        """Handle streaming RAG query"""
        try:
            data = request.json
            user_query = data.get('query', '').strip()
            
            if not user_query:
                return jsonify({'error': 'Empty query'}), 400
            
            # Check documents exist
            docs_exist, doc_count = db_service.check_documents_exist()
            if not docs_exist:
                return jsonify({'error': 'No documents found in database'}), 404
            
            # Generate embedding
            query_embedding = llm_service.generate_embedding(user_query)
            if not query_embedding:
                return jsonify({'error': 'Failed to generate query embedding'}), 500
            
            # Search for similar chunks
            similar_chunks = db_service.search_similar_chunks(query_embedding, top_k=5)
            
            if not similar_chunks:
                def no_results():
                    yield f"data: {json.dumps({'type': 'response', 'content': 'Geen relevante informatie gevonden.'})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return Response(no_results(), mimetype='text/event-stream')
            
            # Generate response
            def generate():
                # Send sources
                sources = [
                    {
                        'file': chunk['file_name'],
                        'chunk': chunk['chunk_index'],
                        'similarity': round(chunk['similarity'] * 100, 1),
                        'preview': chunk['preview']
                    }
                    for chunk in similar_chunks
                ]
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                
                # Stream response
                current_model = model_service.get_current_model()
                for chunk in llm_service.generate_rag_response_stream(user_query, similar_chunks, current_model):
                    yield f"data: {json.dumps({'type': 'response', 'content': chunk})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
            
        except Exception as e:
            logger.error(f"Error in query_stream: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/query_direct_stream', methods=['POST'])
    def api_query_direct_stream():
        """Query Ollama directly without RAG"""
        try:
            data = request.json
            user_query = data.get('query', '').strip()
            
            if not user_query:
                return jsonify({'error': 'Empty query'}), 400
            
            def generate():
                current_model = model_service.get_current_model()
                for chunk in llm_service.generate_response_stream(user_query, current_model):
                    yield f"data: {json.dumps({'type': 'response', 'content': chunk})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
            
        except Exception as e:
            logger.error(f"Error in query_direct_stream: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/list_documents', methods=['GET'])
    def api_list_documents():
        """Get list of all ingested documents"""
        documents = db_service.list_documents()
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)
        })
    
    @app.route('/api/flush_documents', methods=['POST'])
    def api_flush_documents():
        """Delete all ingested documents"""
        success, deleted_count = db_service.delete_all_documents()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'{deleted_count} chunks verwijderd',
                'deleted_count': deleted_count
            })
        else:
            return jsonify({'error': 'Failed to delete documents'}), 500
    
    @app.route('/api/scan_directory', methods=['POST'])
    def api_scan_directory():
        """Scan a directory for documents"""
        try:
            data = request.json
            directory_path = data.get('path', '').strip()
            
            if not directory_path:
                return jsonify({'error': 'No directory path specified'}), 400
            
            from pathlib import Path
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                return jsonify({'error': 'Invalid directory path'}), 400
            
            # Scan directory for documents
            from services.document_service import DocumentService
            doc_service = DocumentService(config)
            
            documents = doc_service.scan_directory(path)
            
            return jsonify({
                'success': True,
                'documents': documents,
                'count': len(documents)
            })
            
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ingest_documents', methods=['POST'])
    def api_ingest_documents():
        """Ingest documents into the database with streaming progress and evaluation"""
        try:
            data = request.json
            file_paths = data.get('files', [])
            
            if not file_paths:
                return jsonify({'error': 'No files specified'}), 400
            
            from pathlib import Path
            from services.document_service import DocumentService
            from services.evaluation_service import EvaluationService
            
            doc_service = DocumentService(config)
            eval_service = EvaluationService(config)
            
            # Use server-sent events for progress updates
            def generate_progress():
                paths = [Path(f) for f in file_paths]
                total = len(paths)
                ingested_count = 0
                failed_count = 0
                
                for i, file_path in enumerate(paths, 1):
                    # Send progress update
                    yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'processing'})}\n\n"
                    
                    try:
                        # Extract text
                        text = doc_service.extract_text(file_path)
                        
                        # More lenient content check (was 50, now 20)
                        if not text:
                            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'skipped', 'reason': 'No text extracted'})}\n\n"
                            failed_count += 1
                            continue
                        
                        # Check for actual content (not just whitespace)
                        text_stripped = text.strip()
                        if len(text_stripped) < 20:
                            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'skipped', 'reason': f'Insufficient content ({len(text_stripped)} chars)'})}\n\n"
                            failed_count += 1
                            continue
                        
                        logger.info(f"Extracted {len(text_stripped)} chars from {file_path.name}")
                        
                        # Chunk text
                        chunks = doc_service.chunk_text(text)
                        yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'chunking', 'chunks': len(chunks)})}\n\n"
                        
                        # Generate embeddings
                        yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'embedding'})}\n\n"
                        embeddings = []
                        for chunk in chunks:
                            embedding = llm_service.generate_embedding(chunk)
                            if not embedding:
                                break
                            embeddings.append(embedding)
                        
                        if len(embeddings) != len(chunks):
                            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'failed', 'reason': 'Embedding generation failed'})}\n\n"
                            failed_count += 1
                            continue
                        
                        # Store in database
                        yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'storing'})}\n\n"
                        file_stat = file_path.stat()
                        success = db_service.ingest_document(
                            file_path=file_path,
                            chunks=chunks,
                            embeddings=embeddings,
                            modified_time=file_stat.st_mtime
                        )
                        
                        if success:
                            ingested_count += 1
                            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'success'})}\n\n"
                        else:
                            failed_count += 1
                            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'failed', 'reason': 'Database error'})}\n\n"
                            
                    except Exception as e:
                        failed_count += 1
                        yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'file': file_path.name, 'status': 'error', 'reason': str(e)})}\n\n"
                
                # Run RAG evaluation after ingestion
                if ingested_count > 0:
                    yield f"data: {json.dumps({'type': 'evaluating', 'message': 'Running RAG evaluation...'})}\n\n"
                    
                    try:
                        # Give database a moment to commit
                        import time
                        time.sleep(0.5)
                        
                        evaluation = eval_service.evaluate_retrieval(
                            db_service=db_service,
                            llm_service=llm_service,
                            top_k=5
                        )
                        
                        if evaluation and 'hit_rate' in evaluation:
                            assessment = eval_service.get_performance_assessment(evaluation)
                            
                            # Send evaluation results
                            yield f"data: {json.dumps({'type': 'evaluation', 'results': evaluation, 'assessment': assessment})}\n\n"
                        else:
                            logger.warning("Evaluation returned no results - skipping")
                            yield f"data: {json.dumps({'type': 'evaluation_error', 'error': 'No test queries could be generated'})}\n\n"
                        
                    except Exception as e:
                        logger.error(f"Evaluation error: {e}", exc_info=True)
                        yield f"data: {json.dumps({'type': 'evaluation_error', 'error': str(e)})}\n\n"
                
                # Send completion
                yield f"data: {json.dumps({'type': 'done', 'ingested': ingested_count, 'failed': failed_count, 'total': total})}\n\n"
            
            return Response(generate_progress(), mimetype='text/event-stream')
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analyze_storage', methods=['POST'])
    def api_analyze_storage():
        """Analyze storage in a directory"""
        try:
            data = request.json
            directory_path = data.get('path', '').strip()
            
            if not directory_path:
                return jsonify({'error': 'No directory path specified'}), 400
            
            from pathlib import Path
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                return jsonify({'error': 'Invalid directory path'}), 400
            
            from services.document_service import DocumentService
            doc_service = DocumentService(config)
            
            analysis = doc_service.analyze_storage(path)
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error analyzing storage: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================================================
    # Error Handlers
    # ============================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('dashboard.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        logger.error(f'Server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    # ============================================================================
    # CLI Commands (optional)
    # ============================================================================
    
    @app.cli.command()
    def test():
        """Run tests"""
        logger.info('Running tests...')
        # TODO: Implement test runner
    
    @app.cli.command()
    def init_db():
        """Initialize database"""
        logger.info('Initializing database...')
        # TODO: Implement with DatabaseService
    
    return app


def main():
    """Main entry point"""
    # Create app
    app = create_app('development')
    
    # Get config
    config = get_config('development')
    
    logger.info("=" * 60)
    logger.info("WhereSpace - Unified Application")
    logger.info("=" * 60)
    logger.info(f"Starting server on http://{config.HOST}:{config.PORT}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Run app
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


if __name__ == '__main__':
    main()
