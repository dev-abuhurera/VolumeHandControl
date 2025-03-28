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
        self.box_color = (0, 255, 255)  # Yellow boxes
        self.box_thickness = 2

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

    def draw_interface(self, img, landmark_list, point1_id=4, point2_id=8, draw_midpoint=True):
        """
        Draw connection between any two landmarks
        Args:
            img: Input image
            landmark_list: List of all landmarks [[id, x, y], ...]
            point1_id: First landmark index to connect (default 4=thumb)
            point2_id: Second landmark index to connect (default 8=index)
            draw_midpoint: Whether to draw midpoint circle when close
        """
        if landmark_list and len(landmark_list) > max(point1_id, point2_id):
            # Get specified landmarks
            x1, y1 = landmark_list[point1_id][1], landmark_list[point1_id][2]
            x2, y2 = landmark_list[point2_id][1], landmark_list[point2_id][2]

            # Draw connection between specified points
            cv2.circle(img, (x1, y1), 15, (20, 100, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (20, 100, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

            # Draw midpoint if enabled and fingers are close
            if draw_midpoint and self.calculate_distance(x1, y1, x2, y2) < 50:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(img, (cx, cy), 15, (20, 100, 200), cv2.FILLED)

        # Draw volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
        cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, f'{int(self.volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        return img

    def run(self):
        """Main loop to run the volume controller"""
        while True:
            success, img = self.cap.read()
            if not success:
                break

            # Use the box detection method
            img, hand_boxes = self.detector.find_hands_with_box(
                img,
                draw_landmarks=True,
                draw_box=True,
                box_color=self.box_color,
                box_thickness=self.box_thickness
            )

            # Get landmark positions
            lm_list = self.detector.find_position(img, draw=False)

            if lm_list and len(lm_list) > 8:
                try:
                    # Calculate volume based on thumb and index finger
                    length = self.calculate_distance(lm_list[4][1], lm_list[4][2],
                                                     lm_list[8][1], lm_list[8][2])
                    vol = self.map_volume(length)
                    self.volume.SetMasterVolumeLevel(vol, None)
                except IndexError:
                    pass

            # Calculate FPS
            ctime = time.time()
            fps = 1 / (ctime - self.ptime)
            self.ptime = ctime

            # Draw interface with custom connections
            img = self.draw_interface(img, lm_list, point1_id=4, point2_id=8)

            # Display FPS
            cv2.putText(img, f"FPS: {int(fps)}", (40, 70),
                       cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

            cv2.imshow("Volume Control with Hand Boxes", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    controller = VolumeController()
    controller.run()


if __name__ == "__main__":
    main()