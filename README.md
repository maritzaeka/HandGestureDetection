# IoT Smart Payment Terminal – Hand Gesture Detection

This repository implements a hand gesture (open hand) detection system as part of an IoT-based smart payment terminal for visually impaired users.  
The system detects an emergency hand gesture using computer vision and publishes the result to IoT devices via MQTT, while also exposing a REST API for integration and testing.

---

## System Overview

The system is designed to support emergency assistance during payment transactions by detecting an open-hand gesture in real time.

Workflow:
1. Camera captures image frames
2. AI model detects hand gesture (open hand)
3. Detection result is sent via MQTT
4. ESP8266 reacts by controlling LED/relay
5. REST API provides external access for monitoring and testing

---

## Architecture

- ESP32-CAM for image capture
- Hand gesture detection using MediaPipe
- REST API built with FastAPI
- MQTT for communication between AI service and ESP8266
- ESP8266 for physical emergency indicators

---

## MQTT Message Logic

| Topic | Payload | Behavior |
|------|--------|---------|
| `TOPIC_WARN` | `HAND_OPEN` | Triggers emergency LED blinking |
| `TOPIC_SESSION` | `started` | LED ON |
| `TOPIC_SESSION` | other | LED OFF |

---

## Model Performance

- Accuracy: 91%
- Precision: 100%
- False negatives occur mainly due to motion blur, low lighting, or non-frontal hand positions

The system is optimized to avoid false emergency triggers.

---

## Requirements

- Python 3.9 or higher
- Virtual environment (recommended)

Python dependencies:
```bash
pip install mediapipe
pip install opencv-python
pip install fastapi
pip install uvicorn

How to Run the System
======================
Activate virtual environment:
venv\Scripts\activate

Run hand gesture detection:
python hand_open_detect.py

Start REST API server:
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

API Endpoints
=============
API documentation (Swagger):
http://127.0.0.1:8000/docs

Hand gesture detection endpoint:
http://127.0.0.1:8000/docs#/default/detect_hand_detect_hand_post
