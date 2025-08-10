# 🚗 Vehicle Security System – Smart Multi-Layer Protection


A custom-designed **smart vehicle security system** combining AI and embedded technologies to prevent theft, detect drowsiness, and offer full control through facial recognition, RFID, GPS tracking, and remote commands via SMS.

---

## 🔧 Key Features

- 🧠 **Driver Face Recognition**  
  Only authorized faces can use the vehicle using a live webcam-based verification system (OpenCV + Python).

- 😴 **Drowsiness Detection System**  
  Alerts and prevents accidents using real-time Eye Aspect Ratio (EAR) monitoring with a webcam.

- 🆔 **RFID Vehicle Access Control**  
  Unlock and start the vehicle using pre-registered RFID tags.

- 📍 **Live GPS Tracking & SMS Alerts**  
  Track vehicle location via GPS, and receive coordinates or system status through the App.

- ✂️ **Remote Vehicle Cutoff**  
  Stop the vehicle remotely via cloud data communication or via a secret SMS command.

---

## 🛠️ Technologies Used

| Component        | Description                      |
|------------------|----------------------------------|
| **Python + OpenCV** | Face recognition & drowsiness detection |
| **Esp-32** | GPS, RFID, and SMS handling         |
| **Raspberry Pi 5** | Host for image processing and control logic |
| **GSM Module SIM7600**     | Provide Internet and SMS control   |
| **GPS Module Neo 6M**     | For location tracking             |
| **RFID Reader (RC522)** | For contactless authentication     |

---

# 🚗 AutoConnectX – Smart Vehicle Security & Control App

Welcome to **AutoConnectX**, a custom-built mobile app designed to provide seamless, smart control over your vehicle’s security and monitoring systems — without exposing the underlying code.

---

## 📱 App Features Overview

AutoConnectX offers a comprehensive suite of smart vehicle features to keep your car secure and connected:

- 🧠 **Face Recognition Access**  
  Authenticate drivers using live facial recognition technology for secure vehicle unlocking.

- 😴 **Driver Drowsiness Alerts**  
  Real-time monitoring detects signs of drowsiness and issues timely alerts to prevent accidents.

- 🆔 **RFID-Based Vehicle Control**  
  Unlock and Lock your vehicle effortlessly through the App.

- 📍 **Live GPS Tracking & Notifications**  
  Track your vehicle location in real-time and receive status updates via the app.

- ✂️ **Remote Engine Cutoff**  
  Remotely disable your vehicle’s ignition instantly through secure cloud commands or secret SMS codes.


## ⚠️ Note on Source Code

The source code and sensitive files are maintained in a **private repository** for security and privacy reasons. This public repo focuses on sharing the vision, ideas, and progress of the AutoConnectX project.

---

*Created by Shinto Tony*  

## 📐 System Architecture

```mermaid

graph TD;
    Camera -->|Face & Drowsiness Detection| RaspberryPi
    RaspberryPi -->|Authorized Person| Arduino
    RaspberryPi -->|Unknown Person Detected| Email_Owner
    RaspberryPi -->|Driver Drowsy| Alert
    RFID --> Arduino
    GPS --> Arduino
    GSM --> Arduino
    Arduino -->|Ignition Control| RelayModule
    
