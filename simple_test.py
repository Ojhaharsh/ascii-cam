import cv2
import mediapipe as mp
import time

print("Testing camera and MediaPipe...")

# Test camera first
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Camera not working")
    exit()

print("✅ Camera working")

# Test MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("✅ MediaPipe initialized")
print("Show your hand to the camera...")

frame_count = 0
detection_count = 0

for i in range(50):  # Test 50 frames
    ret, frame = cap.read()
    if not ret:
        continue
        
    frame_count += 1
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        detection_count += 1
        print(f"Frame {frame_count}: Hand detected! ({detection_count} total)")
    
    cv2.imshow('Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(0.1)

print(f"Test complete: {detection_count}/{frame_count} frames had hand detection")

cap.release()
cv2.destroyAllWindows()
hands.close()