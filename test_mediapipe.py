import cv2
import mediapipe as mp

# Quick test to verify MediaPipe is working
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ Camera access: OK")
    ret, frame = cap.read()
    if ret:
        print("✅ Frame capture: OK")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        print("✅ MediaPipe processing: OK")
        print("🎉 Everything is working! You can now run the full ASCII converter.")
    else:
        print("❌ Could not capture frame")
else:
    print("❌ Could not open camera")

cap.release()
hands.close()