import cv2
import numpy as np
import os
import time

class SimpleASCIIConverter:
    def __init__(self):
        # ASCII characters from darkest to lightest
        self.ascii_chars = "@%#*+=-:. "
        
        # Video settings
        self.width = 120
        self.height = 40
        self.brightness = 1.0
        self.contrast = 1.0
        
    def pixel_to_ascii(self, pixel_value):
        """Convert pixel brightness to ASCII character"""
        ascii_index = int(pixel_value / 255 * (len(self.ascii_chars) - 1))
        return self.ascii_chars[ascii_index]
    
    def frame_to_ascii(self, frame):
        """Convert entire frame to ASCII"""
        # Resize frame
        resized = cv2.resize(frame, (self.width, self.height))
        
        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Apply brightness and contrast
        gray = cv2.convertScaleAbs(gray, alpha=self.contrast, beta=self.brightness * 50)
        
        # Convert to ASCII
        ascii_frame = []
        for row in gray:
            ascii_row = ''.join([self.pixel_to_ascii(pixel) for pixel in row])
            ascii_frame.append(ascii_row)
        
        return ascii_frame
    
    def run(self):
        """Main loop for real-time ASCII video conversion"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Simple ASCII Video Converter Started!")
        print("Controls:")
        print("'q' - Quit")
        print("'+' - Increase brightness")
        print("'-' - Decrease brightness")
        print("'r' - Reset settings")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to ASCII
            ascii_frame = self.frame_to_ascii(frame)
            
            # Clear screen and display ASCII
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Print ASCII frame
            for line in ascii_frame:
                print(line)
            
            # Show original video
            cv2.imshow('Original Video', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                self.brightness = min(2.0, self.brightness + 0.2)
                print(f"Brightness: {self.brightness:.1f}")
            elif key == ord('-'):
                self.brightness = max(0.2, self.brightness - 0.2)
                print(f"Brightness: {self.brightness:.1f}")
            elif key == ord('r'):
                self.brightness = 1.0
                self.contrast = 1.0
                print("Settings reset!")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    converter = SimpleASCIIConverter()
    converter.run()