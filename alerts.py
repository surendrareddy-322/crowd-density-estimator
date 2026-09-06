import config
from datetime import datetime
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        
        # Simple cooldown: only alert once every 60 seconds to avoid SMS spam
        if self.last_alert_time is None or (now - self.last_alert_time).seconds > 60:
            print(f"⚠️ [ALERT] {now.strftime('%H:%M:%S')} - HIGH CROWD DENSITY DETECTED: {count} people in zone!")
            self.last_alert_time = now
            
            # Send SMS via Twilio
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            from_number = os.environ.get('TWILIO_FROM_NUMBER')
            to_number = os.environ.get('TWILIO_TO_NUMBER')
            
            if account_sid and auth_token and from_number and to_number and account_sid != 'your_account_sid_here':
                try:
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(
                        body=f"🚨 ALERT: High crowd density detected! {count} people in the monitoring zone.",
                        from_=from_number,
                        to=to_number
                    )
                    print(f"✅ SMS Alert sent successfully. SID: {message.sid}")
                except Exception as e:
                    print(f"❌ Failed to send SMS: {e}")
            else:
                print("ℹ️ Twilio credentials not fully configured in .env. Skipping SMS.")
