from flask import Blueprint, jsonify, request, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
import json
import logging
from PyPDF2 import PdfReader # type: ignore
import os

from app.schemas.schemas import ChatHistorySchema
from app.services.user_service import UserService as user_service
from app.services.chat_history_service import ChatHistoryService as chat_service
from app.llms.llm import LLMService as llm_service
from app.factory.elasticsearch_factory import ElasticsearchClientFactory
from app.services.elasticsearch_service import ElasticsearchService as es_service

logger = logging.getLogger(__name__)
chat_history_bp = Blueprint('chat', __name__)
chat_schema = ChatHistorySchema()

es = ElasticsearchClientFactory.create_client()

@chat_history_bp.route("/start-chat", methods=["POST"])
@jwt_required()
def create_chat():
    try:
        data = request.get_json()
        new_chat: ChatHistorySchema = chat_schema.load(data)
        current_user = get_jwt_identity()         
        chat_service.create_chat_message(user_id=current_user, title=new_chat.title, messages=new_chat.messages)
        return jsonify({"message": "Chat created successfully"}), 201
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({"message": "An error occurred during chat creation"}), 500
    
@chat_history_bp.route("", methods=["GET"])
@jwt_required()
def get_user_chats():
    try:
        current_user = get_jwt_identity()
        messages = chat_service.get_user_chats_by_id(current_user)
        logger.info(f"Fetching chats for user: {current_user}, messages: {messages}")   
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error fetching chats: {str(e)}")
        return jsonify({"error": f"Something went wrong {e}"})
    
@chat_history_bp.route("/<string:chat_id>", methods=["GET"])
@jwt_required()
def get_chat(chat_id:str):
    try: 
        current_user_id = get_jwt_identity()
        chat = chat_service.get_chat_history_by_id(chat_id, current_user_id)
        if not chat:
            return jsonify({'error': 'Chat not found or not authorized'}), 404
        
        return jsonify(chat['messages']), 200
        
    except Exception as e:
        logger.error(f"Error in get_chat: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching the chat"
        }), 500

@chat_history_bp.route("/<string:chat_id>", methods=["PATCH"])
@jwt_required()
def update_chat(chat_id:str):
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        chat = chat_service.get_chat_history_by_id(chat_id=chat_id, user_id=current_user)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        
        update_data = {}
        if "title" in data:
            update_data["title"] = data["title"]
        
        if "messages" in data:
            messages = data.get("messages", [])
            if not isinstance(messages, list):
                messages = [messages]
            update_data["messages"] = messages
        
        updated_chat = chat_service.update_chat_repo(chat_id, current_user, update_data=update_data)
        if updated_chat:
            return jsonify(updated_chat), 200
        else:
            return jsonify({"error": "Chat not found or update failed"}), 404
    except Exception as e:
        logger.error(f"Error in update_chat route: {str(e)}")
        return jsonify({"error": "An error occurred while updating the chat"}), 500
    
# New implementation
@chat_history_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        current_user = get_jwt_identity()

        if not messages or not isinstance(messages, list):
            return jsonify({"error": "Invalid messages format"}), 400

        user_message = messages.pop() if messages else None
        logger.info(f"User message: {user_message}")   
        
        if not user_message or user_message.get('role') != 'user':
            return jsonify({"error": "Last message must be a user message"}), 400
            
        user_question = user_message['content'].strip()
        
        # Generate embedding for semantic search
        query_embedding = llm_service.get_embedding(user_question)
        if not query_embedding:
            return jsonify({"error": "Query processing failed"}), 500

        # Check index status
        index_name = os.getenv("ELASTICSEARCH_INDEX", "org_pedia")
        if not es.indices.exists(index=index_name):
            logger.error(f"Index {index_name} does not exist")
            return jsonify({"error": "No documents have been indexed yet"}), 404

        # Get index stats
        try:
            stats = es.count(index=index_name)['count']
            doc_count = stats['indices'][index_name]['total']['docs']['count']
            if doc_count == 0:
                return jsonify({"error": "No documents have been indexed yet"}), 404
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")

        # Retrieve relevant context with multiple attempts
        context_docs = []
        min_scores = [0.7, 0.5, 0.3]  # Try progressively lower thresholds
        
        for min_score in min_scores:
            context_docs = es_service.search_documents(es, query_embedding, size=5, min_score=min_score)
            if context_docs:
                logger.info(f"Found {len(context_docs)} documents with min_score {min_score}")
                break
            else:
                logger.info(f"No documents found with min_score {min_score}, trying lower threshold")
        
        # Format context for the LLM
        if context_docs:
            # Format each context document with a numbered section and clear headers
            formatted_contexts = []
            for i, doc in enumerate(context_docs, 1):
                # Add clear section breaks and headers
                formatted_contexts.append(
                    f"=== DOCUMENT {i} START ===\n"
                    f"{doc}\n"
                    f"=== DOCUMENT {i} END ===\n"
                )
            context_text = "\n".join(formatted_contexts)
            
            logger.info(f"Found {len(context_docs)} relevant context documents")
            
            # Create a system message that establishes the context
            system_message = {
                "role": "system",
                "content": (
                    "You are an AI assistant providing information about Synasespend AI. "
                    "You have access to official documentation about this company. "
                    "Do not confuse this with any other companies. "
                    "Only use information from the provided documents. "
                    "Do not add any external knowledge or make assumptions."
                )
            }
            
            # Add the ability for the system to refer to the context
            context_text = f"{system_message['content']}\n\n{context_text}"
            # Add the ability to use different LLM models for different contexts
            # For instance when a user asks about a specific product or service of the company and it does not exist in the general documentation
            # then the system should be able to look for another agents that are specialized in that product or service.
            # If not it should just use the general know
            
            # Create a user message with the context and question
            context_message = {
                "role": "user",
                "content": (
                    f"Here are the official documents about Synasespend AI:\n\n"
                    f"{context_text}\n\n"
                    f"Based only on these documents, please answer: {user_question}"
                )
            }
            
            # Create the messages array for the LLM
            messages_for_llm = [
                system_message,
                context_message
            ]
            
            logger.info("Prepared messages for LLM:")
            logger.info(f"1. System message: {system_message['content'][:100]}...")
            logger.info(f"2. Context length: {len(context_text)} characters")
            logger.info(f"3. User question: {user_question}")
        else:
            logger.info("No relevant context found")
            messages_for_llm = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant providing information about Synasespend AI. "
                        "You have access to official documentation about this company. "
                        "Do not confuse this with any other companies. "
                        "Only use information from the provided documents. "
                        "Do not add any external knowledge or make assumptions."
                    )
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ]
            
            logger.info("Prepared messages for LLM:")
            logger.info(f"1. System message: {messages_for_llm[0]['content'][:100]}...")
            logger.info(f"2. User question: {user_question}")

        messages_processing = messages_for_llm

        app = current_app._get_current_object()

        def generate():
            try:
                response = llm_service.generate_chat(
                    model_provider="ollama",
                    model_name="llama3.2",
                    messages=messages_processing
                )
                
                full_response = ""
                for chunk in response:
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    if chunk.get("done"):
                        with app.app_context():
                            messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "context": context_docs  # Store references
                            })
                            chat_service.create_chat_message(
                                user_id=current_user,
                                title=f"Chat: {user_question[:50]}",
                                messages=messages
                            )
                        break

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Generation error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable buffering for nginx
            }
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat processing failed"}), 500
    

