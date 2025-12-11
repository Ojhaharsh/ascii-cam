import cv2
import mediapipe as mp
import time

class SimpleGestureControl:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.brightness = 1.0
        
    def is_thumb_up(self, landmarks):
        """Simple thumbs up detection"""
        # Thumb tip (4) should be above thumb IP (3) and above wrist (0)
        thumb_tip_y = landmarks[4].y
        thumb_ip_y = landmarks[3].y
        wrist_y = landmarks[0].y
        
        # Index finger should be down (tip below PIP)
        index_tip_y = landmarks[8].y
        index_pip_y = landmarks[6].y
        
        return (thumb_tip_y < thumb_ip_y and 
                thumb_tip_y < wrist_y and 
                index_tip_y > index_pip_y)
    
    def is_thumb_down(self, landmarks):
        """Simple thumbs down detection"""
        # Thumb tip (4) should be below thumb IP (3) and below wrist (0)
        thumb_tip_y = landmarks[4].y
        thumb_ip_y = landmarks[3].y
        wrist_y = landmarks[0].y
        
        # Index finger should be down (tip below PIP)
        index_tip_y = landmarks[8].y
        index_pip_y = landmarks[6].y
        
        return (thumb_tip_y > thumb_ip_y and 
                thumb_tip_y > wrist_y and 
                index_tip_y > index_pip_y)
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Camera not found!")
            return
            
        print("Gesture Control Test")
        print("Show thumbs up/down to control brightness")
        print("Press 'q' to quit")
        
        last_gesture_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gesture_detected = False
            current_time = time.time()
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Check gestures with cooldown
                    if current_time - last_gesture_time > 1.0:
                        if self.is_thumb_up(hand_landmarks.landmark):
                            self.brightness = min(2.0, self.brightness + 0.2)
                            print(f"👍 THUMBS UP! Brightness: {self.brightness:.1f}")
                            last_gesture_time = current_time
                            gesture_detected = True
                            
                        elif self.is_thumb_down(hand_landmarks.landmark):
                            self.brightness = max(0.2, self.brightness - 0.2)
                            print(f"👎 THUMBS DOWN! Brightness: {self.brightness:.1f}")
                            last_gesture_time = current_time
                            gesture_detected = True
            
            # Display current brightness on frame
            cv2.putText(frame, f"Brightness: {self.brightness:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if gesture_detected:
                cv2.putText(frame, "GESTURE DETECTED!", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('Gesture Control', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = SimpleGestureControl()
    controller.run()