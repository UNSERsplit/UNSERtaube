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
        self.saturation_lower = 70

    def on_frame(self, frame):
        processed_frame = self._process_frame(frame)

        if self.show_filtered_frame:
            return processed_frame
        else:
            return frame
    
    def _process_frame(self, frame):

        img = cv2.bilateralFilter(frame, 11, 75, 75)

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

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel, iterations=20)

        ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours

        final = cv2.drawContours(cv2.bitwise_and(frame, frame, mask=raw_mask), ctns, -1, (0,255,0), 3)

        return final