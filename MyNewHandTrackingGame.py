import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm

pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)
# Set your desired resolution here
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Height
detector = htm.handDetector()

while True:
    success, img = cap.read()
    if not success:
        break
    img = detector.findHands(img)
    lmlist = detector.findposition(img)
    if lmlist != 0:
        print(lmlist)  # value at any index

    cTime = time.time()
    fps = 1 / (cTime - pTime)  # Calculate FPS   as frames per second (inverse of time between frames)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
