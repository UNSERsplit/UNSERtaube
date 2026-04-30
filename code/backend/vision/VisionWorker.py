import numpy as np
import cv2

class VisionWorker:
    def __init__(self) -> None:
        self.show_filtered_frame = False

        self.hue_upper = 170
        self.hue_lower = 5

        self.value_upper = 255
        self.value_lower = 120

        self.saturation_upper = 255
        self.saturation_lower = 80

    def on_frame(self, frame):
        processed_frame = self._process_frame(frame)

        if self.show_filtered_frame:
            return processed_frame
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

        for contour in contours:
            if len(contour) < 5:
                continue
            ellipse = cv2.fitEllipse(contour)
            area = cv2.contourArea(contour)
            if area < 2000:
                continue
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
    
    def _merge_ellipses(self, e1, e2, final):
        mask = np.zeros((500, 500), dtype=np.uint8)
        cv2.ellipse(mask, e1, 255, -1) # type: ignore
        cv2.ellipse(mask, e2, 255, -1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # Konturen der beiden Ellipsen herausfiltern

        # 5. Fit a new ellipse to the combined contours
        if len(contours) > 0:
            # Combine all points from all contours found
            all_points = np.vstack(contours)
            if len(all_points) >= 5: # Need at least 5 points to fit an ellipse
                new_ellipse = cv2.fitEllipse(all_points)
                
                # 6. Draw the new combined ellipse
                combined = cv2.ellipse(final, new_ellipse, (0, 255, 0), 2)
                cv2.ellipse(img, e1, (255,0,0),2)
                cv2.ellipse(img, e2, (255,0,0),2)

        return
