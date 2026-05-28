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
        lower_red1 = np.array([0,   100,  70])
        upper_red1 = np.array([10,  255, 255])
        lower_red2 = np.array([170, 100,  70])
        upper_red2 = np.array([180, 255, 255])

        mask = (cv2.inRange(hsv, lower_red1, upper_red1)
                | cv2.inRange(hsv, lower_red2, upper_red2)) # type: ignore

        # Clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []

        # Need at least 5 points to fit an ellipse
        candidates = [cnt for cnt in contours
                    if len(cnt) >= 5 and cv2.contourArea(cnt) > 500]
        if not candidates:
            return []

        # Score each candidate: prefer large, ellipse-like contours
        best = None
        best_score = 0.0
        for cnt in candidates:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            # Ellipse-aware circularity: a perfect ellipse has circularity
            # π*a*b / (approximate perimeter)^2 * 4π — but simpler to just
            # check how well the ellipse fit matches the contour.
            ellipse = cv2.fitEllipse(cnt)
            (ecx, ecy), (ma, MA), angle = ellipse

            # Ratio of contour area to fitted ellipse area
            ellipse_area = np.pi * (ma / 2) * (MA / 2)
            if ellipse_area == 0:
                continue
            fill_ratio = area / ellipse_area  # ~1.0 for a solid ellipse

            # For a ring (hollow), the fill ratio will be less than 1.
            # But the outer contour should still match the ellipse shape well.
            # Use Hu-moment matching or just accept fill_ratio > 0.3
            if fill_ratio < 0.2 or fill_ratio > 1.5:
                continue

            # Reject very elongated shapes (aspect ratio > 4:1 is not a ring)
            aspect = max(ma, MA) / max(min(ma, MA), 1)
            if aspect > 4.0:
                continue

            score = area * (1.0 / (1.0 + abs(1.0 - fill_ratio)))
            if score > best_score:
                best_score = score
                best = (cnt, ellipse)

        if best is None:
            return []

        cnt, ellipse = best
        (cx, cy), (minor_axis, major_axis), angle = ellipse
        h, w = frame.shape[:2]

        # Estimate tilt: a circle viewed at angle θ from normal becomes an
        # ellipse with minor/major = cos(θ)
        axis_ratio = min(minor_axis, major_axis) / max(major_axis, minor_axis, 1)
        tilt_rad = np.arccos(np.clip(axis_ratio, 0, 1))
        tilt_deg = np.degrees(tilt_rad)

        radius = (minor_axis + major_axis)


        angle = np.radians(angle)

        # Half-extents of the bounding box of a rotated ellipse:
        # extent_x = sqrt((a*cos θ)² + (b*sin θ)²)
        # extent_y = sqrt((a*sin θ)² + (b*cos θ)²)
        extent_x = np.sqrt((major_axis * np.cos(angle))**2 + (minor_axis * np.sin(angle))**2)
        extent_y = np.sqrt((major_axis * np.sin(angle))**2 + (minor_axis * np.cos(angle))**2)

        x = int(cx - extent_x)
        y = int(cy - extent_y)
        w = int(2 * extent_x)
        h = int(2 * extent_y)

        return [{
                    "type":"ring",
                    "cords": [x,y,x+w,y+h]
                }]