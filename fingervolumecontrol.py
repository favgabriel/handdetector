import cv2
import time
import numpy as np
import HandleTrackingModule as htm
import math

wcam,hcam = 640, 480


cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4,hcam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface,POINTER(IAudioEndpointVolume))

# volume.GetMute()
# volume.GetMasterVolumeLevel()
volumerange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0,None)
minVol= volumerange[0]
maxVol = volumerange[1]
vol = 0
volBar = 400
volPer = 40

while True:
    success, img = cap.read()
    #find hand
    img = detector.findHands(img,draw=False)
    #get the hand position
    lmList,_ = detector.findPosition(img,draw=False)

    if len(lmList) != 0:
        # print(lmList[4],lmList[8])
        #get coordinates of index and thumb finger
        x1,y1 = lmList[4][1], lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        cx,cy = (x1 + x2) // 2, (y1 + y2) // 2
        #distance betwwen coordinates
        length = math.hypot(x2-x1, y2-y1)

        #Hand range 50-300
        #volume range -65 -0
        vol = np.interp(length,[50,300],[minVol,maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length,[50,300],[0,100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol,None)
        #since the hand range is from 50 we check if the length is greater than 50 to draw points
        if length > 50:
            cv2.circle(img,(cx,cy),15,(0,255,0),cv2.FILLED)
            #show thumb
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            #show line intersection
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            #cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    #volume bar graphics
    cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
    cv2.putText(img,f'{int(volPer)} %',(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)

    cTime = time.time()
    fps = 1/ (cTime-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}',(48,58),cv2.FONT_HERSHEY_PLAIN,1,(255,0,0),3)

    cv2.imshow("Img",img)
    cv2.waitKey(1)