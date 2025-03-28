import cv2
import mediapipe as mp
import time


class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img , {}

    def find_hands_with_box(self, img, draw_landmarks=True, draw_box=True, box_color=(0, 255, 255), box_thickness=3):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        hand_boxes = []

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                # Get all landmark coordinates
                landmark_list = []
                for landmark in hand_landmarks.landmark:
                    h, w, c = img.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmark_list.append((cx, cy))

                # Calculate bounding box
                x_min = min(landmark_list, key=lambda x: x[0])[0]
                y_min = min(landmark_list, key=lambda x: x[1])[1]
                x_max = max(landmark_list, key=lambda x: x[0])[0]
                y_max = max(landmark_list, key=lambda x: x[1])[1]
                hand_boxes.append((x_min, y_min, x_max, y_max))

                # Draw box and landmarks
                if draw_box:
                    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), box_color, box_thickness)
                    # Draw center point
                    center_x, center_y = (x_min + x_max) // 2, (y_min + y_max) // 2
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), cv2.FILLED)

                if draw_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img, hand_boxes

    def find_position(self, img, hand_no=0, draw=True, landmark_ids=None):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if landmark_ids is None or id in landmark_ids:
                    lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        return lm_list


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandDetector()
    p_time = 0

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture frame")
                break

            # Use the box detection method
            img, hand_boxes = detector.find_hands_with_box(
                img,
                draw_landmarks=True,
                draw_box=True,
                box_color=(255, 200, 100),  # Yellow boxes
                box_thickness=3
            )

            # # Get landmark positions (optional)
            # lm_list = detector.find_position(img, draw=False)
            # if len(lm_list) > 8:  # If hand detected
            #     print(f"Thumb position: {lm_list[4][1:]}, Index position: {lm_list[8][1:]}")

            # Display FPS
            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            cv2.imshow("Hand Tracking with Boxes", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()