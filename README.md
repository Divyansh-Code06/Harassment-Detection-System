# Harassment Detection System

This project implements a real-time **Harassment Detection System** using computer vision and pose estimation. The system captures live video from a webcam, analyzes human pose data with the **YOLOv8 Pose Estimation** model, and detects aggressive gestures (e.g., raised hands). When such behavior is detected, the system triggers an audible alarm and sends an email alert with details of the incident.

## Features

- **Real-Time Video Processing:** Captures live feed from your webcam.
- **Pose Estimation:** Uses YOLOv8 Pose to detect keypoints (e.g., wrists, shoulders).
- **Aggression Detection:** Analyzes keypoints to detect aggressive hand gestures.
- **Alert System:** 
  - **Alarm:** Plays an alarm sound.
  - **Email Notification:** Sends an email alert with the detection details.
- **User Interface:** Displays a live camera feed for continuous monitoring.
- **Threshold & Cooldown Logic:** Prevents multiple alerts from triggering too quickly.

## Requirements

- **Python 3.7+**
- **OpenCV**
- **YOLOv8 (Ultralytics package)**
- **SimpleAudio** (or another library for playing audio)
- **smtplib** (for sending email)
- **Numpy**
