import cv2
import mediapipe as mp
import time


class HandDetector():
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, tracking_con=0.5):
        """
        Initialize hand detector with parameters:
        :param mode: Whether to treat input images as static images or video stream
        :param max_hands: Maximum number of hands to detect
        :param detection_con: Minimum detection confidence threshold
        :param tracking_con: Minimum tracking confidence threshold
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.tracking_con = tracking_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.tracking_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        Find hands in an image
        :param img: Image to find hands in
        :param draw: Whether to draw landmarks on the image
        :return: Image with hand landmarks drawn if draw=True
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        connection_drawing_spec=self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
        return img

    def find_position(self, img, hand_no=0, draw=True, landmark_ids=None):
        """
        Find positions of hand landmarks
        :param img: Image containing the hand
        :param hand_no: Which hand to track (0 = first hand detected)
        :param draw: Whether to draw circles on the landmarks
        :param landmark_ids: List of specific landmark IDs to track (None for all)
        :return: List of landmark positions [id, x, y]
        """
        lm_list = []

        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]

            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                if landmark_ids is None or id in landmark_ids:
                    lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        return lm_list


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandDetector(max_hands=2)

    p_time = 0
    c_time = 0

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture image")
                break

            img = detector.find_hands(img)
            lm_list = detector.find_position(img, draw=True)

            # Print thumb tip position (landmark 4)
            if len(lm_list) != 0:
                print(f"Thumb tip position: {lm_list[4]}")

            # Calculate and display FPS
            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time

            cv2.putText(
                img,
                f"FPS: {int(fps)}",
                (10, 70),
                cv2.FONT_HERSHEY_DUPLEX,
                2,
                (255, 0, 255),
                3
            )

            cv2.imshow("Hand Tracking", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()