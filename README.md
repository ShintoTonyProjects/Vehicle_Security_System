# 🚗 Vehicle Security System – Smart Multi-Layer Protection


A custom-designed **smart vehicle security system** combining AI and embedded technologies to prevent theft, detect drowsiness, and offer full control through facial recognition, RFID, GPS tracking, and remote commands via SMS.

---

## 🔧 Key Features

- 🧠 **Driver Face Recognition**  
  Only authorized faces can start the vehicle using a live webcam-based verification system (OpenCV + Python).

- 😴 **Drowsiness Detection System**  
  Alerts and prevents accidents using real-time Eye Aspect Ratio (EAR) monitoring with a webcam.

- 🆔 **RFID Vehicle Access Control**  
  Unlock and start the vehicle using pre-registered RFID tags.

- 📍 **Live GPS Tracking & SMS Alerts**  
  Track vehicle location via GPS, and receive coordinates or system status through SMS.

- ✂️ **Remote Vehicle Cutoff**  
  Stop the vehicle remotely via a secret SMS command.

---

## 🛠️ Technologies Used

| Component        | Description                      |
|------------------|----------------------------------|
| **Python + OpenCV** | Face recognition & drowsiness detection |
| **Esp-32** | GPS, RFID, and SMS handling         |
| **Raspberry Pi 5** | Host for image processing and control logic |
| **GSM Module SIM800l**     | For sending and receiving SMS     |
| **GPS Module Neo 6M**     | For location tracking             |
| **RFID Reader (RC522)** | For contactless authentication     |

---

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
    
