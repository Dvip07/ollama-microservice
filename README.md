# ollama-microservice

# Ollama Microservices Communication

This project sets up multiple microservices running Ollama LLM (`llama3.2`) that can communicate with each other. The microservices register with a **Service Registrar**, send messages to each other, and return AI-generated responses. A **React frontend** displays the conversations in real-time.

## 🚀 Features
- **Multiple Microservices**: Each service runs Ollama LLM (`llama3.2`).
- **Dynamic Registration**: Services register with the **Service Registrar**.
- **LLM-based Chat**: Services exchange messages and respond using AI.
- **Real-time UI Updates**: Messages are displayed in a **React** frontend.

---

## 📌 Requirements
These are the Requirements to run this project on your system

- **Python 3**
- **Flask & Flask-SocketIO**
- **Ollama CLI** ([Install Ollama](https://ollama.ai))
- **Node.js & npm** (for React frontend)

### 📦 Install Dependencies
Run the following commands to install dependencies:

```sh
pip install flask flask-socketio flask-cors requests eventlet
```

---

## 🏗️ Setup and Run
### **1️⃣ Start the Service Registrar**
The **Service Registrar** manages microservices and message forwarding.

```sh
python registrar.py
```

### **2️⃣ Start Multiple Microservices**
Each service runs an **Ollama LLM instance** and can communicate with other services.

```sh
python app.py 5001  # Start first service
python app.py 5002  # Start second service
```

### **3️⃣ Start React Frontend**
Navigate to the **React frontend directory** and run:

```sh
npm install  # Install dependencies
npm start    # Start the frontend
```

### **4️⃣ Open the UI**
Go to: **[http://localhost:3000](http://localhost:3000)**

Send a message using the UI, and watch **Ollama microservices** talk to each other! 🧠💬

---

## 📝 How It Works
### **1. Service Registration**
Each **microservice (`app.py`) registers itself** with the **Service Registrar (`registrar.py`)**.

### **2. Message Processing**
- A microservice receives a message from another service.
- It processes the message using **Ollama LLM (`llama3.2`)**.
- It responds with the AI-generated reply.
- The conversation continues between services.

### **3. UI Updates in Real-Time**
- The **React frontend** fetches **active microservices**.
- Messages are forwarded through the **Service Registrar**.
- WebSockets update the conversation in real-time.

### **4. Timeout**
- If a service failed to send a message every five minutes, it gets deleted from the service registrar.

---

## 🔍 API Endpoints
### **1️⃣ Service Registrar (`registrar.py`)**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/register` | Register a microservice |
| `GET` | `/services` | Get active services |
| `POST` | `/forward` | Forward a message to a service |

### **2️⃣ Microservices (`app.py`)**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/receive` | Receive a message and process with Ollama LLM |

---

## 🛠️ Troubleshooting
### **1️⃣ Services Not Registering?**
Run:
```sh
curl http://127.0.0.1:5003/services
```
- If `{}` is returned, restart services:
```sh
python app.py 5001
python app.py 5002
```

### **2️⃣ Messages Not Forwarding?**
Test manually:
```sh
curl -X POST http://127.0.0.1:5003/forward \  
    -H "Content-Type: application/json" \  
    -d '{"from_service": "ollama-service-5001", "to_service": "ollama-service-5002", "message": "Hello"}'
```
- Check logs in `registrar.py` and `app.py`

### **3️⃣ UI Not Updating?**
Check WebSockets in Chrome Console (`F12 → Console`):
```javascript
const socket = io("http://127.0.0.1:5003");
socket.on("message_forwarded", (data) => console.log("WebSocket Message:", data));
```

---
