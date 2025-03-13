# from flask import Flask, jsonify
# import requests

# app = Flask(__name__)

# # Mac calls Windows here
# @app.route('/call-service-b', methods=['GET'])
# def call_service_b():
#     url = "http://192.168.2.117:5001/receive-message"  # Windows Device IP here
#     try:
#         response = requests.get(url)
#         data = response.json()
#         return jsonify({"response_from_service_b": data})
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": str(e)}), 500

# # Mac receives messages here
# @app.route('/receive-message', methods=['GET'])
# def receive_message():
#     # Call local Ollama instance for a generated message
#     ollama_response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "llama3.2",
#             "prompt": "Hello, I am Ollama serving your request Arth, Add your identitiy at the end of text. Your identity is Service B.",
#             "stream": False 
#         }
#     )
#     return jsonify(ollama_response.json())

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5002, debug=True)

from flask import Flask, jsonify, request
import time
import threading
from flask_cors import CORS 
import time
import requests
import eventlet
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# eventlet.monkey_patch() 

# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Store registered services
service_registry = {}

# Define expiration time (5 minutes)
EXPIRATION_TIME = 5 * 60  # 5 minutes in seconds

@app.route('/register', methods=['POST'])
def register_service():
    """Registers a microservice with its IP, port, and last active timestamp."""
    data = request.json
    service_id = f"{data['ip']}:{data['port']}"
    service_registry[service_id] = {
        "ip": data["ip"],
        "name": data["name"],
        "port": data["port"],
        "last_active": time.time()
    }
    return jsonify({"message": "Service registered successfully"}), 200

@app.route('/services', methods=['GET'])
def list_services():
    """Returns the list of currently registered services."""
    current_time = time.time()
    active_services = {
        k: v for k, v in service_registry.items() if current_time - v["last_active"] < EXPIRATION_TIME
    }
    return jsonify(active_services)

@app.route('/update-activity', methods=['POST'])
def update_activity():
    """Updates last active time when a service sends a message."""
    data = request.json
    service_id = f"{data['ip']}:{data['port']}"
    if service_id in service_registry:
        service_registry[service_id]["last_active"] = time.time()
        return jsonify({"message": "Activity updated"}), 200
    return jsonify({"error": "Service not found"}), 404

@app.route('/deregister', methods=['POST'])
def deregister_service():
    """Deregisters a service when it stops running."""
    data = request.json
    service_id = f"{data['ip']}:{data['port']}"
    if service_id in service_registry:
        del service_registry[service_id]
        return jsonify({"message": "Service deregistered"}), 200
    return jsonify({"error": "Service not found"}), 404

def remove_inactive_services():
    """Continuously removes services inactive for more than 5 minutes."""
    while True:
        time.sleep(60)  # Check every 60 seconds
        current_time = time.time()
        inactive_services = [
            service_id for service_id, info in service_registry.items()
            if current_time - info["last_active"] > EXPIRATION_TIME
        ]
        for service_id in inactive_services:
            del service_registry[service_id]
            print(f"Service {service_id} removed due to inactivity.")

# Start background thread to remove inactive services
threading.Thread(target=remove_inactive_services, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
