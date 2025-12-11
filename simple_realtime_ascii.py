#!/usr/bin/env python3
"""
Simple Real-Time ASCII Video Converter
Clean, simple version with camera window showing ASCII conversion
"""
import cv2
import numpy as np
import mediapipe as mp
import time

class SimpleRealtimeASCII:
    def __init__(self):
        # ASCII characters from darkest to lightest
        self.ascii_chars = "@%#*+=-:. "
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Settings
        self.brightness = 1.0
        self.show_hands = True
        self.show_ascii = True
        self.last_gesture = "Ready"
        
        # Gesture smoothing
        self.gesture_buffer = []
        
    def pixel_to_ascii(self, pixel_value):
        """Convert pixel to ASCII character"""
        ascii_index = int(pixel_value / 255 * (len(self.ascii_chars) - 1))
        return self.ascii_chars[ascii_index]
    
    def detect_simple_gesture(self, landmarks):
        """Simple gesture detection"""
        if not landmarks:
            return None
            
        # Get thumb and index positions
        thumb_tip_y = landmarks[4].y
        index_tip_y = landmarks[8].y
        
        # Simple detection: thumb vs index position
        if thumb_tip_y < index_tip_y - 0.1:
            return "brightness_up"
        elif thumb_tip_y > index_tip_y + 0.1:
            return "brightness_down"
        
        return None
    
    def create_ascii_overlay(self, frame):
        """Create ASCII art overlay on frame"""
        if not self.show_ascii:
            return frame
            
        # Create smaller ASCII version
        small_frame = cv2.resize(frame, (60, 20))
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # Apply brightness
        gray = cv2.convertScaleAbs(gray, alpha=self.brightness, beta=0)
        
        # Create overlay area
        overlay = frame.copy()
        start_x, start_y = 20, 50
        
        # Draw background
        cv2.rectangle(overlay, (start_x-10, start_y-10), 
                     (start_x + 480, start_y + 320), (0, 0, 0), -1)
        
        # Draw ASCII
        for y in range(20):
            ascii_line = ""
            for x in range(60):
                pixel = gray[y, x]
                ascii_line += self.pixel_to_ascii(pixel)
            
            # Draw the line
            cv2.putText(overlay, ascii_line, (start_x, start_y + y * 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        
        # Blend with original
        return cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)
    
    def run(self):
        """Main loop"""
        print("Simple Real-Time ASCII Video Converter")
        print("👍 Thumb above index = Brighter")
        print("👎 Thumb below index = Darker")
        print("Press 'q' to quit, 'a' to toggle ASCII, 'h' to toggle hands")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
            
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        last_gesture_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Hand detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Gesture control
            current_time = time.time()
            if current_time - last_gesture_time > 0.5:
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        gesture = self.detect_simple_gesture(hand_landmarks.landmark)
                        if gesture:
                            last_gesture_time = current_time
                            
                            if gesture == "brightness_up":
                                self.brightness = min(2.0, self.brightness + 0.2)
                                self.last_gesture = f"👍 Brighter: {self.brightness:.1f}"
                                print(f"👍 Brightness: {self.brightness:.1f}")
                            elif gesture == "brightness_down":
                                self.brightness = max(0.2, self.brightness - 0.2)
                                self.last_gesture = f"👎 Darker: {self.brightness:.1f}"
                                print(f"👎 Brightness: {self.brightness:.1f}")
            
            # Draw hand landmarks
            if self.show_hands and results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Add ASCII overlay
            if self.show_ascii:
                frame = self.create_ascii_overlay(frame)
            
            # Add status info
            cv2.rectangle(frame, (0, 0), (640, 40), (0, 0, 0), -1)
            status = f"Brightness: {self.brightness:.1f} | ASCII: {'ON' if self.show_ascii else 'OFF'} | {self.last_gesture}"
            cv2.putText(frame, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow('Real-Time ASCII Camera', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):
                self.show_ascii = not self.show_ascii
                print(f"ASCII: {'ON' if self.show_ascii else 'OFF'}")
            elif key == ord('h'):
                self.show_hands = not self.show_hands
                print(f"Hands: {'ON' if self.show_hands else 'OFF'}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("Done!")

if __name__ == "__main__":
    converter = SimpleRealtimeASCII()
    converter.run()