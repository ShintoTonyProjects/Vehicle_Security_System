import cv2
import face_recognition
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import time
import numpy as np
from collections import deque
import subprocess
import os
import threading
from datetime import datetime
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 170)  # 130–170
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3].id)

def speak(text):
    def _speak():
        engine.say(" ")  
        engine.runAndWait()
        time.sleep(0.3) 
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.7) 
    threading.Thread(target=_speak).start()  # Non-blocking

# ======================
# CONFIGURATION
# ======================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENCODINGS_PATH = PROJECT_ROOT / "trained_data" / "encodings.pkl"

# Face Recognition Settings
RESIZE_FACTOR = 0.75
CONFIDENCE_THRESHOLD = 0.6
REQUIRED_VERIFICATION_FRAMES = 15  # ~3 seconds at 5 FPS
REQUIRED_UNKNOWN_FRAMES = 25       # ~5 seconds at 5 FPS
POSITION_HISTORY_LENGTH = 5

# Email Settings
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "shinto.tony.projects@gmail.com"
EMAIL_PASSWORD = "tcoxcgwujalzxqze"
RECIPIENT_EMAIL = "shinto.tony.projects@gmail.com"

# System Switching
ENABLE_SYSTEM_SWITCH = True
DROWSINESS_SCRIPT = PROJECT_ROOT / "scripts" / "drowsiness.py"

# ======================
# FACE RECOGNITION SYSTEM
# ======================
class FaceRecognitionSystem:
    def __init__(self):
        self.load_known_faces()
        self.verification_counts = {}
        self.unknown_counts = {}
        self.current_identity = None
        self.tracked_positions = deque(maxlen=POSITION_HISTORY_LENGTH)
        self.last_capture_time = 0
        self.verification_complete = False
        self.unknown_detected = False
        self.last_unknown_feedback_time = 0

    def load_known_faces(self):
        with open(ENCODINGS_PATH, "rb") as f:
            self.known_data = pickle.load(f)

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        boxes = []
        names = []
        current_names = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = (
                int(top / RESIZE_FACTOR),
                int(right / RESIZE_FACTOR),
                int(bottom / RESIZE_FACTOR),
                int(left / RESIZE_FACTOR)
            )

            self.tracked_positions.append((top, right, bottom, left))
            avg_box = np.mean(self.tracked_positions, axis=0).astype(int)
            top, right, bottom, left = avg_box

            name, confidence = self.recognize_face(face_encoding)
            display_name, status = self.update_verification(name, confidence)

            boxes.append((top, right, bottom, left))
            names.append(display_name)
            current_names.append((name, confidence))

            color = (0, 255, 0) if status == "verified" else (0, 0, 255) if status == "unknown" else (255, 165, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, display_name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        self.check_unknown_face(frame, current_names)

        return frame, boxes, names

    def recognize_face(self, face_encoding):
        matches = face_recognition.compare_faces(self.known_data["encodings"], face_encoding, tolerance=0.5)

        name = "Unknown"
        confidence = 0

        if True in matches:
            matched_idxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matched_idxs:
                name = self.known_data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
            confidence = counts[name] / len(matched_idxs)

        return name, confidence

    def update_verification(self, name, confidence):
        status = "processing"

        if confidence >= CONFIDENCE_THRESHOLD:
            if name not in self.verification_counts:
                self.verification_counts[name] = 0
            self.verification_counts[name] += 1

            for other_name in list(self.verification_counts.keys()):
                if other_name != name:
                    self.verification_counts[other_name] = max(0, self.verification_counts[other_name] - 1)

            if self.verification_counts[name] >= REQUIRED_VERIFICATION_FRAMES:
                if not self.verification_complete:
                    self.current_identity = name
                    self.verification_complete = True
                    speak("User Authentication Success")
                status = "verified"
                display_name = name
            else:
                display_name = "Recognizing..."
        else:
            name = "Unknown"
            display_name = "Unknown"
            if self.current_identity:
                self.verification_counts[self.current_identity] = max(0, self.verification_counts[self.current_identity] - 1)
                if self.verification_counts[self.current_identity] == 0:
                    self.current_identity = None
                    self.verification_complete = False
            status = "unknown"

        return display_name, status

    def check_unknown_face(self, frame, current_names):
        unknown_present = any(name[0] == "Unknown" and name[1] < 0.4 for name in current_names)
        verified_present = any(name[0] != "Unknown" for name in current_names)

        if unknown_present and not verified_present:
            if "Unknown" not in self.unknown_counts:
                self.unknown_counts["Unknown"] = 0
            self.unknown_counts["Unknown"] += 1

            if self.unknown_counts["Unknown"] >= REQUIRED_UNKNOWN_FRAMES and not self.unknown_detected:
                self.unknown_detected = True
                now = time.time()
                if now - self.last_unknown_feedback_time > 10:  # Throttle audio
                    speak("Access denied. Unknown person detected.")
                    self.last_unknown_feedback_time = now
                self.capture_and_send_unknown(frame)
        else:
            self.unknown_counts = {}
            self.unknown_detected = False

    def capture_and_send_unknown(self, frame):
        if EMAIL_ENABLED:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unknown_{timestamp}.jpg"
            cv2.imwrite(filename, frame)

            threading.Thread(
                target=self.send_email,
                args=("Unknown Person Detected", filename)
            ).start()

    def send_email(self, subject, image_path):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = subject

            body = f"{subject} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText(body, 'plain'))

            with open(image_path, 'rb') as f:
                img = MIMEImage(f.read())
                msg.attach(img)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
            server.quit()

            print(f"Email alert sent: {subject}")
            os.remove(image_path)
        except Exception as e:
            print(f"Error sending email: {e}")

# ======================
# MAIN APPLICATION
# ======================
def main():
    face_system = FaceRecognitionSystem()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_time = time.time()
    fps_counter = 0
    fps = 0

    while True:
        ret, vid = cap.read()
        if not ret:
            break

        frame = cv2.flip(vid, 1)

        processed_frame, boxes, names = face_system.process_frame(frame)

        fps_counter += 1
        if time.time() - last_time >= 1.0:
            fps = fps_counter
            fps_counter = 0
            last_time = time.time()

        cv2.putText(processed_frame, f"FPS: {fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', processed_frame)

        if ENABLE_SYSTEM_SWITCH and face_system.verification_complete:
            verified_user = face_system.current_identity
            print(f"Verified user: {verified_user}. Switching to drowsiness detection...")
            speak(f"Verified user: {verified_user}. Switching to drowsiness detection...")
            cap.release()
            cv2.destroyAllWindows()
            subprocess.Popen(["python", DROWSINESS_SCRIPT])
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
