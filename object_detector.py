import cv2
import numpy as np
import json
import os
from PIL import Image, ImageDraw, ImageFont
import uuid
from datetime import datetime

class ElectricalObjectDetector:
    """
    Object detection system for electrical components using OpenCV
    """
    
    def __init__(self):
        self.electrical_components = {
            'conduit': {
                'keywords': ['pipe', 'tube', 'conduit', 'emt'],
                'color': (255, 0, 0),  # Red
                'description': 'EMT Conduit or electrical piping'
            },
            'junction_box': {
                'keywords': ['box', 'outlet', 'receptacle', 'switch'],
                'color': (0, 255, 0),  # Green
                'description': 'Junction box or electrical outlet'
            },
            'panel': {
                'keywords': ['panel', 'board', 'breaker', 'electrical'],
                'color': (0, 0, 255),  # Blue
                'description': 'Electrical panel or breaker box'
            },
            'wire': {
                'keywords': ['wire', 'cable', 'conductor'],
                'color': (255, 255, 0),  # Yellow
                'description': 'Electrical wiring or cables'
            }
        }
    
    def detect_objects(self, image_path):
        """
        Detect electrical objects in an image using OpenCV
        Returns list of detected objects with bounding boxes
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # Convert to different color spaces for better detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        detected_objects = []
        
        # Detect rectangular shapes (common in electrical components)
        self._detect_rectangular_objects(image, gray, detected_objects)
        
        # Detect circular/cylindrical objects (conduit, pipes)
        self._detect_circular_objects(image, gray, detected_objects)
        
        # Detect metallic objects (panels, boxes)
        self._detect_metallic_objects(image, hsv, detected_objects)
        
        return detected_objects
    
    def _detect_rectangular_objects(self, image, gray, detected_objects):
        """Detect rectangular electrical components like panels and boxes"""
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular (4 corners)
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                area = cv2.contourArea(contour)
                
                # Filter based on size and aspect ratio
                if area > 1000 and 0.3 < aspect_ratio < 3.0:
                    # Classify based on aspect ratio and size
                    if aspect_ratio > 1.5:
                        component_type = 'panel'
                    else:
                        component_type = 'junction_box'
                    
                    detected_objects.append({
                        'type': component_type,
                        'confidence': 0.75,
                        'bbox': [x, y, w, h],
                        'area': area
                    })
    
    def _detect_circular_objects(self, image, gray, detected_objects):
        """Detect circular objects like conduit openings"""
        # Blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 50,
                                  param1=50, param2=30, minRadius=10, maxRadius=100)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # Filter based on radius
                if r > 15:
                    detected_objects.append({
                        'type': 'conduit',
                        'confidence': 0.70,
                        'bbox': [x-r, y-r, 2*r, 2*r],
                        'area': np.pi * r * r
                    })
    
    def _detect_metallic_objects(self, image, hsv, detected_objects):
        """Detect metallic surfaces common in electrical equipment"""
        # Define range for metallic/gray colors
        lower_metal = np.array([0, 0, 50])
        upper_metal = np.array([180, 50, 200])
        
        # Create mask for metallic colors
        mask = cv2.inRange(hsv, lower_metal, upper_metal)
        
        # Morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours in mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 2000:  # Filter small objects
                x, y, w, h = cv2.boundingRect(contour)
                detected_objects.append({
                    'type': 'panel',
                    'confidence': 0.65,
                    'bbox': [x, y, w, h],
                    'area': area
                })
    
    def draw_detections(self, image_path, detected_objects, output_path):
        """
        Draw bounding boxes on detected objects and save the result
        """
        # Load image with PIL for better text rendering
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        for obj in detected_objects:
            x, y, w, h = obj['bbox']
            obj_type = obj['type']
            confidence = obj['confidence']
            
            # Get color for this object type
            color = self.electrical_components.get(obj_type, {}).get('color', (255, 255, 255))
            
            # Draw bounding box
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            
            # Draw label
            label = f"{obj_type.replace('_', ' ').title()}: {confidence:.0%}"
            
            # Calculate text size and position
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw background rectangle for text
            draw.rectangle([x, y - text_height - 5, x + text_width + 10, y], fill=color)
            
            # Draw text
            draw.text((x + 5, y - text_height - 2), label, fill=(255, 255, 255), font=font)
        
        # Save the result
        image.save(output_path)
        return output_path
    
    def get_component_matches(self, detected_objects):
        """
        Match detected objects with electrical parts database
        """
        matches = []
        
        # Simple mapping for demonstration
        component_database = {
            'conduit': {
                'name': 'EMT Conduit',
                'part_numbers': ['EMT-34', 'EMT-12', 'EMT-1'],
                'vendor': 'Various',
                'description': 'Electrical Metallic Tubing for wire protection'
            },
            'junction_box': {
                'name': 'Junction Box',
                'part_numbers': ['JB-4SQ', 'JB-OCT', 'JB-RND'],
                'vendor': 'Various',
                'description': 'Electrical junction and outlet boxes'
            },
            'panel': {
                'name': 'Electrical Panel',
                'part_numbers': ['PNL-100A', 'PNL-200A', 'PNL-400A'],
                'vendor': 'Square D / Eaton',
                'description': 'Main electrical distribution panels and subpanels'
            },
            'wire': {
                'name': 'Electrical Wire',
                'part_numbers': ['THHN-12', 'THHN-14', 'THHN-10'],
                'vendor': 'Southwire',
                'description': 'THHN building wire for electrical circuits'
            }
        }
        
        for obj in detected_objects:
            obj_type = obj['type']
            if obj_type in component_database:
                component_info = component_database[obj_type].copy()
                component_info['detected_area'] = obj['area']
                component_info['confidence'] = obj['confidence']
                component_info['bbox'] = obj['bbox']
                matches.append(component_info)
        
        return matches
    
    def process_image(self, image_path, user_comment=""):
        """
        Complete processing pipeline: detect objects, draw boxes, match components
        """
        # Generate unique filename for processed image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"detected_{timestamp}_{unique_id}.jpg"
        output_path = os.path.join('static/detections', output_filename)
        
        # Detect objects
        detected_objects = self.detect_objects(image_path)
        
        # Draw detections on image
        if detected_objects:
            self.draw_detections(image_path, detected_objects, output_path)
        else:
            # Copy original image if no detections
            import shutil
            shutil.copy2(image_path, output_path)
        
        # Get component matches
        component_matches = self.get_component_matches(detected_objects)
        
        return {
            'detected_objects': detected_objects,
            'component_matches': component_matches,
            'processed_image_path': output_path,
            'detection_count': len(detected_objects)
        }