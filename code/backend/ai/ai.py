from multiprocessing import Process, Queue, Pipe
from multiprocessing.connection import Connection
from abc import ABC, abstractmethod

import cv2
import threading
import time
import os

# 1. FIX THE STARTUP HANG: Force instant connection
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;udp|"
    "fflags;nobuffer|"
    "flags;low_delay|"
    "probesize;32|"         # Stop analyzing massive chunks of data
    "analyzeduration;0"     # Stop waiting to figure out the framerate
)

class FastStream: # danke gemini
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

class Module(ABC):
    def __init__(self, frame_func) -> None:
        self.enabled = False
        self.detections = []
        self.frame_func = frame_func
        self.process: Process = None # type: ignore
        self.pipe: Connection = None # type: ignore

    def enable(self) -> None:
        if self.enabled:
            raise ValueError("Already turned on")
        self.enabled = True

        parent, child = Pipe()
        self.process = Process(
            target=self._target,
            args=(self.frame_func, child)
        )
        self.pipe = parent
        self.process.start()
        

    def disable(self) -> None:
        if not self.enabled:
            raise ValueError("Already turned off")
        self.enabled = False
        self.detections = []

        self.pipe.send("exit")
        self.pipe.close()

        print(f"waiting on child to exit {self.__qualname__}")
        self.process.join(3)
        print("Exited")
        
    
    @staticmethod
    def _target(frame_func, pipe: Connection) -> None:
        stream = FastStream("rtsp://127.0.0.1:8554/camera")
        while not pipe.poll() and not pipe.closed:
            if stream.new_frame_ready and stream.frame is not None:
                stream.new_frame_ready = False

                frame = stream.frame

                detections = frame_func(frame)

                pipe.send(detections)
        pipe.close()

    def get_detections(self) -> list:
        if self.enabled:
            if self.pipe.poll():
                self.detections = self.pipe.recv()
                print("Detected")
        return self.detections
    
from .people_detection import People_Module
from .ring_detection import Ring_Module

class AI_Module:
    def __init__(self) -> None:
        self.people = People_Module()
        self.ring = Ring_Module()
    
    def on_disconnect(self):
        if self.ring.enabled:
            self.ring.disable()
        if self.people.enabled:
            self.people.disable()

    def set_people_detection(self, on: bool):
        if on:
            self.people.enable()
        else:
            self.people.disable()

    def set_ring_detection(self, on: bool):
        if on:
            self.ring.enable()
        else:
            self.ring.disable()

    def get_detections(self):
        return self.ring.get_detections() + self.people.get_detections()