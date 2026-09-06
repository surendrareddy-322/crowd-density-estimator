import config
from datetime import datetime

class AlertSystem:
    def __init__(self):
        # Keep track of the last alert time to avoid spamming alerts every frame
        self.last_alert_time = None
        
    def check_thresholds(self, count):
        """
        Takes the current crowd count and returns the risk level (String)
        and an associated color for the bounding boxes/text.
        """
        risk_level = "NORMAL"
        color = (0, 255, 0) # Green for normal in OpenCV (BGR format)
        
        if count >= config.RISK_HIGH:
            risk_level = "HIGH RISK"
            color = (0, 0, 255) # Red
            self.trigger_alert(count)
        elif count >= config.RISK_MEDIUM:
            risk_level = "MEDIUM RISK"
            color = (0, 165, 255) # Orange 
        elif count >= config.RISK_LOW:
            risk_level = "LOW RISK"
            color = (0, 255, 255) # Yellow
            
        return risk_level, color
        
    def trigger_alert(self, count):
        """
        In a production environment, this would send an SMS or Email.
        For now, we simply print a visible warning to the console.
        """
        now = datetime.now()
        
        # Simple cooldown: only alert once every 10 seconds to avoid spam
        if self.last_alert_time is None or (now - self.last_alert_time).seconds > 10:
            print(f"⚠️ [ALERT] {now.strftime('%H:%M:%S')} - HIGH CROWD DENSITY DETECTED: {count} people in zone!")
            self.last_alert_time = now
            
        # Optional: Add Twilio (SMS) or SMTP (Email) integration here later
