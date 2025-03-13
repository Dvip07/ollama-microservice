# import requests
# import socket
# import time
# from flask import Flask, jsonify, request

# app = Flask(__name__)

# # Service Registry URL (replace with actual registry IP if needed)
# SERVICE_REGISTRY_URL = "http://192.168.137.1:5003"

# # Get own IP address
# IP_ADDRESS = socket.gethostbyname(socket.gethostname())
# PORT = 5002  # Use 5002 for Mac

# def register_service():
#     """Registers the microservice with the service registry."""
#     service_data = {"ip": IP_ADDRESS, "port": PORT}
#     try:
#         requests.post(f"{SERVICE_REGISTRY_URL}/register", json=service_data)
#         print(f"Registered service at {IP_ADDRESS}:{PORT}")
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to register service: {e}")

# def update_activity():
#     """Updates last active timestamp in the registry when a message is sent."""
#     service_data = {"ip": IP_ADDRESS, "port": PORT}
#     try:
#         requests.post(f"{SERVICE_REGISTRY_URL}/update-activity", json=service_data)
#     except requests.exceptions.RequestException:
#         pass  # Ignore failures to avoid breaking communication

# @app.route('/receive-message', methods=['POST'])
# def receive_message():
#     """Handles incoming messages and updates activity."""
#     data = request.json
#     update_activity()
#     return jsonify({"response": f"Hi, I am Service at {IP_ADDRESS}:{PORT}, message received!"})

# @app.route('/send-message', methods=['POST'])
# def send_message():
#     """Sends a message to any registered service."""
#     target_service = request.json.get("target_service")
#     if not target_service:
#         return jsonify({"error": "Target service not specified"}), 400

#     try:
#         response = requests.post(f"http://{target_service}/receive-message", json={"from": f"{IP_ADDRESS}:{PORT}"})
#         return jsonify({"response": response.json()})
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": f"Failed to reach {target_service}: {str(e)}"}), 500

# if __name__ == '__main__':
#     register_service()
#     app.run(host='0.0.0.0', port=PORT, debug=True)


import requests
import socket
import time
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import requests
import socket
import logging
from flask_cors import CORS 


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# SERVICE_REGISTRY_URL = "http://192.168.2.153:5003"
# IP_ADDRESS = socket.gethostbyname(socket.gethostname())
# PORT = 5002  # Mac runs on port 5002

# Service Registry URL (replace with actual registry IP if needed)
SERVICE_REGISTRY_URL = "http://192.168.2.153:5003"

# Get own IP address
IP_ADDRESS = "192.168.2.153"
PORT = 5002  # Change this for each device 

def register_service():
    """Registers the microservice with the service registry."""
    service_data = {"ip": IP_ADDRESS, "port": PORT, "name": "Service A"}
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
# def receive_message():
#     """Handles incoming messages, processes with Ollama, and updates activity."""
#     data = request.json
#     update_activity()

#     # Generate response using Ollama
#     ollama_response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "llama3.2",
#             "prompt": f"Received message: {data.get('message')}. We have to respond on behalf of Service A.",
#             "stream": False 
#         }
#     )

#     response_text = ollama_response.json().get("response", "No response from Ollama")
#     return jsonify({"response": response_text})

def receive_message():
    """Handles incoming messages, processes with Ollama, and sends a response back."""
    data = request.json
    sender_service = data.get("from_service")  # Extract sender
    message_received = data.get("message")

    update_activity()

    logger.info(f"Received message: '{message_received}' from {sender_service}")

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
# def send_message():
    # """Sends a message to a selected registered service."""
    # target_service = request.json.get("target_service")
    # message = request.json.get("message")

    # logger.info(f"Sending message '{message}' to {target_service}")

    # if not target_service or not message:
    #     return jsonify({"error": "Target service or message not specified"}), 400

    # try:
    #     response = requests.post(f"http://{target_service}/receive-message", json={"message": message})
    #     return jsonify({"response": response.json()})
    # except requests.exceptions.RequestException as e:
    #     return jsonify({"error": f"Failed to reach {target_service}: {str(e)}"}), 500
    
def send_message():
    """Sends a message to a selected registered service."""
    target_service = request.json.get("target_service")
    message = request.json.get("message")

    logger.info(f"Sending message '{message}' to {target_service}")

    if not target_service or not message:
        return jsonify({"error": "Target service or message not specified"}), 400

    try:
        response = requests.post(f"http://{target_service}/receive-message", json={
            "message": message,
            "from_service": f"{IP_ADDRESS}:{PORT}"
        })
        return jsonify({"response": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to reach {target_service}: {str(e)}"}), 500


if __name__ == '__main__':
    register_service()
    app.run(host='0.0.0.0', port=PORT, debug=True)
