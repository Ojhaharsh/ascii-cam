#!/usr/bin/env python3
"""
Dual Window ASCII Video Converter
Shows camera feed in one window and ASCII art in another window side by side
"""
import cv2
import numpy as np
import mediapipe as mp
import time

class DualWindowASCII:
    def __init__(self):
        # ASCII characters from darkest to lightest
        self.ascii_chars = "@%#*+=-:. "
        
        # MediaPipe setup for hand detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Video settings
        self.ascii_width = 120
        self.ascii_height = 40
        self.brightness = 1.0
        self.contrast = 1.0
        self.show_hands = True
        self.last_gesture = "None"
        
        # Gesture smoothing
        self.gesture_buffer = []
        self.buffer_size = 3
        
        # Display settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def pixel_to_ascii(self, pixel_value):
        """Convert pixel brightness to ASCII character"""
        ascii_index = int(pixel_value / 255 * (len(self.ascii_chars) - 1))
        return self.ascii_chars[ascii_index]
    
    def frame_to_ascii_image(self, frame):
        """Convert frame to ASCII and return as image"""
        # Resize frame for ASCII conversion
        resized = cv2.resize(frame, (self.ascii_width, self.ascii_height))
        
        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Apply brightness and contrast
        gray = cv2.convertScaleAbs(gray, alpha=self.brightness * self.contrast, beta=0)
        
        # Create ASCII image
        char_width = 8
        char_height = 16
        ascii_img_width = self.ascii_width * char_width
        ascii_img_height = self.ascii_height * char_height
        
        # Create black background
        ascii_img = np.zeros((ascii_img_height, ascii_img_width, 3), dtype=np.uint8)
        
        # Draw ASCII characters
        for y in range(self.ascii_height):
            for x in range(self.ascii_width):
                pixel_value = gray[y, x]
                ascii_char = self.pixel_to_ascii(pixel_value)
                
                # Position for character
                char_x = x * char_width
                char_y = (y + 1) * char_height - 4
                
                # Color based on brightness (darker = white text, lighter = gray text)
                color_intensity = int(255 - pixel_value)
                color = (color_intensity, color_intensity, color_intensity)
                
                # Draw character
                cv2.putText(ascii_img, ascii_char, (char_x, char_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return ascii_img
    
    def detect_gestures(self, results):
        """Detect hand gestures with smoothing"""
        current_gesture = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                
                # Get key landmark positions
                thumb_tip_y = landmarks[4].y
                thumb_ip_y = landmarks[3].y
                thumb_mcp_y = landmarks[2].y
                
                index_tip_y = landmarks[8].y
                index_pip_y = landmarks[6].y
                middle_tip_y = landmarks[12].y
                middle_pip_y = landmarks[10].y
                ring_tip_y = landmarks[16].y
                ring_pip_y = landmarks[14].y
                pinky_tip_y = landmarks[20].y
                pinky_pip_y = landmarks[18].y
                
                # Improved thumbs up detection
                thumb_extended_up = thumb_tip_y < thumb_ip_y and thumb_tip_y < thumb_mcp_y
                other_fingers_down = (index_tip_y > index_pip_y and 
                                    middle_tip_y > middle_pip_y and 
                                    ring_tip_y > ring_pip_y and 
                                    pinky_tip_y > pinky_pip_y)
                
                if thumb_extended_up and other_fingers_down:
                    current_gesture = "brightness_up"
                
                # Improved thumbs down detection
                thumb_extended_down = thumb_tip_y > thumb_ip_y and thumb_tip_y > thumb_mcp_y
                
                if thumb_extended_down and other_fingers_down:
                    current_gesture = "brightness_down"
                
                # Peace sign: index and middle up, others down
                peace_fingers = (index_tip_y < index_pip_y and 
                               middle_tip_y < middle_pip_y and 
                               ring_tip_y > ring_pip_y and 
                               pinky_tip_y > pinky_pip_y)
                
                if peace_fingers:
                    current_gesture = "toggle_hands"
                
                # Fist: all fingers down
                all_fingers_down = (thumb_tip_y > thumb_ip_y and
                                  index_tip_y > index_pip_y and 
                                  middle_tip_y > middle_pip_y and 
                                  ring_tip_y > ring_pip_y and 
                                  pinky_tip_y > pinky_pip_y)
                
                if all_fingers_down:
                    current_gesture = "reset"
        
        # Add to gesture buffer for smoothing
        self.gesture_buffer.append(current_gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        
        # Return gesture only if it's consistent across multiple frames
        if len(self.gesture_buffer) >= 2:
            recent_gestures = self.gesture_buffer[-2:]
            if all(g == recent_gestures[0] and g is not None for g in recent_gestures):
                return recent_gestures[0]
        
        return None
    
    def draw_ui(self, frame):
        """Draw UI elements on camera frame"""
        height, width = frame.shape[:2]
        
        # Status bar background
        cv2.rectangle(frame, (0, 0), (width, 60), (0, 0, 0), -1)
        
        # Status text
        status_text = f"Brightness: {self.brightness:.1f} | Hands: {'ON' if self.show_hands else 'OFF'}"
        cv2.putText(frame, status_text, (10, 25), self.font, 0.6, (255, 255, 255), 2)
        
        # Last gesture
        cv2.putText(frame, f"Last: {self.last_gesture}", (10, 45), 
                   self.font, 0.5, (0, 255, 255), 1)
        
        # Instructions at bottom
        instructions = "Thumbs Up/Down = Brightness | Peace = Toggle Hands | Fist = Reset | 'q' = Quit"
        cv2.putText(frame, instructions, (10, height - 10), 
                   self.font, 0.4, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main loop for dual window ASCII video conversion"""
        print("Dual Window ASCII Video Converter")
        print("👍 Thumbs up = Increase brightness")
        print("👎 Thumbs down = Decrease brightness") 
        print("✌️ Peace sign = Toggle hand landmarks")
        print("✊ Fist = Reset settings")
        print("Press 'q' to quit")
        print("Starting camera...")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        last_gesture_time = 0
        gesture_cooldown = 0.5
        
        print("Camera started! Two windows will open - Camera and ASCII Art")
        
        # Position windows side by side
        cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
        cv2.namedWindow('ASCII Art', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Camera Feed', 100, 100)
        cv2.moveWindow('ASCII Art', 750, 100)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Hand detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Update last gesture status
            if results.multi_hand_landmarks:
                if "No hand" in self.last_gesture:
                    self.last_gesture = "Hand detected - try gestures!"
            else:
                if "Hand detected" in self.last_gesture:
                    self.last_gesture = "No hand detected"
            
            # Gesture control with cooldown
            current_time = time.time()
            if current_time - last_gesture_time > gesture_cooldown:
                gesture = self.detect_gestures(results)
                if gesture:
                    last_gesture_time = current_time
                    
                    if gesture == "brightness_up":
                        self.brightness = min(2.0, self.brightness + 0.2)
                        self.last_gesture = f"👍 THUMBS UP! Brightness: {self.brightness:.1f}"
                        print(f"👍 THUMBS UP! Brightness: {self.brightness:.1f}")
                    elif gesture == "brightness_down":
                        self.brightness = max(0.2, self.brightness - 0.2)
                        self.last_gesture = f"👎 THUMBS DOWN! Brightness: {self.brightness:.1f}"
                        print(f"👎 THUMBS DOWN! Brightness: {self.brightness:.1f}")
                    elif gesture == "toggle_hands":
                        self.show_hands = not self.show_hands
                        self.last_gesture = f"✌️ PEACE SIGN! Hands: {'ON' if self.show_hands else 'OFF'}"
                        print(f"✌️ PEACE SIGN! Hands: {'ON' if self.show_hands else 'OFF'}")
                    elif gesture == "reset":
                        self.brightness = 1.0
                        self.contrast = 1.0
                        self.last_gesture = "✊ FIST! Settings reset!"
                        print("✊ FIST! Settings reset!")
            
            # Draw hand landmarks if enabled
            camera_frame = frame.copy()
            if self.show_hands and results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(camera_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Add UI to camera frame
            camera_frame = self.draw_ui(camera_frame)
            
            # Generate ASCII art
            ascii_img = self.frame_to_ascii_image(frame)
            
            # Add title to ASCII window
            cv2.putText(ascii_img, f"ASCII Art - Brightness: {self.brightness:.1f}", 
                       (10, 25), self.font, 0.6, (255, 255, 255), 2)
            
            # Show both windows
            cv2.imshow('Camera Feed', camera_frame)
            cv2.imshow('ASCII Art', ascii_img)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("Camera closed. Goodbye!")

if __name__ == "__main__":
    converter = DualWindowASCII()
    converter.run()