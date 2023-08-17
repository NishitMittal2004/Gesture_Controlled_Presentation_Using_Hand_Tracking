import cv2
import os
import numpy as np
import HandTrackingModule as htm
import math
import autopy

width, height = 1080, 608
folderPath = "Demo Presentation"
frameR = 125  # Frame Reduction
smoothening = 2

plocX, plocY = 0,0  # Previous location
clocX, clocY = 0,0  # Current location

cap = cv2.VideoCapture(1)
cap.set(3, width)
cap.set(4, height)
# cap.set(10, 150)

detector = htm.handDetector(detectionCon=0.8, maxHands=1)

tipIds = [4, 8, 12, 16, 20]

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

# Variables
imgNumber = 0
hs, ws = int(76*1.5), int(135*1.5)
gestureThreshold = 200
buttonPressed = False
buttonCounter = 0
buttonDelay = 20
annotations = [[]]
annotationNumber = -1
annotationStart = False
wScr, hScr = autopy.screen.size()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # print(lmList)

    cv2.line(img, (0, gestureThreshold),(width,gestureThreshold), (128,128,128), 5)

    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Adding webcam image on the slides
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws:w] = imgSmall

    if len(lmList) != 0 and buttonPressed is False:
        fingers = []
        p1, p2 = lmList[5][1], lmList[5][2]
        q1, q2 = lmList[0][1], lmList[0][2]
        cx, cy = (p1+q1)//2, (p2+q2)//2
        # print(cx, cy)

        # Thumb
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[9][1], lmList[9][2]
        length = math.hypot(x2 - x1, y2 - y1)
        # print(int(length))
        if length > 50:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Index Finger
        xVal = int(np.interp(lmList[8][1], [width//2,width-250], [0,w]))
        yVal = int(np.interp(lmList[8][2], [100,height-270], [0,h]))
        indexFinger = xVal, yVal
        # print(indexFinger)

        # print(fingers)
        totalFingers = fingers.count(1)
        # print(totalFingers)

        # Constrain values for easy drawing

        if cy <= gestureThreshold:

            # Gesture 1 - Left
            if fingers == [1,0,0,0,0]:
                annotationStart = False
                # print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = -1
                    imgNumber = imgNumber - 1

            # Gesture 2 - Right
            if fingers == [0,0,0,0,1]:
                annotationStart = False
                # print("Right")
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = -1
                    imgNumber = imgNumber + 1

        # Gesture 3 - Show Pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
            annotationStart = False
            # print("Pointer")

        # Gesture 4 - Draw Pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
            # print("Drawing")

        # Gesture 5 - Erase
        if fingers == [1, 1, 1, 1, 1]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    else:
        annotationStart = False

    # Button pressed iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0,0,200), 8)


    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break