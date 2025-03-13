Here is the updated `README.md` file for your **Microservice Communication System**. It includes **setup instructions, usage, and troubleshooting** steps.

---

## 📌 **Microservice Communication System**
A system where **multiple microservices** communicate with each other using **Flask (Python) APIs, WebSockets, and React (Frontend).**  
Each service registers itself in a **Service Registry**, can send messages to other registered services, and process responses using **Ollama AI (LLM Model).**  

---

## 📂 **Project Structure**
```
/microservices-project
│── /frontend                # React frontend (Service B UI)
│── /backend-service-a       # Flask API for Service A
│── /backend-service-b       # Flask API for Service B
│── /service-registry        # Flask-based service registry
│── README.md                # Documentation
```

---

## 🚀 **Features**
✅ **Service Discovery** - Services register/deregister automatically.  
✅ **Real-Time Communication** - Uses **WebSockets** for instant message forwarding.  
✅ **AI-Powered Response** - Microservices use **Ollama** to generate AI-based replies.  
✅ **Message Routing** - Send messages to **specific services** via the frontend.  
✅ **Auto-Deregistration** - Services inactive for **5+ minutes** are removed.  

---

## ⚙️ **Setup Instructions**

### 🔹 **1️⃣ Install Dependencies**
Ensure Python (Flask) & Node.js (React) are installed.

#### 📌 **Backend (Service A & B)**
```bash
pip install flask flask-cors requests flask-socketio
```

#### 📌 **Frontend**
```bash
npm install axios socket.io-client
```

---

### 🔹 **2️⃣ Start Service Registry**
The **Service Registry** manages active services. Start it first:
```bash
cd service-registry
python service_registry.py
```

---

### 🔹 **3️⃣ Start Microservices**
Start **Service A** (Mac/Linux) & **Service B** (Windows):

#### 📌 **Run Service A (Mac/Linux)**
```bash
cd backend-service-a
python service_a.py
```

#### 📌 **Run Service B (Windows)**
```bash
cd backend-service-b
python service_b.py
```

---

### 🔹 **4️⃣ Start the Frontend**
The **React frontend** runs on `localhost:3000`.  
```bash
cd frontend
npm start
```

---

## 🔥 **How It Works**
1️⃣ Each microservice **registers with the service registry** when started.  
2️⃣ Frontend **fetches available services** and shows them in a dropdown.  
3️⃣ Users **send messages to selected services** from the UI.  
4️⃣ The **receiver processes the message** using **Ollama AI** and responds.  
5️⃣ The response **appears in the UI logs in real time** (via WebSockets).  

---

## 🖥 **Frontend Usage**
📌 **1️⃣ Open `http://localhost:3000` in a browser.**  
📌 **2️⃣ Select a service from the dropdown.**  
📌 **3️⃣ Type a message and click "Send Message".**  
📌 **4️⃣ View the logs as messages are sent/received.**

---

## 🛠 **Troubleshooting**
### ❌ **CORS Policy Error?**
If the frontend can't communicate with Flask:
- Restart Flask servers.
- Ensure `flask-cors` is installed.
- Add this to Flask:
  ```python
  from flask_cors import CORS
  CORS(app, resources={r"/*": {"origins": "*"}})
  ```

### ❌ **WebSocket Not Connecting?**
- Ensure **Flask WebSockets (`socketio.run(app)`)** is running.
- Restart the **Service Registry**.
- Run:
  ```bash
  npm install socket.io-client
  ```

### ❌ **Messages Not Being Forwarded?**
- Ensure the **correct service IPs are used**.
- Check Flask logs for **"Failed to reach target service"** errors.

---

## 🎯 **Next Steps**
✅ Add authentication for secure communication.  
✅ Improve logging with timestamps & JSON formatting.  
✅ Deploy services using **Docker & Kubernetes**.  

---

## 🤝 **Contributors**
- **Your Name** (Lead Developer)
- **Your Team Members**

📌 **Questions?** Reach out via [GitHub Issues](#) 🚀

---

🚀 **Enjoy building scalable microservices!** 🚀
