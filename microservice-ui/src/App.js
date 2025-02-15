import React, { useEffect, useState } from "react";
import axios from "axios";
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:5003", {
  transports: ["websocket", "polling"],
  reconnectionAttempts: 5,
  timeout: 20000,
});

function App() {
  const [services, setServices] = useState([]);
  const [message, setMessage] = useState("");
  const [logs, setLogs] = useState([]);

  // Fetch available services from Flask API
  const fetchServices = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5003/services");
      console.log("Fetched Services:", response.data);
      setServices(Object.entries(response.data.services)); // Convert object to array
    } catch (error) {
      console.error("Error fetching services:", error);
    }
  };

  useEffect(() => {
    fetchServices(); // Fetch services on load
  
    socket.on("update_services", (updatedServices) => {
      setServices(Object.entries(updatedServices));
    });
  
    socket.on("message_forwarded", (data) => {
      console.log("WebSocket Received:", data);
  
      setLogs((prevLogs) => [
        ...prevLogs,
        `Sent: "${data.message}" from ${data.from} to ${data.to}`,
        `LLM Response: ${JSON.stringify(data.response)}`,
      ]);
    });
  
    return () => {
      socket.off("update_services");
      socket.off("message_forwarded");
    };
  }, []);
  

  const sendMessage = async () => {
    if (!message || services.length < 2) {
      setLogs((prevLogs) => [...prevLogs, "No services available or message is empty"]);
      return;
    }
  
    const [firstService, secondService] = services.map(([serviceId]) => serviceId);
  
    try {
      const response = await axios.post("http://127.0.0.1:5003/forward", {
        from_service: firstService,
        to_service: secondService,
        message: message,
      });
  
      setLogs((prevLogs) => [
        ...prevLogs,
        `Sent: "${message}" from ${firstService} to ${secondService}`,
        `Response: ${JSON.stringify(response.data)}`,
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setLogs((prevLogs) => [
        ...prevLogs,
        `Error sending message: ${error.response?.data?.error || error.message}`,
      ]);
    }
  };
  
  

  const sendMessageToAll = async () => {
    if (!message) return;
  
    const requests = services.map(async ([serviceId]) => {
      try {
        const response = await axios.post("http://127.0.0.1:5003/forward", {
          from_service: services[0][0],  // First service sends message
          to_service: serviceId,
          message: message,
        });
  
        setLogs((prevLogs) => [
          ...prevLogs,
          `Sent: "${message}" to ${serviceId}`,
          `LLM Response: ${JSON.stringify(response.data)}`,
        ]);
      } catch (error) {
        setLogs((prevLogs) => [
          ...prevLogs,
          `Error sending to ${serviceId}: ${error.message}`,
        ]);
      }
    });
  
    await Promise.all(requests);
  };
  

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Microservice Communication</h1>

      <div>
        <h3>Available Services:</h3>
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>Service ID</th>
              <th>Host</th>
              <th>Port</th>
            </tr>
          </thead>
          <tbody>
            {services.length > 0 ? (
              services.map(([serviceId, details]) => (
                <tr key={serviceId}>
                  <td>{serviceId}</td>
                  <td>{details.host}</td>
                  <td>{details.port}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3">No services available</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          type="text"
          placeholder="Enter message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button onClick={sendMessageToAll} style={{ marginLeft: "10px" }}>
          Send to All
        </button>
      </div>

      <div style={{ marginTop: "20px" }}>
        <h3>Logs:</h3>
        <div
          style={{
            backgroundColor: "#f4f4f4",
            padding: "10px",
            borderRadius: "5px",
          }}
        >
          {logs.map((log, index) => (
            <p key={index}>{log}</p>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
