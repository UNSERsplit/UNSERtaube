from typing import List
import cv2
import threading
import time
import os
import numpy as np

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

class VisionWorker:
    def __init__(self) -> None:
        self.show_filtered_frame = False

        self.hue_upper = 170
        self.hue_lower = 5

        self.value_upper = 255
        self.value_lower = 120

        self.saturation_upper = 255
        self.saturation_lower = 80

        self.processing_frame = None
        self.processed_frame = None
        self.last_process_start = None

    def on_position(self, framex, framey, frame_shape, width, height):
        pass

    
    def _process_frame(self, original_frame):

        frame, mask = self._filter_red_parts(original_frame)
        #mask = self._fix_mask(mask)
        #mask = self._canny(mask)
        #return cv2.bitwise_and(original_frame, original_frame, mask=mask)
        frame, mask, contours = self._find_contours(frame, mask)

        final = original_frame
        original_frame = original_frame.copy()

        ellipselist = []
        for contour in contours:
            if len(contour) < 5:
                continue
            ellipse = cv2.fitEllipse(contour)
            area = cv2.contourArea(contour)
            if area < 2000:
                continue
            ellipselist.append(ellipse)

        merged_ellipselist = self._check_mergeable_ellipses(ellipselist, original_frame.shape)

        for ellipse in ellipselist:
            center, axes, angle = ellipse
            center = list(map(lambda x: int(x),list(center)))
            final = cv2.ellipse(final, ellipse, (0,0,255), 3) #type: ignore
            final = cv2.circle(final, center, 3, (0,255,0), -1)
            final = cv2.putText(final, str(int(0)), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)


        return cv2.bitwise_and(frame, frame)
    
    def _canny(self, frame):
        sigma = 0.33

        median = np.median(frame)
        lower = int(max(0, (1.0 - sigma) * median))
        upper = int(min(255, (1.0 + sigma) * median))
        edge_image = cv2.Canny(frame, lower, upper)

        return edge_image

        return frame, raw_mask, ctns

    def _check_mergeable_ellipses(self, ellipselist, canvas_shape):
        new_ellipses = []
        used_ellipses = []
        width, height, _ = canvas_shape
        for i in range(len(ellipselist)):
            if i in used_ellipses:
                continue

            found_merge = False
            for j in range(i + 1, len(ellipselist)):
                if j in used_ellipses:
                    continue

                e1 = ellipselist[i]
                e2 = ellipselist[j]

                (x1, y1), (w1, h1), angle1 = e1
                (x2, y2), (w2, h2), angle2 = e2


                if abs(y1 - y2) < 40 and abs(angle1 + angle2 - 180) < 30:
                    merged = self._merge_ellipses(e1, e2, (width, height))

                    if merged is not None:
                        new_ellipses.append(merged)
                        used_ellipses.append(i)
                        used_ellipses.append(j)
                        found_merge = True
                        break # diesen schleifendurchgang beenden, da ja mit ellipse schon gemerged wurde


            if not found_merge: # keine Merges gefunden:
                new_ellipses.append(ellipselist[i])

        return new_ellipses


    def _merge_ellipses(self, e1, e2, canvas_shape):

        mask = np.zeros(canvas_shape, dtype=np.uint8)

        cv2.ellipse(mask, e1, 255, -1)
        cv2.ellipse(mask, e2, 255, -1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Alle Konturpunkte aller gefundenen Inseln zusammenfassen
            all_points = np.vstack(contours)

            # 4. FitEllipse benötigt mindestens 5 Punkte
            if len(all_points) >= 5:
                new_ellipse = cv2.fitEllipse(all_points)
                return new_ellipse

        return None

hue_upper = 170
hue_lower = 5

value_upper = 255
value_lower = 120

saturation_upper = 255
saturation_lower = 80

# Lower mask (0-10)
lower_red1 = np.array([
    0, 
    saturation_lower, 
    value_lower
])
upper_red1 = np.array([
    hue_lower, 
    saturation_upper, 
    value_upper
])

# Upper mask (170-180)
lower_red2 = np.array([
    hue_upper, 
    saturation_lower, 
    value_lower
])
upper_red2 = np.array([
    180, 
    saturation_upper, 
    value_upper
])

def _filter_red_parts(frame):
    img = cv2.GaussianBlur(frame, (9, 9), 0)
    #img = cv2.bilateralFilter(frame, 30, 75, 75)

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask0 = cv2.inRange(img_hsv, lower_red1, upper_red1)

    mask1 = cv2.inRange(img_hsv, lower_red2, upper_red2)

    # Join the masks
    raw_mask = mask0 | mask1 # type: ignore Kein plan was vs-code hier hat, es funktioniert eh

    return img, raw_mask

def _fix_mask(raw_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel, iterations=15)
    return raw_mask

def _find_contours(frame, raw_mask):
    ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours
    final = frame
    for contour in ctns:
        if len(contour) < 5:
            continue
        ellipse = cv2.fitEllipse(contour)
        area = cv2.contourArea(contour)
        if area < 2000:
            continue

        center, axes, angle = ellipse

        ratio = int(axes[0] / axes[1] * 10)
        dy = int(center[0]) - int(frame.shape[1] / 2)
        dx = int(center[1]) - int(frame.shape[0] / 2)

        move(ratio, dx, dy)

        center = list(map(lambda x: int(x),list(center)))
        final = cv2.ellipse(final, ellipse, (0,0,255), 3) #type: ignore
        final = cv2.circle(final, center, 3, (0,255,0), -1)
        final = cv2.putText(final, str(ratio), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        final = cv2.line(final, center, (center[0] - dy, center[1] - dx), (0,255,0))
        
    return final

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
worker = VisionWorker()
print("Connected!")

try:
    # 2. FIX THE 60% BURN: Don't hammer the UI
    while True:
        # Only spend CPU rendering the image IF it's a completely new frame
        if stream.new_frame_ready and stream.frame is not None:
            stream.new_frame_ready = False  # Reset flag so we don't redraw the exact same frame

            img, mask = _filter_red_parts(stream.frame)
            #mask = _fix_mask(mask)
            img = cv2.bitwise_and(img, img, mask=mask)
            #img = _find_contours(img, mask)

            #frame = cv2.bitwise_and(img, img, mask=mask)

            cv2.imshow("Sub-Second Stream", img)
            
        
        # Wait 33ms (~30 FPS limit for the UI). 
        # This lets your CPU sleep instead of looping 1000 times a second.
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
finally:
    stream.stop()
    cv2.destroyAllWindows()