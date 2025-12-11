import cv2
import mediapipe as mp
import numpy as np

class GestureDebugger:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def analyze_hand(self, landmarks):
        """Analyze hand landmarks and return finger states"""
        # Key landmarks
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        # Check finger states (extended = tip above pip joint)
        thumb_up = thumb_tip[1] < thumb_ip[1]
        thumb_down = thumb_tip[1] > thumb_ip[1]
        index_up = index_tip[1] < index_pip[1]
        middle_up = middle_tip[1] < middle_pip[1]
        ring_up = ring_tip[1] < ring_pip[1]
        pinky_up = pinky_tip[1] < pinky_pip[1]
        
        return {
            'thumb_up': thumb_up,
            'thumb_down': thumb_down,
            'index_up': index_up,
            'middle_up': middle_up,
            'ring_up': ring_up,
            'pinky_up': pinky_up,
            'thumb_above_mcp': thumb_tip[1] < thumb_mcp[1],
            'thumb_below_mcp': thumb_tip[1] > thumb_mcp[1]
        }
    
    def detect_gesture(self, finger_states):
        """Detect gestures based on finger states"""
        if not finger_states:
            return "No hand detected"
            
        fs = finger_states
        
        # Thumbs up: thumb extended up, others down
        if (fs['thumb_up'] and fs['thumb_above_mcp'] and 
            not fs['index_up'] and not fs['middle_up'] and 
            not fs['ring_up'] and not fs['pinky_up']):
            return "👍 THUMBS UP"
            
        # Thumbs down: thumb extended down, others down  
        if (fs['thumb_down'] and fs['thumb_below_mcp'] and
            not fs['index_up'] and not fs['middle_up'] and
            not fs['ring_up'] and not fs['pinky_up']):
            return "👎 THUMBS DOWN"
            
        # Peace sign: index and middle up, others down
        if (fs['index_up'] and fs['middle_up'] and
            not fs['ring_up'] and not fs['pinky_up']):
            return "✌️ PEACE SIGN"
            
        # Fist: all fingers down
        if (not fs['thumb_up'] and not fs['index_up'] and 
            not fs['middle_up'] and not fs['ring_up'] and 
            not fs['pinky_up']):
            return "✊ FIST"
            
        return "Unknown gesture"
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
            
        print("Gesture Debug Mode - Press 'q' to quit")
        print("Hold your hand clearly in front of the camera")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            finger_states = None
            gesture = "No hand detected"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Get landmark positions
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        landmarks.append([cx, cy])
                    
                    finger_states = self.analyze_hand(landmarks)
                    gesture = self.detect_gesture(finger_states)
            
            # Display info on frame
            cv2.putText(frame, f"Gesture: {gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if finger_states:
                y_pos = 70
                for finger, state in finger_states.items():
                    status = "UP" if state else "DOWN"
                    color = (0, 255, 0) if state else (0, 0, 255)
                    cv2.putText(frame, f"{finger}: {status}", (10, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    y_pos += 30
            
            cv2.imshow('Gesture Debug', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    debugger = GestureDebugger()
    debugger.run()