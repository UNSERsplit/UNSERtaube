from typing import List
import cv2
import threading
import time
import os
import sys
import numpy as np

def merge_contours(contours):
    merging = []
    for c in contours:
        if True:
            merging.append(c)
    
    return np.vstack(merging)


def on_frame(frame):
    frame = cv2.GaussianBlur(frame, (9, 9), 0)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red wraps around 0° in HSV, so we need two ranges
    lower_red1 = np.array([0,   150,  120])
    upper_red1 = np.array([5,  255, 255])
    lower_red2 = np.array([160, 150,  100])
    upper_red2 = np.array([180, 255, 255])

    mask = (cv2.inRange(hsv, lower_red1, upper_red1)
            | cv2.inRange(hsv, lower_red2, upper_red2)) # type: ignore

    # Clean up noise
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) < 1:
        return
    
    contour = merge_contours(contours)

    if len(contour) < 2:
        return
    
    cv2.drawContours(frame, [contour], -1, (30, 30, 30), 3)

    if len(contour) < 5:
        return
    
    if len(contour) > 600:
        color = (0,255,0)
    else:
        color = (255,0,0)
    

    ellipse = cv2.fitEllipse(contour)
    cv2.ellipse(frame, ellipse, color, 3) #type: ignore
    cv2.putText(frame, f"Q:{len(contour)}", (0,50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    #frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    return frame, {
        "ellipse": ellipse,
        "accuracy": len(contour)
    }

# 1. FIX THE STARTUP HANG: Force instant connection
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;udp|"
    "fflags;nobuffer|"
    "flags;low_delay|"
    "probesize;32|"         # Stop analyzing massive chunks of data
    "analyzeduration;0"     # Stop waiting to figure out the framerate
)

class FastStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.frame = None
        self.new_frame_ready = False  # Track if we have fresh data
        self.stopped = False
        
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                has_frame = self.cap.grab()
                if has_frame:
                    ret, self.frame = self.cap.retrieve()
                    self.new_frame_ready = True  # Flag that a new frame arrived
            
            # Tiny sleep to keep the background thread from maxing a core
            time.sleep(0.001)

    def stop(self):
        self.stopped = True
        self.cap.release()

def move(ratio, dx, dy):
    if ratio < 8:
        print("Side-To-Side",end=" ")
    
    if dx > 10:
        print("Up",end=" ")

    if dx < 10:
        print("Down",end=" ")
    
    if dy > 10:
        print("Left",end=" ")
        
    if dy < 10:
        print("Right",end=" ")
    
    print("",end="\n")

# --- Main Application ---
url = "rtsp://127.0.0.1:8554/camera"
print("Connecting...")
stream = FastStream(url)
print("Connected!")

try:
    # 2. FIX THE 60% BURN: Don't hammer the UI
    while True:
        # Only spend CPU rendering the image IF it's a completely new frame
        if stream.new_frame_ready and stream.frame is not None:
            stream.new_frame_ready = False  # Reset flag so we don't redraw the exact same frame

            frame = stream.frame
            r = on_frame(frame)
            ret = None
            if r is not None:
                frame, ret = r

            cv2.imshow("Sub-Second Stream", frame)
            
        
        # Wait 33ms (~30 FPS limit for the UI). 
        # This lets your CPU sleep instead of looping 1000 times a second.
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
finally:
    stream.stop()
    cv2.destroyAllWindows()