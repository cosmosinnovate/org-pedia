from flask import Blueprint, jsonify, request, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import logging

from app.schemas.schemas import ChatHistorySchema
from app.services.user_service import UserService as user_service
from app.services.chat_history_service import ChatHistoryService as chat_service
from app.llms.llm import LLMService as llm_service

logger = logging.getLogger(__name__)
chat_history_bp = Blueprint('chat', __name__)
chat_schema = ChatHistorySchema()

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
def get_current_user_chats():
    try:
        current_user = get_jwt_identity()
        messages = chat_service.get_user_chat_by_id(current_user)
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
    
@chat_history_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    try:        
        data = request.get_json()
        messages = data.get("messages", [])
        current_user = get_jwt_identity()
        
        if not isinstance(messages, list):
            messages = [messages]
            
        # Ensure messages are in the correct format
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                return jsonify({"error": "Invalid message format. Each message must have 'role' and 'content'"}), 400
        
        app = current_app._get_current_object()
        
        def generate():
            try:
                response = llm_service.generate_chat("ollama", "llama2", messages)
                content_buffer = ""
                
                for part in response:
                    content = part.get("message", {}).get("content", "")
                    if content:
                        content_buffer += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    if part.get("done"):
                        with app.app_context():
                            messages.append({"role": "assistant", "content": content_buffer})
                            chat_service.create_chat_message(
                                user_id=current_user, 
                                title="Chat with Llama", 
                                messages=messages
                            )
                        break
                
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error in generate function: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({"error": "Error processing request"}), 500