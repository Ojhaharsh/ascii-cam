#!/usr/bin/env python3
"""
Quick gesture test with improved detection and visual feedback
"""
import cv2
import mediapipe as mp
import time

class QuickGestureTest:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.brightness = 1.0
        
        # Gesture smoothing
        self.gesture_buffer = []
        self.buffer_size = 5
        
    def detect_gesture(self, landmarks):
        """Improved gesture detection"""
        if not landmarks:
            return None
            
        # Get key positions
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
        
        # Check finger states
        thumb_up = thumb_tip_y < thumb_ip_y and thumb_tip_y < thumb_mcp_y
        thumb_down = thumb_tip_y > thumb_ip_y and thumb_tip_y > thumb_mcp_y
        
        other_fingers_down = (index_tip_y > index_pip_y and 
                            middle_tip_y > middle_pip_y and 
                            ring_tip_y > ring_pip_y and 
                            pinky_tip_y > pinky_pip_y)
        
        # Gesture detection
        if thumb_up and other_fingers_down:
            return "thumbs_up"
        elif thumb_down and other_fingers_down:
            return "thumbs_down"
        
        return None
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Camera not found!")
            return
            
        print("Quick Gesture Test - Hold gestures steady")
        print("👍 Thumbs up = Increase brightness")
        print("👎 Thumbs down = Decrease brightness")
        print("Press 'q' to quit")
        
        last_gesture_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            current_gesture = None
            current_time = time.time()
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Detect gesture
                    current_gesture = self.detect_gesture(hand_landmarks.landmark)
            
            # Add to buffer for smoothing
            self.gesture_buffer.append(current_gesture)
            if len(self.gesture_buffer) > self.buffer_size:
                self.gesture_buffer.pop(0)
            
            # Check for stable gesture
            stable_gesture = None
            if len(self.gesture_buffer) >= 3:
                recent = self.gesture_buffer[-3:]
                if all(g == recent[0] and g is not None for g in recent):
                    stable_gesture = recent[0]
            
            # Apply gesture with cooldown
            if stable_gesture and current_time - last_gesture_time > 1.0:
                if stable_gesture == "thumbs_up":
                    self.brightness = min(2.0, self.brightness + 0.2)
                    print(f"👍 THUMBS UP! Brightness: {self.brightness:.1f}")
                    last_gesture_time = current_time
                elif stable_gesture == "thumbs_down":
                    self.brightness = max(0.2, self.brightness - 0.2)
                    print(f"👎 THUMBS DOWN! Brightness: {self.brightness:.1f}")
                    last_gesture_time = current_time
            
            # Display info
            cv2.putText(frame, f"Brightness: {self.brightness:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if current_gesture:
                cv2.putText(frame, f"Raw: {current_gesture}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            if stable_gesture:
                cv2.putText(frame, f"Stable: {stable_gesture}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Show gesture buffer status
            buffer_status = [g for g in self.gesture_buffer if g is not None]
            if buffer_status:
                cv2.putText(frame, f"Buffer: {len(buffer_status)}/{self.buffer_size}", 
                           (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
            
            cv2.imshow('Quick Gesture Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tester = QuickGestureTest()
    tester.run()