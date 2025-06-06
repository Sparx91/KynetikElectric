"""
YOLOv8-style object detection module for Kynetik Electric
Uses OpenCV-based detection optimized for electrical components
"""
import cv2
import numpy as np
import os
from typing import List, Dict, Tuple
import json

class ElectricalYOLODetector:
    """
    Advanced object detection system mimicking YOLOv8 functionality
    Specialized for electrical components and industrial equipment
    """
    
    def __init__(self):
        self.confidence_threshold = 0.3
        self.nms_threshold = 0.4
        
        # Electrical component classes (YOLOv8-style class mapping)
        self.classes = [
            'electrical_panel', 'junction_box', 'conduit', 'outlet', 'switch',
            'breaker', 'transformer', 'meter', 'receptacle', 'wire', 'cable',
            'conduit_body', 'disconnect', 'motor', 'light_fixture'
        ]
        
        # Detection confidence scores for different component types
        self.class_weights = {
            'electrical_panel': 0.9,
            'junction_box': 0.8,
            'conduit': 0.7,
            'outlet': 0.8,
            'switch': 0.8,
            'breaker': 0.9,
            'transformer': 0.9,
            'meter': 0.9,
            'receptacle': 0.8,
            'wire': 0.6,
            'cable': 0.6,
            'conduit_body': 0.7,
            'disconnect': 0.8,
            'motor': 0.9,
            'light_fixture': 0.7
        }

    def detect_objects(self, image_path: str) -> List[str]:
        """
        YOLOv8-style object detection function
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            List[str]: List of detected object names
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Get detections using advanced computer vision
            detections = self._perform_detection(image)
            
            # Extract object names
            detected_objects = [detection['class'] for detection in detections]
            
            # Remove duplicates while preserving order
            unique_objects = []
            for obj in detected_objects:
                if obj not in unique_objects:
                    unique_objects.append(obj)
            
            return unique_objects
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def detect_objects_with_confidence(self, image_path: str) -> List[Dict]:
        """
        Enhanced detection with confidence scores and bounding boxes
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            List[Dict]: List of detection dictionaries with class, confidence, bbox
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            return self._perform_detection(image)
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def _perform_detection(self, image: np.ndarray) -> List[Dict]:
        """
        Advanced computer vision detection pipeline
        """
        detections = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Electrical panel detection
        detections.extend(self._detect_panels(image, gray))
        
        # Junction box detection
        detections.extend(self._detect_junction_boxes(image, gray))
        
        # Conduit detection
        detections.extend(self._detect_conduits(image, gray))
        
        # Outlet/receptacle detection
        detections.extend(self._detect_outlets(image, gray))
        
        # Switch detection
        detections.extend(self._detect_switches(image, gray))
        
        # Wire/cable detection
        detections.extend(self._detect_wires(image, hsv))
        
        # Metallic component detection
        detections.extend(self._detect_metallic_components(image, hsv))
        
        return self._apply_nms(detections)

    def _detect_panels(self, image: np.ndarray, gray: np.ndarray) -> List[Dict]:
        """Detect electrical panels and distribution boards"""
        detections = []
        
        # Large rectangular detection for panels
        contours, _ = cv2.findContours(
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Large components
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.5 < aspect_ratio < 2.0:  # Panel-like proportions
                    confidence = min(0.9, area / 10000)
                    detections.append({
                        'class': 'electrical_panel',
                        'confidence': confidence,
                        'bbox': [x, y, w, h]
                    })
        
        return detections

    def _detect_junction_boxes(self, image: np.ndarray, gray: np.ndarray) -> List[Dict]:
        """Detect junction boxes and outlet boxes"""
        detections = []
        
        # Square/rectangular detection for boxes
        contours, _ = cv2.findContours(
            cv2.Canny(gray, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Medium-sized components
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.7 < aspect_ratio < 1.4:  # Box-like proportions
                    confidence = 0.8
                    detections.append({
                        'class': 'junction_box',
                        'confidence': confidence,
                        'bbox': [x, y, w, h]
                    })
        
        return detections

    def _detect_conduits(self, image: np.ndarray, gray: np.ndarray) -> List[Dict]:
        """Detect EMT conduit and piping"""
        detections = []
        
        # Line detection for conduits
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                
                if length > 100:  # Long enough to be conduit
                    confidence = 0.7
                    x, y, w, h = min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1)
                    detections.append({
                        'class': 'conduit',
                        'confidence': confidence,
                        'bbox': [x, y, max(w, 20), max(h, 20)]
                    })
        
        return detections

    def _detect_outlets(self, image: np.ndarray, gray: np.ndarray) -> List[Dict]:
        """Detect electrical outlets and receptacles"""
        detections = []
        
        # Circle detection for outlets
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                  param1=50, param2=30, minRadius=10, maxRadius=50)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                confidence = 0.8
                detections.append({
                    'class': 'outlet',
                    'confidence': confidence,
                    'bbox': [x-r, y-r, 2*r, 2*r]
                })
        
        return detections

    def _detect_switches(self, image: np.ndarray, gray: np.ndarray) -> List[Dict]:
        """Detect electrical switches"""
        detections = []
        
        # Small rectangular detection for switches
        contours, _ = cv2.findContours(
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 1000:  # Small components
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.8 < aspect_ratio < 1.2:  # Square-like proportions
                    confidence = 0.8
                    detections.append({
                        'class': 'switch',
                        'confidence': confidence,
                        'bbox': [x, y, w, h]
                    })
        
        return detections

    def _detect_wires(self, image: np.ndarray, hsv: np.ndarray) -> List[Dict]:
        """Detect electrical wires and cables"""
        detections = []
        
        # Color-based detection for copper/colored wires
        wire_colors = [
            ([0, 50, 50], [10, 255, 255]),    # Red wires
            ([110, 50, 50], [130, 255, 255]), # Blue wires
            ([40, 50, 50], [80, 255, 255]),   # Green wires
        ]
        
        for lower, upper in wire_colors:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    confidence = 0.6
                    detections.append({
                        'class': 'wire',
                        'confidence': confidence,
                        'bbox': [x, y, w, h]
                    })
        
        return detections

    def _detect_metallic_components(self, image: np.ndarray, hsv: np.ndarray) -> List[Dict]:
        """Detect metallic electrical components"""
        detections = []
        
        # Metallic surface detection (gray/silver colors)
        lower_metal = np.array([0, 0, 50])
        upper_metal = np.array([180, 30, 200])
        mask = cv2.inRange(hsv, lower_metal, upper_metal)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                confidence = 0.7
                detections.append({
                    'class': 'conduit_body',
                    'confidence': confidence,
                    'bbox': [x, y, w, h]
                })
        
        return detections

    def _apply_nms(self, detections: List[Dict]) -> List[Dict]:
        """Apply Non-Maximum Suppression to remove duplicate detections"""
        if not detections:
            return []
        
        # Convert to format required for NMS
        boxes = []
        scores = []
        class_ids = []
        
        for i, detection in enumerate(detections):
            x, y, w, h = detection['bbox']
            boxes.append([x, y, x + w, y + h])
            scores.append(detection['confidence'])
            class_ids.append(i)
        
        boxes = np.array(boxes, dtype=np.float32)
        scores = np.array(scores, dtype=np.float32)
        
        if len(boxes) == 0:
            return []
        
        # Apply OpenCV NMS
        try:
            indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), self.confidence_threshold, self.nms_threshold)
            
            if isinstance(indices, tuple) and len(indices) == 0:
                return []
            if not isinstance(indices, (list, tuple)) or len(indices) == 0:
                return []
            
            # Return filtered detections
            filtered_detections = []
            if isinstance(indices, np.ndarray):
                indices = indices.flatten()
            
            for i in indices:
                if isinstance(i, (list, tuple)):
                    i = i[0]
                filtered_detections.append(detections[i])
        except Exception:
            # If NMS fails, return original detections
            return detections
        
        return filtered_detections

    def get_component_matches(self, detected_objects: List[str]) -> List[Dict]:
        """
        Match detected objects with electrical parts database
        
        Args:
            detected_objects (List[str]): List of detected object names
            
        Returns:
            List[Dict]: List of component matches with part information
        """
        from models import ElectricalPart
        
        matches = []
        for obj in detected_objects:
            # Find matching parts in database
            parts = ElectricalPart.query.filter(
                ElectricalPart.detection_labels.contains(obj.lower())
            ).all()
            
            for part in parts:
                matches.append({
                    'name': part.name,
                    'part_number': part.part_number,
                    'vendor': part.vendor,
                    'description': part.description,
                    'category': part.category
                })
        
        return matches

    def save_detection_image(self, image_path: str, output_path: str) -> bool:
        """
        Save image with detection bounding boxes drawn
        
        Args:
            image_path (str): Input image path
            output_path (str): Output image path
            
        Returns:
            bool: Success status
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            detections = self._perform_detection(image)
            
            # Draw bounding boxes
            for detection in detections:
                x, y, w, h = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['class']
                
                # Draw rectangle
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(image, (x, y - label_size[1] - 10), (x + label_size[0], y), (0, 255, 0), -1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # Save result
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error saving detection image: {e}")
            return False

def detect_objects(image_path: str) -> List[str]:
    """
    Main detection function for compatibility with existing code
    
    Args:
        image_path (str): Path to the input image
        
    Returns:
        List[str]: List of detected object names
    """
    detector = ElectricalYOLODetector()
    return detector.detect_objects(image_path)

def toolie_summarize(items: List[str]) -> str:
    """
    Future-ready function for Toolie AI integration
    
    Args:
        items (List[str]): List of detected electrical components
        
    Returns:
        str: AI-generated summary of detected components
    """
    if not items:
        return "No electrical components detected in the image."
    
    # Placeholder implementation - will be enhanced with Toolie AI
    component_count = len(items)
    unique_items = list(set(items))
    
    summary = f"Detected {component_count} electrical components: {', '.join(unique_items)}. "
    
    # Add professional assessment
    if 'electrical_panel' in items:
        summary += "Main electrical distribution equipment identified. "
    if 'junction_box' in items:
        summary += "Junction boxes present for wire connections. "
    if 'conduit' in items:
        summary += "Conduit system detected for wire protection. "
    if 'outlet' in items or 'receptacle' in items:
        summary += "Power outlets available for equipment connection. "
    
    summary += "Professional electrical assessment recommended for detailed analysis and quote preparation."
    
    return summary