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
        time.sleep(1)
        average = frame.mean(axis=0).mean(axis=0)
        return ["ring " + str(average)]