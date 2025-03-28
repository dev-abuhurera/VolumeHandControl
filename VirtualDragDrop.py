import cv2
import numpy as np
import HandTrackingModule as htm
from VolumeHandControl import VolumeController


class DraggableBox:
    def __init__(self, pos_center, size=[150, 150]):
        self.pos_center = list(pos_center)  # [x, y]
        self.size = size  # [width, height]
        self.dragging = False
        self.color = (255, 0, 255, 80)  # Purple with 80 alpha (semi-transparent)
        self.pinch_counter = 0
        self.release_counter = 0
        self.offset_x = 0
        self.offset_y = 0

    def update(self, img, lm_list, pinch_threshold=35, debounce_threshold=5):
        if lm_list and len(lm_list) > 12:
            # Get finger positions
            index_x, index_y = lm_list[8][1], lm_list[8][2]  # Index finger
            middle_x, middle_y = lm_list[12][1], lm_list[12][2]  # Middle finger

            # Calculate distance between fingers
            finger_distance = VolumeController.calculate_distance(None, index_x, index_y, middle_x, middle_y)

            # Check if fingers are inside this box
            inside_box = (self.pos_center[0] - self.size[0] // 2 <= index_x <= self.pos_center[0] + self.size[0] // 2 and
                          self.pos_center[1] - self.size[1] // 2 <= index_y <= self.pos_center[1] + self.size[1] // 2)

            # Pinch detection with debouncing
            if finger_distance < pinch_threshold and inside_box:
                self.pinch_counter += 1
                self.release_counter = 0

                if self.pinch_counter >= debounce_threshold:
                    if not self.dragging:
                        # Calculate offset when starting to drag
                        self.offset_x = self.pos_center[0] - (index_x + middle_x) // 2
                        self.offset_y = self.pos_center[1] - (index_y + middle_y) // 2
                        self.dragging = True

                    # Update position with offset
                    self.pos_center[0] = (index_x + middle_x) // 2 + self.offset_x
                    self.pos_center[1] = (index_y + middle_y) // 2 + self.offset_y
                    self.color = (0, 255, 0, 80)  # Green (semi-transparent) when dragging

                    # Draw pinch indicator
                    cv2.circle(img, ((index_x + middle_x) // 2, (index_y + middle_y) // 2),
                               12, (0, 0, 255), cv2.FILLED)
            else:
                self.release_counter += 1
                self.pinch_counter = 0

                if self.release_counter >= debounce_threshold and self.dragging:
                    self.dragging = False
                    self.color = (255, 0, 255, 80)  # Purple when released

        return finger_distance if 'finger_distance' in locals() else None

    def draw(self, img):
        overlay = img.copy()

        # Get box coordinates
        x1, y1 = int(self.pos_center[0] - self.size[0] // 2), int(self.pos_center[1] - self.size[1] // 2)
        x2, y2 = int(self.pos_center[0] + self.size[0] // 2), int(self.pos_center[1] + self.size[1] // 2)

        # Draw semi-transparent rectangle
        cv2.rectangle(overlay, (x1, y1), (x2, y2), self.color[:3], cv2.FILLED)

        # Blend the overlay with the original image
        alpha = self.color[3] / 255.0
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # Draw an outline around the box
        cv2.rectangle(img, (x1, y1), (x2, y2), self.color[:3], 2)  # Outline


def main():
    # Initialize camera and detector
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    detector = htm.HandDetector(detection_con=0.8)

    # Create multiple draggable boxes
    boxes = [
        DraggableBox(pos_center=[200, 200]),
        DraggableBox(pos_center=[500, 200]),
        DraggableBox(pos_center=[800, 200]),
        DraggableBox(pos_center=[300, 500]),
        DraggableBox(pos_center=[700, 500])
    ]

    active_box = None  # Track which box is currently being dragged

    # Parameters
    PINCH_THRESHOLD = 35
    DEBOUNCE_THRESHOLD = 5

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)

        # Hand detection
        img, _ = detector.find_hands_with_box(img, draw_landmarks=True, draw_box=True,
                                              box_color=(255, 200, 100), box_thickness=3)
        lm_list = detector.find_position(img, draw=False)

        # Update and draw boxes
        for box in boxes:
            if active_box is None or active_box == box:
                finger_distance = box.update(img, lm_list, PINCH_THRESHOLD, DEBOUNCE_THRESHOLD)
                if box.dragging:
                    active_box = box  # Lock movement to only one box

            box.draw(img)

        # Release active box if fingers move apart
        if active_box and not active_box.dragging:
            active_box = None  # Allow new box to be selected

        # Display status
        status_text = f"Active Box: {'MOVING' if active_box else 'NONE'}"
        cv2.putText(img, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Pinch Threshold: {PINCH_THRESHOLD}px", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Draggable Semi-Transparent Boxes", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
