import cv2
import numpy as np
import HandleTrackingModule as htm
import time
import autopy

###############################
wCam,hCam = 640,480
smoothening = 5
frameR = 100 # frame reduction
##############################
pTime =0
plocx,plocy =0,0
clocx,clocy=0,0

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist,bbox = detector.findPosition(img)

    if len(lmlist) != 0:
        x1,y1 = lmlist[0][1:]
        x2, y2= lmlist[12][1:]

        # print(x1,y1,x2,y2)

        fingers = detector.fingersUp()
        #set the frame coordinate where mouse should move
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        #mouse move
        if fingers[1]==1 and fingers[2] == 0:
            x3 = np.interp(x1,(frameR,wCam),(0,wScr))
            y3 = np.interp(y1,(frameR,hCam),(0,hScr))

            #smoothing values so the mouse does not shake
            clocx = plocx*(x3-plocx)/smoothening
            clocy = plocy * (y3-plocy)/smoothening
            #flip the width by minus the screen width from the x3 coordinates
            autopy.mouse.move(wScr-clocx,clocy)
            cv2.circle(img,(x1,y1),12,(255,0,255),cv2.FILLED)
            plocx,plocy = clocx,clocy

        #mouse click
        if fingers[1] ==1 and fingers[2] == 1:
            length, img, lineinfo = detector.findDistance(8,12,img)
            if length < 40:
                cv2.circle(img,(lineinfo[4],lineinfo[5]),15,(0,255,0),cv2.FILLED)
                autopy.mouse.click()

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    #cv2.putText(img,f"fps {fps}")
    cv2.imshow("Image",img)
    cv2.waitKey(1)