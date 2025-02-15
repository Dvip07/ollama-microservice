import requests
import json
import subprocess
import sys
import threading
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Get port from command-line arguments (default: 5001)
SERVICE_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
SERVICE_NAME = "llm-service"
SERVICE_ID = f"{SERVICE_NAME}-{SERVICE_PORT}"
SERVICE_HOST = "127.0.0.1"
REGISTRAR_URL = "http://127.0.0.1:5003"

def register_service():
    """Send a heartbeat to the Service Registrar."""
    while True:
        try:
            requests.post(f"{REGISTRAR_URL}/register", json={
                "service_id": SERVICE_ID,
                "host": SERVICE_HOST,
                "port": SERVICE_PORT
            })
            print(f"Sent heartbeat for {SERVICE_ID}")
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
        time.sleep(120)  # Send heartbeat every 2 minutes
        
def query_ollama(prompt):
    """Process message using Ollama LLM."""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"LLM Error: {e}"

@app.route('/receive', methods=['POST'])
def receive_message():
    """Receive a forwarded message and process with Ollama."""
    data = request.json
    sender_service = data.get("from_service")
    message = data.get("message")

    print(f"{SERVICE_ID} received from {sender_service}: {message}")

    # Process the message using Ollama LLM
    response_message = query_ollama(message)

    # Send the response back to the sender for further conversation
    requests.post(f"{REGISTRAR_URL}/forward", json={
        "from_service": SERVICE_ID,
        "to_service": sender_service,
        "message": response_message
    })

    return jsonify({"response": response_message}), 200

@app.route('/list_services', methods=['GET'])
def get_services():
    """Fetch the list of available services from the registrar."""
    try:
        response = requests.get("http://127.0.0.1:5003/services")
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send', methods=['POST'])
def send_message():
    """Request the registrar to forward a message to another service."""
    data = request.json
    target_service_id = data.get("service_id")
    message = data.get("message")

    if not target_service_id or not message:
        return jsonify({"error": "Invalid request"}), 400

    try:
        response = requests.post(f"{REGISTRAR_URL}/forward", json={
            "service_id": target_service_id,
            "message": message
        })
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the heartbeat thread
threading.Thread(target=register_service, daemon=True).start()
# threading.Thread(target=register_service, daemon=True).start()


if __name__ == '__main__':
    app.run(port=SERVICE_PORT)
