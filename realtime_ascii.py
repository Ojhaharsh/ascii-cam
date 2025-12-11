#!/usr/bin/env python3
"""
Real-Time ASCII Art Video Converter
Converts live camera feed to ASCII art with customizable settings
Author: Modified for educational purposes
"""

import cv2
import numpy as np
from PIL import Image
import keyboard as kb
from datetime import datetime

class ASCIIVideoProcessor:
    def __init__(self):
        """Initialize the ASCII video processor with default settings"""
        # ASCII character set from dark to light
        self.character_set = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", ".", " "]
        
        # Display settings
        self.char_size = 5
        self.font_scale = 0.2
        self.text_color = (0, 0, 0)
        self.background_color = 255
        self.dark_mode = False
        self.is_recording = False
        self.brightness_level = 1.0
        self.show_help = False
        
        # Video settings
        self.frame_width = 0
        self.frame_height = 0
        
    def convert_to_ascii(self, input_image):
        """Convert PIL image to ASCII text representation"""
        # Resize and convert to grayscale
        processed_img = input_image.resize((self.frame_width, self.frame_height)).convert("L")
        
        # Apply brightness adjustment
        brightness_array = np.array(processed_img)
        brightness_array = np.clip(brightness_array * self.brightness_level, 0, 255).astype(np.uint8)
        processed_img = Image.fromarray(brightness_array)
        
        # Map pixels to ASCII characters
        pixel_data = "".join([self.character_set[pixel_value // 22] for pixel_value in processed_img.getdata()])
        
        # Format as multi-line string
        ascii_text = "\n".join([pixel_data[idx:(idx + self.frame_width)] 
                               for idx in range(0, len(pixel_data), self.frame_width)])
        return ascii_text

    def render_ascii_image(self, ascii_string):
        """Convert ASCII string to visual image using OpenCV"""
        font_type = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        line_thickness = 0
        y_position = 0
        string_index = 0
        
        # Create blank canvas
        canvas = np.zeros([self.frame_height * self.char_size, 
                          self.frame_width * self.char_size, 3], dtype=np.uint8)
        canvas.fill(self.background_color)
        
        # Render each character
        for i in range(0, len(ascii_string), self.frame_width + 1):
            current_line = ascii_string[string_index:i]
            x_position = 0
            
            for character in current_line:
                position = (x_position, y_position)
                canvas = cv2.putText(canvas, character, position, font_type, 
                                   self.font_scale, self.text_color, line_thickness, cv2.FILLED)
                x_position += self.char_size
                
            y_position += self.char_size
            string_index = i
        
        return canvas

def display_instructions():
    """Display user instructions and controls"""
    instructions = """
    ═══════════════════════════════════════════════════════════════════════════════
    ║                    ASCII Video Converter - Live Camera Feed                 ║
    ═══════════════════════════════════════════════════════════════════════════════
    ║ Recommended frame width: 170-240 (higher values may reduce performance)     ║
    ║                                                                             ║
    ║ 🎮 KEYBOARD CONTROLS:                                                       ║
    ║                                                                             ║
    ║ 📹 RECORDING & CAPTURE:                                                     ║
    ║ • SPACE: Start/Stop video recording                                         ║
    ║ • S: Save screenshot (capture current frame)                                ║
    ║                                                                             ║
    ║ 🎨 VISUAL ADJUSTMENTS:                                                      ║
    ║ • ↑/↓ Arrow Keys: Adjust character size (bigger/smaller)                    ║
    ║ • +/- Keys: Modify brightness (brighter/darker)                             ║
    ║ • T: Toggle theme (dark/light mode)                                         ║
    ║                                                                             ║
    ║ ⚙️ SETTINGS:                                                                ║
    ║ • R: Reset all settings to defaults                                         ║
    ║ • H: Show/Hide this help                                                    ║
    ║                                                                             ║
    ║ 🚪 EXIT:                                                                    ║
    ║ • Q or ESC: Exit application                                                ║
    ║                                                                             ║
    ║ 🎉 Enjoy creating ASCII art!                                                ║
    ═══════════════════════════════════════════════════════════════════════════════
    """
    print(instructions)

def get_frame_dimensions():
    """Get and validate frame width from user input"""
    min_width = 170
    
    while True:
        try:
            width = int(input("Enter desired frame width (minimum 170): "))
            if width >= min_width:
                break
            else:
                print(f"Frame width too small! Please enter a value >= {min_width}")
        except ValueError:
            print("Please enter a valid number!")
    
    # Calculate height maintaining 16:9 aspect ratio
    aspect_ratio = 9 / 16
    height = int(aspect_ratio * width)
    
    return width, height

def main():
    """Main application function"""
    # Display instructions
    display_instructions()
    
    # Initialize processor
    processor = ASCIIVideoProcessor()
    
    # Get frame dimensions
    processor.frame_width, processor.frame_height = get_frame_dimensions()
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, processor.frame_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, processor.frame_height)
    
    video_writer = None
    
    print("Starting ASCII video conversion...")
    print("Camera initialized successfully!")
    
    # Main processing loop
    while True:
        # Generate timestamp for file naming
        current_time = datetime.now()
        timestamp = current_time.strftime("%H_%M_%S_%f")
        
        # Capture frame from camera
        success, raw_frame = camera.read()
        
        if success:
            # Process frame: flip for mirror effect and convert to ASCII
            mirrored_frame = cv2.flip(raw_frame, 1)
            ascii_text = processor.convert_to_ascii(Image.fromarray(mirrored_frame))
            ascii_image = processor.render_ascii_image(ascii_text)
            
            # Display windows
            cv2.imshow("ASCII Art Output", ascii_image)
            cv2.imshow("Original Camera Feed", cv2.resize(mirrored_frame, (480, 360)))
        
            # Handle keyboard input with improved controls
            if kb.is_pressed("q") or kb.is_pressed("esc"):
                print("🚪 Shutting down application...")
                break
            
            elif kb.is_pressed("s"):
                filename = f"ASCII_CAPTURE_{timestamp}.jpg"
                cv2.imwrite(filename, ascii_image)
                print(f"📸 Screenshot saved as: {filename}")

            elif kb.is_pressed("space"):
                if not processor.is_recording:
                    print("🎬 Recording started...")
                    processor.is_recording = True
                    video_filename = f"ASCII_Recording_{timestamp}.avi"
                    fourcc = cv2.VideoWriter_fourcc(*'MP42')
                    frame_size = (processor.frame_width * processor.char_size, 
                                processor.frame_height * processor.char_size)
                    video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, frame_size)
                else:
                    processor.is_recording = False
                    print("⏹️ Recording stopped and saved!")
                    if video_writer:
                        video_writer.release()
                        video_writer = None
                
            elif kb.is_pressed("up"):
                # Increase character size (max 15)
                processor.char_size = min(15, processor.char_size + 1)
                print(f"📏 Character size: {processor.char_size}")

            elif kb.is_pressed("down"):
                # Decrease character size (min 2)
                processor.char_size = max(2, processor.char_size - 1)
                print(f"📏 Character size: {processor.char_size}")
                
            elif kb.is_pressed("+") or kb.is_pressed("="):
                # Increase brightness (max 2.0)
                processor.brightness_level = min(2.0, processor.brightness_level + 0.1)
                print(f"☀️ Brightness: {processor.brightness_level:.1f}")

            elif kb.is_pressed("-"):
                # Decrease brightness (min 0.3)
                processor.brightness_level = max(0.3, processor.brightness_level - 0.1)
                print(f"🌙 Brightness: {processor.brightness_level:.1f}")

            elif kb.is_pressed("r"):
                # Reset to default settings
                processor.char_size = 5
                processor.font_scale = 0.2
                processor.brightness_level = 1.0
                print("🔄 Settings reset to defaults")

            elif kb.is_pressed("t"):
                # Toggle dark/light mode
                processor.dark_mode = not processor.dark_mode
                if processor.dark_mode:
                    processor.background_color = 0
                    processor.text_color = (255, 255, 255)
                    processor.character_set = processor.character_set[::-1]
                    print("🌙 Switched to dark mode")
                else:
                    processor.background_color = 255
                    processor.text_color = (0, 0, 0)
                    processor.character_set = processor.character_set[::-1]
                    print("☀️ Switched to light mode")
            
            elif kb.is_pressed("h"):
                # Toggle help display
                processor.show_help = not processor.show_help
                if processor.show_help:
                    display_instructions()
                else:
                    print("ℹ️ Help hidden")
                
            # Write frame to video if recording
            if processor.is_recording and video_writer:
                video_writer.write(ascii_image)
        
        # Small delay to prevent excessive CPU usage
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
    
    # Cleanup
    camera.release()
    if video_writer:
        video_writer.release()
    cv2.destroyAllWindows()
    print("Application closed successfully!")

if __name__ == "__main__":
    main()