# config.py
# This file holds the configurable settings for our crowd density estimator.

# YOLOv8 model to use (yolov8n.pt is the 'nano' version, which is fast and good for live video)
MODEL_NAME = 'yolov8n.pt'

# Confidence threshold for detections. Higher means fewer false positives, but might miss some people.
CONFIDENCE_THRESHOLD = 0.3

# The class ID for 'person' in the COCO dataset (which YOLO is trained on) is 0.
PERSON_CLASS_ID = 0

# Risk Thresholds for Alerts (number of people)
RISK_LOW = 10
RISK_MEDIUM = 20
RISK_HIGH = 35
