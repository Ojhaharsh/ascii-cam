#!/usr/bin/env python3
"""
Debug hand detection to see what's happening
"""
import cv2
import mediapipe as mp
import time

class HandDetectionDebug:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Camera not found!")
            return
            
        print("Hand Detection Debug")
        print("Put your hand in front of camera")
        print("Press 'q' to quit")
        
        frame_count = 0
        detection_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Check if hands detected
            hands_detected = False
            if results.multi_hand_landmarks:
                hands_detected = True
                detection_count += 1
                
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Show landmark positions for debugging
                    landmarks = hand_landmarks.landmark
                    thumb_tip = landmarks[4]
                    thumb_ip = landmarks[3]
                    
                    # Draw some key points
                    h, w, c = frame.shape
                    thumb_tip_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                    thumb_ip_pos = (int(thumb_ip.x * w), int(thumb_ip.y * h))
                    
                    cv2.circle(frame, thumb_tip_pos, 10, (0, 255, 0), -1)  # Green for thumb tip
                    cv2.circle(frame, thumb_ip_pos, 8, (255, 0, 0), -1)    # Blue for thumb IP
            
            # Display detection status
            status_color = (0, 255, 0) if hands_detected else (0, 0, 255)
            status_text = "HAND DETECTED" if hands_detected else "NO HAND"
            
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(frame, f"Detections: {detection_count}", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            detection_rate = (detection_count / frame_count) * 100 if frame_count > 0 else 0
            cv2.putText(frame, f"Rate: {detection_rate:.1f}%", (10, 130),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Hand Detection Debug', frame)
            
            # Print to console every 30 frames
            if frame_count % 30 == 0:
                print(f"Frame {frame_count}: Detection rate {detection_rate:.1f}%")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\nFinal stats:")
        print(f"Total frames: {frame_count}")
        print(f"Hand detections: {detection_count}")
        print(f"Detection rate: {(detection_count/frame_count)*100:.1f}%")

if __name__ == "__main__":
    debugger = HandDetectionDebug()
    debugger.run()