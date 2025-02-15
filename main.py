from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import threading
import time
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket

service_registry = {}
HEARTBEAT_TIMEOUT = 300  # 5 minutes

@app.route('/register', methods=['POST'])
def register_service():
    """Register a microservice or update its heartbeat."""
    data = request.json
    service_id = data.get("service_id")
    service_host = data.get("host")
    service_port = data.get("port")

    if service_id and service_host and service_port:
        service_registry[service_id] = {
            "host": service_host,
            "port": service_port,
            "last_heartbeat": time.time()
        }
        # Notify frontend about new service
        socketio.emit('update_services', service_registry)
        return jsonify({"message": f"Service {service_id} registered/updated."}), 200

    return jsonify({"error": "Invalid request"}), 400

@app.route('/services', methods=['GET'])
def list_services():
    """Return the list of active services."""
    return jsonify({"services": service_registry})

@app.route('/forward', methods=['POST'])
def forward_message():
    """Forward a message to another service."""
    data = request.json
    target_service_id = data.get("service_id")
    message = data.get("message")

    if target_service_id not in service_registry:
        return jsonify({"error": "Service not found"}), 404

    target_service = service_registry[target_service_id]
    target_url = f"http://{target_service['host']}:{target_service['port']}/receive"

    try:
        response = requests.post(target_url, json={"message": message})
        response_data = response.json()

        # Notify frontend about message forwarding
        socketio.emit('message_forwarded', {
            "from": "Service Registrar",
            "to": target_service_id,
            "message": message,
            "response": response_data
        })

        return response_data, response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup_services():
    """Remove services that have not sent a heartbeat in 5 minutes."""
    while True:
        current_time = time.time()
        for service_id in list(service_registry.keys()):
            if current_time - service_registry[service_id]["last_heartbeat"] > HEARTBEAT_TIMEOUT:
                print(f"Removing inactive service: {service_id}")
                del service_registry[service_id]
                socketio.emit('update_services', service_registry)  # Notify frontend
        time.sleep(60)

# Start the cleanup thread
threading.Thread(target=cleanup_services, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, port=5000)
