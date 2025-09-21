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

(⚠️ using these components only as a part of prototyping)

| Component        | Description                      |
|------------------|----------------------------------|
| **Python + OpenCV** | Face recognition & drowsiness detection |
| **ESP32** | GPS, RFID, and SMS handling (optional) |
| **Raspberry Pi 5** | Host for image processing and control logic |
| **GSM Module SIM7600**     | Internet and SMS control   |
| **GPS Module Neo 6M**     | Location tracking             |
| **RFID Reader (RC522)** | Contactless authentication     |

---

# 🚗 AutoConnectX – Smart Vehicle Security & Control App

Welcome to **AutoConnectX**, a custom-built mobile app designed to provide seamless, smart control over your vehicle’s security and monitoring systems — without exposing the underlying code.

---

## 📱 App Features Overview

AutoConnectX offers a comprehensive suite of smart vehicle features to keep your car secure and connected:

- 🧠 **Face Recognition Access**  
- 😴 **Driver Drowsiness Alerts**  
- 🆔 **RFID-Based Vehicle Control**  
- 📍 **Live GPS Tracking & Notifications**  
- ✂️ **Remote Engine Cutoff**  

---

## 📂 Visual Portfolio (Placeholders)

- 📸 **App Screenshots:** [Google Drive Folder Link – App UI](https://drive.google.com/drive/folders/1HFt5DvUp-GYYjkV6Ozldppo9vVbuAs4N)  
- 🔧 **Prototype Hardware:** [Google Drive Folder Link – Assembly / Circuits](https://drive.google.com/file/d/11MkbFJOGEe59w7ooO8E9-ArXU_J1jws4/view?usp=drivesdk)
- 🎥 **Demo Videos:** [Google Drive Folder Link – Live Demo Clips](COMING-SOON)  

---

## ⚠️ Note on Source Code

The source code and sensitive files are maintained in a **private repository** for security and privacy reasons.  
This public repo focuses on sharing the vision, ideas, and progress of the AutoConnectX project.

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
