# Hand Gesture Volume Control ✋🔊  

![Demo GIF](demo.gif) *(Replace with your actual demo image/ GIF)*  

## 📌 Project Overview  
A Python application that uses **OpenCV** and **MediaPipe** to control your system volume by detecting hand gestures (thumb and index finger distance).  

---

## 🚀 Features  
✅ **Real-time hand tracking**  
✅ **Volume adjustment** (move fingers apart/closer)  
✅ **Visual feedback** (volume bar + percentage)  
✅ **Mute function** (fingers touch)  
✅ **FPS counter** (performance monitoring)  

---

## 🛠 Setup  

### Prerequisites  
- Python 3.8+  
- Windows (for `pycaw` audio control)  
- Webcam  

### Installation  
1. Clone the repo:  
   ```bash
   git clone https://github.com/Abuhurera-coder/VolumeHandControl.git
   cd VolumeHandControl
Install dependencies:

bash
pip install -r requirements.txt
Run:

bash
python volume_hand_control.py
👆 Usage
Increase volume: Spread thumb & index finger

Decrease volume: Bring fingers closer

Mute: Touch fingers together

(Add screenshot of hand gestures here)

⚙ Customization
Setting	How to Change
Sensitivity	Modify [50, 300] in np.interp()
Colors	Edit cv2 RGB values
Camera resolution	Adjust wCam, hCam
🌐 Compatibility
OS	Hand Tracking	Volume Control	Notes
Windows	✅ Yes	✅ Yes	Full functionality
macOS	✅ Yes	❌ No	No pycaw support
Linux	✅ Yes	❌ No	Requires alternative audio control
⚠ Troubleshooting
Issue	Fix
No volume control	Use Windows (or implement alsaaudio for Linux)
Hand not detected	Improve lighting/background
High CPU usage	Lower camera resolution in code
📂 Files
text
.
├── volume_hand_control.py  # Main script
├── HandTrackingModule.py   # MediaPipe wrapper
└── requirements.txt       # Dependencies
