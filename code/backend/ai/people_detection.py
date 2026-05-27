import cv2

from ai.ai import Module
import time
import numpy as np
from ultralytics import YOLO

class People_Module(Module):
    def __init__(self) -> None:
        model = YOLO('yolov8s.pt')
        model.load('yolov8s.pt')
        super().__init__(self.frame, model)
    
    def enable(self):
        print("People enable")
        return super().enable()
    
    def disable(self):
        print("People disable")
        return super().disable()
    
    @staticmethod
    def frame(frame: np.ndarray, model: YOLO) -> list:
        FACTOR = 2
        frame = cv2.resize(frame, (frame.shape[0] // FACTOR, frame.shape[1] // FACTOR))
        results = model.predict(frame)
        if not results[0].boxes:
            return []
        boxes_data = results[0].boxes.data

        detected_objects = []
        for row in boxes_data:
            x1, y1, x2, y2, _, d = map(lambda a: int(a * FACTOR), row)
            if d == 0: #person
                detected_objects.append({
                    "type":"person",
                    "cords": [x1, y1, x2, y2]
                })
    

        return detected_objects