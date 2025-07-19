# Hand Gesture Volume Control ✋🔊  


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


pip install -r requirements.txt


Run:
python volume_hand_control.py


## 👆 Usage  
- **Increase volume**: Spread thumb & index finger apart → 📈  
- **Decrease volume**: Bring fingers closer together → 📉  
- **Mute**: Touch thumb and index finger → 🔇  

*(Add `demo_gestures.png` or GIF showing these actions)*  

---

## ⚙ Customization  

| Setting               | Modification Guide                     |
|-----------------------|----------------------------------------|
| **Sensitivity**       | Edit `[50, 300]` range in `np.interp()`|
| **Colors**           | Change RGB values in `cv2` functions   |
| **Camera Resolution**| Adjust `wCam` and `hCam` variables     |

---

## 🌐 Compatibility  

| OS        | Hand Tracking | Volume Control | Notes                          |
|-----------|--------------|----------------|--------------------------------|
| **Windows** | ✅ Yes       | ✅ Yes          | Full functionality with `pycaw`|
| **macOS**  | ✅ Yes       | ❌ No           | Requires alternative audio control |
| **Linux**  | ✅ Yes       | ❌ No           | Use `alsaaudio` (Linux-only)   |

.
├── volume_hand_control.py  # Main script
├── HandTrackingModule.py   # MediaPipe wrapper
└── requirements.txt       # Dependencies
