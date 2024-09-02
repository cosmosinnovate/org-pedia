import os
from flask import Flask, request, Response, json
import ollama
from anthropic import AnthropicBedrock
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

client = AnthropicBedrock(
    aws_secret_key=os.environ.get("AWS_SECRET_KEY"),
    aws_access_key=os.environ.get("AWS_ACCESS_KEY"),
    aws_region="us-east-1"
)

@app.route('/ollama-chat', methods=['POST'])
def ollama_chat():
    try:
        messages = request.json.get("messages")

        if not isinstance(messages, list):
            messages = [messages]

        def generate():
            response = ollama.chat(
                model="codellama",
                messages=messages,
                options={
                    "temperature": 0.9,
                    "max_token": 2000
                },
                stream=True
            )

            for part in response:
                content = part.get('message', {}).get('content', '')
                yield f"data: {json.dumps({'content': content})}\n\n"
                
                if part.get('done'):
                    break

            # Signal the end of the stream
            yield "data: [DONE]\n\n"

        return Response(generate(), headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        })

    except Exception as e:
        print(f"Error processing request: {e}")
        return {"error": "Error processing request"}, 500


@app.route('/bedrock-chat', methods=['POST'])
def bedrock_chat():
    try:
        messages = request.json.get('messages', [])

        # Ensure messages is a list
        if not isinstance(messages, list):
            messages = [messages]

        # Validate each message
        for message in messages:
            if 'role' not in message or 'content' not in message or not message['content'].strip():
                return {'error': 'Each message must contain "role" and non-empty "content"'}, 400

        def generate():
            response = client.messages.create(
                model='anthropic.claude-3-sonnet-20240229-v1:0',
                messages=messages,
                max_tokens=4000,
                stream=True
            )

            for event in response:
                # Print the type and content of the event for debugging
                print(f"Received event: {event}")
                
                # Assuming event is an instance of a class
                if hasattr(event, 'type') and event.type == 'content_block_delta':
                    delta = getattr(event, 'delta', {})
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        content = getattr(delta, 'text', '')
                        yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"

        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive'
        }
        return Response(generate(), headers=headers)

    except Exception as e:
        print(f"Error processing Bedrock chat request: {e}")
        return {'error': 'Error processing Bedrock chat request'}, 500


@app.route('/', methods=["GET"])
def health():
    return {"message": "OK"}

if __name__ == "__main__":
    app.run(port=8000)