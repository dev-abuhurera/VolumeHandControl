import cv2
import time
import math
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeController:
    def __init__(self, width=1280, height=720, detection_con=0.7):
        """Initialize volume controller with camera and hand detector"""
        # Camera setup
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, width)
        self.cap.set(4, height)

        # Hand detector
        self.detector = htm.HandDetector(detection_con=detection_con)

        # Volume control
        self.setup_volume_control()

        # Tracking variables
        self.ptime = 0
        self.volBar = 400
        self.volPer = 0

    def setup_volume_control(self):
        """Initialize system volume control"""
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]

    def calculate_distance(self, x1, y1, x2, y2):
        """Calculate distance between two points"""
        return math.hypot(x2 - x1, y2 - y1)

    def map_volume(self, distance):
        """Map finger distance to volume range"""
        vol = np.interp(distance, [50, 300], [self.minVol, self.maxVol])
        self.volBar = np.interp(distance, [50, 300], [400, 150])
        self.volPer = np.interp(distance, [50, 300], [0, 100])
        return vol

    def draw_interface(self, img, x1, y1, x2, y2, cx, cy, fps):
        """Draw all UI elements on the image"""
        # Draw fingers and connection
        cv2.circle(img, (x1, y1), 15, (20, 100, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (20, 100, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        # Draw volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
        cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, f'{int(self.volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        # Draw FPS
        cv2.putText(img, f"FPS: {int(fps)}", (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        return img

    def run(self):
        """Main loop to run the volume controller"""
        while True:
            success, img = self.cap.read()
            if not success:
                break

            img = self.detector.find_hands(img)
            lmlist = self.detector.find_position(img, draw=False)

            x1 = y1 = x2 = y2 = cx = cy = 0 # initialize the local variables

            if len(lmlist) != 0:
                x1, y1 = lmlist[4][1], lmlist[4][2]  # Thumb
                x2, y2 = lmlist[8][1], lmlist[8][2]  # Index finger
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                length = self.calculate_distance(x1, y1, x2, y2)
                vol = self.map_volume(length)
                self.volume.SetMasterVolumeLevel(vol, None)

                if length < 50:
                    cv2.circle(img, (cx, cy), 15, (20, 100, 200), cv2.FILLED)

            # Calculate FPS
            ctime = time.time()
            fps = 1 / (ctime - self.ptime)
            self.ptime = ctime

            img = self.draw_interface(img, x1, y1, x2, y2, cx, cy, fps)

            cv2.imshow("Volume Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    controller = VolumeController()
    controller.run()


if __name__ == "__main__":
    main()