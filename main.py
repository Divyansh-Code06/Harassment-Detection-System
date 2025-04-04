import cv2
import time
import smtplib
import numpy as np
import os
import simpleaudio as sa  
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ultralytics import YOLO  # YOLO Pose Estimation

# Paths
alarm_sound = r"D:\presentation\alarm.wav"  #   Alarm sound


if not os.path.exists(alarm_sound):
    print(" Error: Alarm sound not found. Check path!")
    exit()

# Load YOLO Pose Model
model = YOLO("yolov8n-pose.pt")  # Using YOLOv8 Pose model

# Email function
def send_email(detected_location, event_type):
    sender_email = "paramsingh1810@gmail.com"
    receiver_email = "harshitthakur2325@gmail.com"
    password = "nnid fwzo iloq ycmo"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["hassasment has been detected near khare's kitchen"] = f"🚨 Alert: {event_type}"

    body = f"🚨 Harassment detected at {detected_location}."
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(" Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Alarm function
def ring_alarm():
    print(" ALARM: Harassment detected!")
    try:
        wave_obj = sa.WaveObject.from_wave_file(alarm_sound)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound finishes
    except Exception as e:
        print(f"❌ Error playing alarm: {e}")

# Set up camera
cap = cv2.VideoCapture(0)

# Harassment detection parameters
harassment_detected = False
frame_threshold = 5  # Faster detection
aggressive_frames = 0  # Counter for aggressive behavior frames
last_alarm_time = 0  # Timestamp to prevent repeated alarms
last_aggression_time = 0  # Track last detected aggression frame
CONFIDENCE_THRESHOLD = 0.4  #  Reduced from 0.5 to detect more hands
COOLDOWN_TIME = 5  #  Reduced from 10 to allow faster retrigger
AGGRESSION_HOLD_TIME = 2.5 #  Reduced from 3 for faster detection
HAND_RAISE_THRESHOLD = 20  #  Reduced from 50 to allow more flexibility

print(" Monitoring harassment. Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(" Error accessing camera")
        break

    # Run YOLO Pose Detection
    results = model(frame)

    # Check for aggressive gestures
    aggression_detected = False

    for result in results:
        if result.keypoints is None or len(result.keypoints.xy) == 0:
            continue  # Skip if no person detected

        keypoints = result.keypoints.xy.cpu().numpy()  # Get pose keypoints
        confidences = result.keypoints.conf.cpu().numpy()  # Confidence scores

        for person, confidence in zip(keypoints, confidences):
            if len(person) < 11:
                continue  # Ensure valid keypoints

            
            print(f" Left Wrist: {person[9]}, Right Wrist: {person[10]}")
            print(f" Left Shoulder: {person[5]}, Right Shoulder: {person[6]}")
            print(f" Confidence Scores: Left Wrist={confidence[9]}, Right Wrist={confidence[10]}")

            left_shoulder, right_shoulder = person[5], person[6]
            left_wrist, right_wrist = person[9], person[10]

            # **NEW: Ensure hand is raised significantly**
            if (confidence[9] >= CONFIDENCE_THRESHOLD and left_wrist[1] < left_shoulder[1] - HAND_RAISE_THRESHOLD) or \
               (confidence[10] >= CONFIDENCE_THRESHOLD and right_wrist[1] < right_shoulder[1] - HAND_RAISE_THRESHOLD):
                aggression_detected = True
                last_aggression_time = time.time()  # Track last time aggression was seen

    # If aggression is detected, increase counter
    if aggression_detected:
        aggressive_frames += 1
    else:
        aggressive_frames = 0  # Reset if no aggression detected

    #  Trigger alarm if aggression is detected for AGGRESSION_HOLD_TIME frames
    if aggressive_frames >= AGGRESSION_HOLD_TIME and not harassment_detected:
        current_time = time.time()
        
        # Prevent multiple alarms (Only trigger every COOLDOWN_TIME seconds)
        if current_time - last_alarm_time >= COOLDOWN_TIME:  
            detected_location = "Latitude: 12.34, Longitude: 56.78"  # Mock location
            ring_alarm()
            send_email(detected_location, "Harassment Detected")
            last_alarm_time = current_time  # Update last alarm timestamp
            harassment_detected = True  
            aggressive_frames = 0  # Reset after triggering

    # Reset harassment detection **only if no aggression for COOLDOWN_TIME seconds**
    if harassment_detected and time.time() - last_aggression_time >= COOLDOWN_TIME:
        harassment_detected = False  # Allow re-triggering after cooldown

    # Display camera feed
    cv2.imshow("Camera Feed", frame)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print(" Monitoring stopped.")
        break

cap.release()
cv2.destroyAllWindows()
