import sys

class VisionController:
    def __init__(self) -> None:
        self.target = None

        self.X_DEADZONE = 0.1
        self.Y_DEADZONE = 0.1

    def updateTarget(self, framex, framey, frame_shape, width, height):
        self.target = (framex / frame_shape[0], framey / frame_shape[1], width / height)
    
    def tickMove(self):
        if self.target is None:
            return
        target = self.target
        self.target = None

        x_diff = target[0] - 0.5 # positive => go right
        y_diff = 0.5 - target[1] # positive => go up

        if abs(x_diff) <= self.X_DEADZONE:
            x_diff = 0
        
        if abs(y_diff) <= self.Y_DEADZONE:
            y_diff = 0
        
        print("DIFF:", x_diff, y_diff)
        sys.stdout.flush()