@chat_history_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # First check if it's a text file
        if file.mimetype.startswith('text/'):
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                # Try common fallback encodings
                try:
                    content = file.read().decode('latin-1')
                except Exception as e:
                    return jsonify({"error": f"Text decoding failed: {str(e)}"}), 400
        elif file.mimetype == 'application/pdf':
            # Handle PDF files
            pdf = PdfReader(file)
            content = "\n".join([page.extract_text() for page in pdf.pages])
        else:
            return jsonify({"error": f"Unsupported file type: {file.mimetype}"}), 400

        # Clean and validate content
        content = es_service.clean_content(content)
        if not content:
            return jsonify({"error": "Content is empty after cleaning"}), 400
            
        logger.info(f"Cleaned content length: {len(content)}")
        logger.info(f"Content preview: {content[:200]}...")

        # Generate embedding
        embedding = llm_service.get_embedding(content)
        if not embedding:
            return jsonify({"error": "Embedding generation failed"}), 500
        
        logger.info(f"Generated embedding dimensions: {len(embedding)}")

        # Check index status
        index_name = os.getenv("ELASTICSEARCH_INDEX", "documents")
        if es.indices.exists(index=index_name):
            stats = es.count(index=index_name)['count']
            doc_count = stats
            logger.info(f"Current index status: {doc_count} documents")
            
            # Get and verify mapping
            mapping = es.indices.get_mapping(index=index_name)
            logger.info(f"Current mapping: {mapping}")
        else:
            logger.info("Index does not exist, will be created during indexing")

        # Index the document
        try:
            es_service.index_document(es, content, embedding)
            logger.info("Document indexed successfully")
            
            # Verify document was indexed
            stats = es.count(index=index_name)['count']
            new_doc_count = stats
            logger.info(f"New document count: {new_doc_count}")
            
            # Try an immediate search to verify
            test_embedding = llm_service.get_embedding(content[:100])  # Use first 100 chars as test
            if test_embedding:
                test_results = es_service.search_documents(es, test_embedding, size=1, min_score=0.3)
                if test_results:
                    logger.info("Document verified in search results")
                else:
                    logger.warning("Document not found in immediate search test")
            
            return jsonify({
                "message": "File indexed successfully",
                "documentCount": new_doc_count
            }), 200
        except Exception as e:
            logger.error(f"Indexing error: {str(e)}")
            # Try to recreate index
            try:
                if es.indices.exists(index=index_name):
                    es.indices.delete(index=index_name)
                es_service.create_index(es, index_name)
                es_service.index_document(es, content, embedding)
                logger.info("Successfully recreated index and indexed document")
                return jsonify({"message": "File indexed successfully (after index recreation)"}), 200
            except Exception as e2:
                logger.error(f"Index recreation failed: {str(e2)}")
                return jsonify({"error": f"Indexing failed even after recreation: {str(e2)}"}), 500

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": f"File processing failed: {str(e)}"}), 500