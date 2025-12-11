#!/usr/bin/env python3
"""
Simple test to verify brightness changes are working in ASCII conversion
"""
import cv2
import numpy as np

def pixel_to_ascii(pixel_value):
    """Convert pixel brightness to ASCII character"""
    ascii_chars = "@%#*+=-:. "
    ascii_index = int(pixel_value / 255 * (len(ascii_chars) - 1))
    return ascii_chars[ascii_index]

def test_brightness_levels():
    """Test different brightness levels on a sample image"""
    # Create a test gradient image
    test_image = np.zeros((40, 120), dtype=np.uint8)
    for i in range(120):
        test_image[:, i] = int(i * 255 / 120)  # Gradient from black to white
    
    brightness_levels = [0.5, 1.0, 1.5, 2.0]
    
    print("Testing brightness levels on gradient image:")
    print("=" * 60)
    
    for brightness in brightness_levels:
        print(f"\nBrightness: {brightness}")
        print("-" * 30)
        
        # Apply brightness
        adjusted = cv2.convertScaleAbs(test_image, alpha=brightness, beta=0)
        
        # Convert to ASCII (just show first few rows)
        for row in range(3):
            ascii_row = ''.join([pixel_to_ascii(pixel) for pixel in adjusted[row]])
            print(ascii_row)

if __name__ == "__main__":
    test_brightness_levels()