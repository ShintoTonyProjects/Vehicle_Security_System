import cv2
import dlib
import numpy as np
from scipy.spatial import distance
from imutils import face_utils
import time
import pyttsx3

# Initialize pyttsx3 engine for voice alerts
engine = pyttsx3.init()
engine.setProperty('volume', 1.0)  # Max volume
engine.setProperty('rate', 150)    # Speech rate

# Calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Calculate Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth):
    A = distance.euclidean(mouth[0], mouth[6])
    B = distance.euclidean(mouth[2], mouth[10])
    C = distance.euclidean(mouth[4], mouth[8])
    mar = (B + C) / (2.0 * A)
    return mar

# Alert function
def alert_user(message):
    print(message)
    engine.say(message)
    engine.runAndWait()
    time.sleep(0.5)  # pause to avoid cutting audio

# Initialize camera
cap = cv2.VideoCapture(0)

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")  # Update path

# Constants for thresholds
EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.52
DROWSINESS_FRAME_THRESH = 20  # number of consecutive frames eye closed
YAWN_ALERT_THRESHOLD = 5

# Counters and state
frame_counter = 0
alarm_on = False
yawn_counter = 0
yawn_alerted = False

# Timing for cooldowns
last_drowsiness_alert_time = 0
last_yawn_time = 0

# Cooldown durations in seconds to prevent spamming alerts
DROWSINESS_COOLDOWN = 10  # seconds
YAWN_COOLDOWN = 10        # seconds
YAWN_RESET_TIME = 60       # seconds without yawns to reset counter

# Colors
COLOR_ACTIVE = (0, 255, 0)
COLOR_WARNING = (0, 0, 255)

while True:
    ret, vid = cap.read()
    if not ret:
        break
    frame = cv2.flip(vid, 1)
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        
        leftEye = shape[42:48]
        rightEye = shape[36:42]
        mouth = shape[48:68]
        
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        mar = mouth_aspect_ratio(mouth)
        
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        mouthHull = cv2.convexHull(mouth)
        
        eye_color = COLOR_WARNING if ear < EYE_AR_THRESH else COLOR_ACTIVE
        mouth_color = COLOR_WARNING if mar > MOUTH_AR_THRESH else COLOR_ACTIVE
        
        cv2.drawContours(frame, [leftEyeHull], -1, eye_color, 1)
        cv2.drawContours(frame, [rightEyeHull], -1, eye_color, 1)
        cv2.drawContours(frame, [mouthHull], -1, mouth_color, 1)
        
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        current_time = time.time()

        # Drowsiness detection with cooldown and voice alert
        if ear < EYE_AR_THRESH:
            frame_counter += 1
            if frame_counter >= DROWSINESS_FRAME_THRESH:
                # Check cooldown
                if (current_time - last_drowsiness_alert_time) > DROWSINESS_COOLDOWN:
                    alert_user("WAKE UP")
                    last_drowsiness_alert_time = current_time
                    alarm_on = True
                
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WARNING, 2)
        else:
            frame_counter = 0
            alarm_on = False

        # Yawn detection with cooldown and counting
        if mar > MOUTH_AR_THRESH:
            cv2.putText(frame, "YAWN DETECTED!", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WARNING, 2)
            
            if (current_time - last_yawn_time) > YAWN_COOLDOWN:
                yawn_counter += 1
                last_yawn_time = current_time
                print(f"Yawn count: {yawn_counter}")
                
                if yawn_counter >= YAWN_ALERT_THRESHOLD and not yawn_alerted:
                    alert_user("Please take a rest for some time.")
                    yawn_alerted = True
        else:
            # Reset yawn counter and alert if no yawns for a while
            if (current_time - last_yawn_time) > YAWN_RESET_TIME:
                yawn_counter = 0
                yawn_alerted = False

    cv2.imshow("Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
