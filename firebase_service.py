"""
Firebase service integration for Kynetik Electric worker dispatch system
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class FirebaseService:
    """
    Firebase service for managing workers, service calls, and file uploads
    """
    
    def __init__(self):
        self.project_id = os.environ.get('FIREBASE_PROJECT_ID')
        self.api_key = os.environ.get('FIREBASE_API_KEY')
        self.app_id = os.environ.get('FIREBASE_APP_ID')
        
        # Mock data for development - replace with actual Firebase integration
        self.workers = [
            {
                'id': 'worker1',
                'name': 'Mike Rodriguez',
                'email': 'mike@kynetikelectric.com',
                'phone': '+15551234567',
                'role': 'technician',
                'active': True
            },
            {
                'id': 'worker2', 
                'name': 'Sarah Johnson',
                'email': 'sarah@kynetikelectric.com',
                'phone': '+15551234568',
                'role': 'senior_technician',
                'active': True
            }
        ]
        
        self.service_calls = []
        self.uploads = []
    
    def get_firebase_config(self):
        """Get Firebase configuration for client-side initialization"""
        return {
            'apiKey': self.api_key,
            'authDomain': f"{self.project_id}.firebaseapp.com",
            'projectId': self.project_id,
            'storageBucket': f"{self.project_id}.firebasestorage.app",
            'appId': self.app_id
        }
    
    def get_workers(self) -> List[Dict]:
        """Get all active workers"""
        return [w for w in self.workers if w['active']]
    
    def get_worker_by_id(self, worker_id: str) -> Optional[Dict]:
        """Get worker by ID"""
        return next((w for w in self.workers if w['id'] == worker_id), None)
    
    def create_service_call(self, data: Dict) -> str:
        """Create a new service call"""
        call_id = f"call_{len(self.service_calls) + 1}_{int(datetime.now().timestamp())}"
        
        service_call = {
            'id': call_id,
            'title': data.get('title'),
            'customer_name': data.get('customer_name'),
            'location': data.get('location'),
            'description': data.get('description'),
            'priority': data.get('priority', 'medium'),
            'assigned_to': data.get('assigned_to'),
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'notes': [],
            'attachments': []
        }
        
        self.service_calls.append(service_call)
        return call_id
    
    def get_service_calls(self, worker_id: str = None) -> List[Dict]:
        """Get service calls, optionally filtered by worker"""
        if worker_id:
            return [call for call in self.service_calls if call['assigned_to'] == worker_id]
        return self.service_calls
    
    def update_service_call_status(self, call_id: str, status: str, notes: str = None) -> bool:
        """Update service call status"""
        for call in self.service_calls:
            if call['id'] == call_id:
                call['status'] = status
                call['updated_at'] = datetime.now().isoformat()
                if notes:
                    call['notes'].append({
                        'note': notes,
                        'timestamp': datetime.now().isoformat()
                    })
                return True
        return False
    
    def upload_file(self, call_id: str, file_data: Dict) -> str:
        """Upload file to Firebase Storage (mock implementation)"""
        upload_id = f"upload_{len(self.uploads) + 1}_{int(datetime.now().timestamp())}"
        
        upload = {
            'id': upload_id,
            'call_id': call_id,
            'filename': file_data.get('filename'),
            'file_path': file_data.get('file_path'),
            'file_type': file_data.get('file_type'),
            'uploaded_by': file_data.get('uploaded_by'),
            'note': file_data.get('note', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        self.uploads.append(upload)
        
        # Add to service call attachments
        for call in self.service_calls:
            if call['id'] == call_id:
                call['attachments'].append(upload_id)
                break
        
        return upload_id
    
    def get_uploads_for_call(self, call_id: str) -> List[Dict]:
        """Get all uploads for a service call"""
        return [upload for upload in self.uploads if upload['call_id'] == call_id]


# Global Firebase service instance
firebase_service = FirebaseService()