import numpy as np
import cv2
import threading
import time
from dronemaster.connection import log

#showDebugHud.set(true)

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
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.last_process_start = None
    
    def _run(self):
        while True:
            if self.processing_frame is not None:
                frame = self.processing_frame
                self.last_process_start = time.time()
                self.processed_frame = self._process_frame(frame)
                log("FPS", 1 / (time.time() - self.last_process_start))
                self.processing_frame = None

    def on_frame(self, frame):
        if self.processing_frame is None:
            self.processing_frame = frame

        if self.show_filtered_frame:
            if self.processed_frame is not None:
                return self.processed_frame
            return np.zeros_like(frame)
        else:
            return frame
    
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

        # while i in range(len(ellipselist)):


        for ellipse in ellipselist:
            center, axes, angle = ellipse
            center = list(map(lambda x: int(x),list(center)))
            final = cv2.ellipse(final, ellipse, (0,0,255), 3) #type: ignore
            final = cv2.circle(final, center, 3, (0,255,0), -1)
            final = cv2.putText(final, str(int(area)), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)


        return cv2.bitwise_and(frame, frame)
    
    def _canny(self, frame):
        sigma = 0.33

        median = np.median(frame)
        lower = int(max(0, (1.0 - sigma) * median))
        upper = int(min(255, (1.0 + sigma) * median))
        edge_image = cv2.Canny(frame, lower, upper)

        return edge_image
    
    def _filter_red_parts(self, frame):
        img = cv2.bilateralFilter(frame, 30, 75, 75)

        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # Lower mask (0-10)
        lower_red = np.array([
            0, 
            self.saturation_lower, 
            self.value_lower
        ])
        upper_red = np.array([
            self.hue_lower, 
            self.saturation_upper, 
            self.value_upper
        ])
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

        # Upper mask (170-180)
        lower_red = np.array([
            self.hue_upper, 
            self.saturation_lower, 
            self.value_lower
        ])
        upper_red = np.array([
            180, 
            self.saturation_upper, 
            self.value_upper
        ])
        mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

        # Join the masks
        raw_mask = mask0 | mask1 # type: ignore Kein plan was vs-code hier hat, es funktioniert eh

        return img, raw_mask

    def _fix_mask(self, raw_mask):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel, iterations=15)
        return raw_mask

    def _find_contours(self, frame, raw_mask):

        ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours

        return frame, raw_mask, ctns

    def _check_mergeable_ellipses(self, ellipselist):
        new_ellipses = []
        merged_ellipses = []
        for ellipse1 in ellipselist:
            for ellipse2 in ellipselist:
                if ellipse1 == ellipse2:
                    continue
                (x1, y1), (w1, h1), angle1 = ellipse1
                (x2, y2), (w2, h2), angle2 = ellipse2
                if x1 < x2:
                    left = ellipse1
                    right = ellipse2
                else:
                    left = ellipse2
                    right = ellipse1

                if abs(y1-y2)<40 and abs(angle1 + angle2 - 180) < 30:
                    new_ellipse = self._merge_ellipses(ellipse1, ellipse2)
                    if new_ellipse is not None:
                        new_ellipses.append(new_ellipse)
                        merged_ellipses.append(ellipse1)
                        merged_ellipses.append(ellipse2)

        for ellipse in merged_ellipses:
            ellipselist.remove(ellipse)
        for ellipse in ellipselist:
            new_ellipses.append(ellipse)

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