import requests
import socket
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS  
from flask_socketio import SocketIO

# Enable logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket

# Service Registry
SERVICE_REGISTRY_URL = "http://192.168.2.153:5003"

# Own IP Address & Port
IP_ADDRESS = "192.168.2.117"  # Change this to Service B's IP
PORT = 5001  # Change as needed

def register_service():
    """Registers Service B with the service registry."""
    service_data = {"ip": IP_ADDRESS, "port": PORT, "name": "Service B"}
    try:
        requests.post(f"{SERVICE_REGISTRY_URL}/register", json=service_data)
        logger.info(f"Registered service at {IP_ADDRESS}:{PORT}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to register service: {e}")

def update_activity():
    """Updates last active timestamp in the registry when a message is sent."""
    service_data = {"ip": IP_ADDRESS, "port": PORT}
    try:
        requests.post(f"{SERVICE_REGISTRY_URL}/update-activity", json=service_data)
    except requests.exceptions.RequestException:
        pass  

@app.route('/receive-message', methods=['POST'])
def receive_message():
    """Handles incoming messages, processes with Ollama, and sends a response back."""
    data = request.json
    sender_service = data.get("from_service")  # Extract sender
    message_received = data.get("message")

    update_activity()

    logger.info(f"Received message: '{message_received}' from {sender_service}")

    # Emit event to frontend for real-time updates
    socketio.emit("message_received", {
        "from": sender_service,
        "message": message_received
    })

    # Generate response using Ollama
    ollama_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": f"Received message: {message_received}. Respond to it.",
            "stream": False 
        }
    )

    response_text = ollama_response.json().get("response", "No response from Ollama")

    logger.info(f"Ollama Response: {response_text}")

    # Send response back to frontend
    socketio.emit("message_forwarded", {
        "from": f"{IP_ADDRESS}:{PORT}",
        "to": sender_service,
        "message": response_text
    })

    # Send the generated response **back** to the sender
    if sender_service:
        try:
            response = requests.post(f"http://{sender_service}/receive-message", json={
                "message": response_text,
                "from_service": f"{IP_ADDRESS}:{PORT}"
            })
            logger.info(f"Sent response back to {sender_service}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send response to {sender_service}: {e}")

    return jsonify({"response": response_text})

@app.route('/send-message', methods=['POST'])
def send_message():
    """Sends a message to a selected registered service."""
    target_service = request.json.get("to_service")
    message = request.json.get("message")

    logger.info(f"Sending message '{message}' to {target_service}")

    if not target_service or not message:
        return jsonify({"error": "Target service or message not specified"}), 400

    try:
        response = requests.post(f"http://{target_service}/receive-message", json={
            "message": message,
            "from_service": f"{IP_ADDRESS}:{PORT}"
        })

        # Notify frontend when a message is sent
        socketio.emit("message_sent", {
            "from": f"{IP_ADDRESS}:{PORT}",
            "to": target_service,
            "message": message
        })

        return jsonify({"response": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to reach {target_service}: {str(e)}"}), 500

if __name__ == '__main__':
    register_service()
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True)
