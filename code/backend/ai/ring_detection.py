import cv2

from ai.ai import Module
import time
import numpy as np

class Ring_Module(Module):
    def __init__(self) -> None:
        super().__init__(self.frame)
    
    def enable(self):
        print("Ring enable")
        return super().enable()
    
    def disable(self):
        print("Ring disable")
        return super().disable()
    
    @staticmethod
    def frame(frame: np.ndarray) -> list:
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
            return []
        
        contour = np.vstack(contours)

        if len(contour) < 2:
            return []
        
        cv2.drawContours(frame, [contour], -1, (30, 30, 30), 3)

        if len(contour) < 5:
            return []
        
        if len(contour) > 600:
            color = (0,255,0)
        else:
            color = (255,0,0)
        

        ellipse = cv2.fitEllipse(contour)
        (cx, cy), (minor_axis, major_axis), angle = ellipse

        axis_ratio = min(minor_axis, major_axis) / max(major_axis, minor_axis, 1)
        tilt = np.degrees(np.arccos(np.clip(axis_ratio, 0, 1)))

        radius = (minor_axis + major_axis)
        
        return [{
                    "type":"ring",
                    "accuracy":len(contour),
                    "center": [cx,cy],
                    "axis": [minor_axis, major_axis],
                    "tilt": tilt,
                    "angle": angle,
                    "radius": radius
                }]