# 🎥 Real-Time ASCII Video Converter

Convert live camera feed to ASCII art in real-time with gesture controls and keyboard shortcuts.

## 🚀 Quick Start

```bash
# Install dependencies
pip install opencv-python mediapipe numpy pillow keyboard

# Run gesture-controlled version (recommended)
python dual_window_ascii.py

# Or run full-featured version
python realtime_ascii.py
```

## 📱 Applications

### 1. **Dual Window ASCII** (`dual_window_ascii.py`)
- **Two windows**: Camera feed + ASCII art
- **Gesture controls**: Use hand movements to adjust brightness
- **Simple and intuitive**

### 2. **Interactive ASCII** (`realtime_ascii.py`)
- **Recording capabilities**: Save videos and screenshots
- **Keyboard controls**: Full customization options
- **Theme switching**: Dark/light modes

## 🎮 Controls

### Gesture Controls (Dual Window)
| Gesture | Action |
|---------|--------|
| 👍 Thumbs Up | Brighter ASCII |
| 👎 Thumbs Down | Darker ASCII |
| ✌️ Peace Sign | Toggle hand tracking |
| ✊ Fist | Reset settings |

### Keyboard Controls (Interactive)
| Key | Action |
|-----|--------|
| **SPACE** | Start/stop recording |
| **S** | Save screenshot |
| **↑/↓** | Adjust size |
| **+/-** | Adjust brightness |
| **T** | Toggle theme |
| **H** | Show help |
| **Q/ESC** | Exit |

## 📦 Installation

1. **Clone repository:**
```bash
git clone https://github.com/yourusername/ascii-cam.git
cd ascii-cam
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run application:**
```bash
python dual_window_ascii.py  # For gesture control
python realtime_ascii.py     # For full features
```

## ⚙️ Requirements

- Python 3.7+
- Webcam/Camera
- Libraries: OpenCV, MediaPipe, NumPy, Pillow, Keyboard

## 🔧 Features

- ✅ Real-time ASCII conversion
- ✅ Hand gesture recognition
- ✅ Video recording & screenshots
- ✅ Customizable brightness & size
- ✅ Dark/light themes
- ✅ Mirror effect for natural interaction

## 🐛 Troubleshooting

**Camera not working?**
- Try `cv2.VideoCapture(1)` instead of `0`
- Check camera permissions

**Poor gesture detection?**
- Ensure good lighting
- Keep hand clearly visible
- Avoid cluttered background

**Performance issues?**
- Reduce frame width (170-200)
- Close other camera applications

## 📄 License

MIT License - feel free to use and modify!

---

**Made with ❤️ for ASCII art enthusiasts**