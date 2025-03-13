import React, { useEffect, useState } from "react";
import axios from "axios";
import { io } from "socket.io-client";

// Connect to WebSocket (ensure backend WebSocket is running)
const socket = io("http://192.168.2.117:5001", {  // Service B WebSocket URL
  transports: ["websocket", "polling"],
  reconnectionAttempts: 5,
  timeout: 20000,
});

function App() {
  const [services, setServices] = useState([]);
  const [message, setMessage] = useState("");
  const [logs, setLogs] = useState([]);
  const [selectedService, setSelectedService] = useState("");

  // Fetch available services from Flask API
  const fetchServices = async () => {
    try {
      const response = await axios.get("http://192.168.2.153:5003/services"); // Correct API endpoint
      console.log("Fetched Services:", response.data);

      // Convert object to array
      setServices(Object.entries(response.data));
    } catch (error) {
      console.error("Error fetching services:", error);
      setLogs((prevLogs) => [...prevLogs, "Failed to fetch services"]);
    }
  };

  useEffect(() => {
    fetchServices(); // Fetch services on load

    // WebSocket event listeners for real-time updates
    socket.on("message_received", (data) => {
      setLogs((prevLogs) => [
        ...prevLogs,
        `Received: "${data.message}" from ${data.from}`,
      ]);
    });

    socket.on("message_forwarded", (data) => {
      setLogs((prevLogs) => [
        ...prevLogs,
        `Forwarded: "${data.message}" from ${data.from} to ${data.to}`,
      ]);
    });

    socket.on("message_sent", (data) => {
      setLogs((prevLogs) => [
        ...prevLogs,
        `Sent: "${data.message}" to ${data.to}`,
      ]);
    });

    return () => {
      socket.off("message_received");
      socket.off("message_forwarded");
      socket.off("message_sent");
    };
  }, []);

  const sendMessage = async () => {
    if (!message) {
      setLogs((prevLogs) => [...prevLogs, "Write something first!"]);
      return;
    }
    if (!selectedService) {
      setLogs((prevLogs) => [...prevLogs, "No service selected!"]);
      return;
    }

    try {
      console.log(`Sending to: ${selectedService}`);
      const response = await axios.post("http://192.168.2.117:5001/send-message", {
        to_service: selectedService,
        message: message,
      });

      setLogs((prevLogs) => [
        ...prevLogs,
        `Sent: "${message}" to ${selectedService}`,
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

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Microservice Communication</h1>

      <div>
        <h3>Available Services:</h3>
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>Service ID</th>
              <th>Service Name</th>
              <th>Host</th>
              <th>Port</th>
            </tr>
          </thead>
          <tbody>
            {services.length > 0 ? (
              services.map(([serviceId, details]) => (
                <tr key={serviceId}>
                  <td>{serviceId}</td>
                  <td>{details.name}</td>
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

        <select
          onChange={(e) => setSelectedService(e.target.value)}
          value={selectedService}
          style={{ marginLeft: "10px" }}
        >
          <option value="">Select Service</option>
          {services.map(([serviceId, details]) => (
            <option key={serviceId} value={serviceId}>
              {details.name}
            </option>
          ))}
        </select>

        <button onClick={sendMessage} style={{ marginLeft: "10px" }}>
          Send Message
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
