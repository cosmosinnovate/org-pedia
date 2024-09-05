import os
from flask import Flask, jsonify, request, Response, json
import ollama
from anthropic import AnthropicBedrock
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from google.auth.transport import requests
from google.oauth2 import id_token
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_migrate import Migrate
from datetime import timedelta
import os

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

os.environ["FLASK_APP"] = "main.py"

CORS(app)  # Enable CORS for all routes
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@localhost/org_pedia"
)

# Initialize JWTManager with the app
jwt = JWTManager(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

client = AnthropicBedrock(
    aws_secret_key=os.environ.get("AWS_SECRET_KEY"),
    aws_access_key=os.environ.get("AWS_ACCESS_KEY"),
    aws_region="us-east-1",
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String)
    display_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    photo_url = db.Column(db.String, nullable=True)
    access_token = db.Column(db.String, nullable=True)

    def __init__(
        self, user_id, display_name=None, email=None, photo_url=None, access_token=None
    ):
        self.user_id = user_id
        self.display_name = display_name
        self.email = email
        self.photo_url = photo_url
        self.access_token = access_token

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user_id == other.user_id
        return NotImplemented

    def to_dict(self):
        """
        Returns a dictionary representation of the User object.

        Returns:
            dict: A dictionary containing user_id, display_name, email,
                photo_url, and access_token.
        """
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "email": self.email,
            "photo_url": self.photo_url,
            "access_token": self.access_token,
        }

    def update_user(user, data):
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    def delete_user(user) -> bool:
        user = User.query.filter_by(user_id=user.user_id).first()
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True


def generate_jwt(user: User) -> str:
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "display_name": user.display_name,
            "email": user.email,
            "photo_url": user.photo_url,
            "user_id": user.user_id,
            "access_token": user.access_token,
            "id": user.id,
        },
        expires_delta=timedelta(hours=45),  # Set token expiration to 45 hours
    )
    return access_token


@app.route("/auth", methods=["POST"])
def authenticate_google():
    data = request.get_json()

    # Check if user already exists
    user = User.query.filter_by(email=data.get("email")).first()
    
    if user:
        # Sign the user in and return the access token
        access_token = generate_jwt(user)
        return jsonify({
            "message": "Signed in successfully",
            "access_token": access_token,
            "user": user.to_dict()  # Convert User object to dict
        }), 200

    # Required fields for user creation
    required_fields = ["user_id", "display_name", "email", "photo_url", "access_token"]

    # Verify that all required fields are provided in the POST request
    if not all(field in data for field in required_fields):
        return jsonify({"message": "All required fields must be provided"}), 400

    try:
        # Extract user data from the POST request
        user_id = data.get("user_id")
        display_name = data.get("display_name")
        email = data.get("email")
        photo_url = data.get("photo_url")
        access_token = data.get("access_token")

        # Verify that all fields have valid values
        if not isinstance(user_id, str) or not user_id:
            return jsonify({"message": "User ID must be a non-empty string"}), 400
        if not isinstance(display_name, str) or not display_name:
            return jsonify({"message": "Display name must be a non-empty string"}), 400
        if not isinstance(email, str) or not email:
            return jsonify({"message": "Email must be a non-empty string"}), 400
        if not isinstance(photo_url, str) or not photo_url:
            return jsonify({"message": "Photo URL must be a non-empty string"}), 400
        if not isinstance(access_token, str) or not access_token:
            return jsonify({"message": "Access token must be a non-empty string"}), 400

        # Create a new user
        user = User(
            user_id=user_id,
            display_name=display_name,
            email=email,
            photo_url=photo_url,
            access_token=access_token,
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "access_token": generate_jwt(user),
        }), 201

    except Exception as e:
        # Handle any exceptions that occur during user creation
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": "Failed to create user"}), 500


@app.route("/ollama-chat", methods=["POST"])
def ollama_chat():
    try:
        messages = request.json.get("messages")

        if not isinstance(messages, list):
            messages = [messages]

        def generate():
            response = ollama.chat(
                model="llama3.1",
                messages=messages,
                options={"temperature": 0.9, "max_token": 2000},
                stream=True,
            )

            for part in response:
                content = part.get("message", {}).get("content", "")
                yield f"data: {json.dumps({'content': content})}\n\n"

                if part.get("done"):
                    break

            # Signal the end of the stream
            yield "data: [DONE]\n\n"

        return Response(
            generate(),
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        print(f"Error processing request: {e}")
        return {"error": "Error processing request"}, 500


@app.route("/bedrock-chat", methods=["POST"])
def bedrock_chat():
    try:
        messages = request.json.get("messages", [])

        # Ensure messages is a list
        if not isinstance(messages, list):
            messages = [messages]

        # Validate each message
        for message in messages:
            if (
                "role" not in message
                or "content" not in message
                or not message["content"].strip()
            ):
                return {
                    "error": 'Each message must contain "role" and non-empty "content"'
                }, 400

        def generate():
            response = client.messages.create(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=messages,
                max_tokens=4000,
                stream=True,
            )

            for event in response:
                # Print the type and content of the event for debugging
                print(f"Received event: {event}")

                # Assuming event is an instance of a class
                if hasattr(event, "type") and event.type == "content_block_delta":
                    delta = getattr(event, "delta", {})
                    if hasattr(delta, "type") and delta.type == "text_delta":
                        content = getattr(delta, "text", "")
                        yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
            "Connection": "keep-alive",
        }
        return Response(generate(), headers=headers)

    except Exception as e:
        print(f"Error processing Bedrock chat request: {e}")
        return {"error": "Error processing Bedrock chat request"}, 500


@app.route("/", methods=["GET"])
def health():
    return {"message": "OK"}


if __name__ == "__main__":
    app.run(debug=True)
    app.run(port=8000)
