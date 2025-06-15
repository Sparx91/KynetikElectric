"""
SMS notification service using Twilio for Kynetik Electric worker dispatch
"""
import os
from typing import Optional
from twilio.rest import Client


class SMSService:
    """
    SMS service for sending notifications to workers
    """
    
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def send_job_assignment_sms(self, worker_phone: str, job_title: str, location: str, job_id: str) -> bool:
        """
        Send SMS notification to worker about new job assignment
        
        Args:
            worker_phone: Worker's phone number
            job_title: Title of the assigned job
            location: Job location/address
            job_id: Unique job identifier
        
        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        if not self.client:
            print("Twilio credentials not configured - SMS not sent")
            return False
        
        try:
            message_body = (
                f"Kynetik Electric Dispatch: Job titled \"{job_title}\" "
                f"has been assigned to you at {location}. "
                f"Job ID: {job_id}. View in app."
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=worker_phone
            )
            
            print(f"SMS sent successfully. SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_job_update_sms(self, phone: str, job_title: str, status: str) -> bool:
        """
        Send SMS notification about job status update
        
        Args:
            phone: Phone number to send to
            job_title: Title of the job
            status: New status of the job
        
        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        if not self.client:
            print("Twilio credentials not configured - SMS not sent")
            return False
        
        try:
            message_body = (
                f"Kynetik Electric: Job \"{job_title}\" "
                f"status updated to: {status.upper()}"
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=phone
            )
            
            print(f"SMS sent successfully. SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False


# Global SMS service instance
sms_service = SMSService()