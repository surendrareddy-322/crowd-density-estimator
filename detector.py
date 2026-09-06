import cv2
import numpy as np
from ultralytics import YOLO
import config
from alerts import AlertSystem

class CrowdDetector:
    def __init__(self):
        # Load the YOLOv8 model
        self.model = YOLO(config.MODEL_NAME)
        # Initialize the alert system from Phase 3
        self.alert_system = AlertSystem()
        
        # Define a Region of Interest (ROI) Zone. 
        # This is a polygon (x, y coordinates). Only people inside this zone are counted.
        # For this example, we'll define a generic large box, but in a real app, 
        # the user could draw this on the Streamlit dashboard!
        self.zone_polygon = np.array([[100, 100], [800, 100], [800, 600], [100, 600]], np.int32)
        
    def process_frame(self, frame):
        """
        Phase 3 logic: Detect people, but only count them if they are inside the Zone.
        Check the count against thresholds and trigger alerts.
        """
        # Run YOLOv8
        results = self.model(frame, classes=[config.PERSON_CLASS_ID], conf=config.CONFIDENCE_THRESHOLD, verbose=False)
        
        person_count = 0
        annotated_frame = frame.copy()
        
        # 1. Draw the Zone polygon on the frame
        # We reshape it to match OpenCV's required format for polylines
        cv2.polylines(annotated_frame, [self.zone_polygon.reshape((-1, 1, 2))], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.putText(annotated_frame, "Monitoring Zone", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Process detections
        total_detected = 0
        for r in results:
            boxes = r.boxes
            total_detected += len(boxes)
            for box in boxes:
                # Get the bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # 2. Calculate the center bottom of the bounding box (where the person's feet are)
                center_x = (x1 + x2) // 2
                bottom_y = y2
                
                # 3. Check if this point is inside our zone polygon
                # measureDist=False means it just returns 1 (inside), -1 (outside), or 0 (on edge)
                is_inside = cv2.pointPolygonTest(self.zone_polygon, (center_x, bottom_y), False)
                
                if is_inside >= 0:
                    # Person is inside the zone!
                    person_count += 1
                    
                    # Draw a bounding box for people *inside* the zone (we will color it dynamically later)
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Draw a small dot at their feet
                    cv2.circle(annotated_frame, (center_x, bottom_y), 5, (0, 255, 0), -1)
                else:
                    # Optional: Draw people outside the zone in grey, so we know they were detected but ignored
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (150, 150, 150), 1)

        # 4. Check thresholds using our AlertSystem
        risk_level, color = self.alert_system.check_thresholds(person_count)
        
        # 5. Display the counts and risk level on the frame
        cv2.putText(annotated_frame, f"Total Detected: {total_detected}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Zone Count: {person_count}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(annotated_frame, f"Status: {risk_level}", (20, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
        return annotated_frame, person_count, risk_level, total_detected

    def process_video(self, video_path=None, use_webcam=False, output_path=None):
        """
        Modified to support either a video file or a live webcam.
        """
        # If use_webcam is True, we open device 0 (your laptop's built-in camera)
        cap = cv2.VideoCapture(0 if use_webcam else video_path)
        
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0: fps = 30 # Fallback for webcams
        
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
        print("Starting video processing. Press 'q' on the video window to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Resize frame for consistency if it's too large (optional but good for performance)
            frame = cv2.resize(frame, (1024, 768))
            
            # Phase 3: Now returns the risk level too
            annotated_frame, count, risk = self.process_frame(frame)
            
            cv2.imshow("Crowd Density Estimator - Phase 3", annotated_frame)
            
            if out:
                out.write(annotated_frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        print("Video processing complete.")

if __name__ == "__main__":
    detector = CrowdDetector()
    print("Testing webcam processing for Phase 3...")
    # Passing use_webcam=True will turn on your laptop's camera!
    detector.process_video(use_webcam=True)
