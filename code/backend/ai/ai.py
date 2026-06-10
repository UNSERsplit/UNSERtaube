from multiprocessing import Process, Queue, Pipe
from multiprocessing.connection import Connection
from abc import ABC, abstractmethod
from dronemaster import Drone

import cv2
import threading
import time
import os

class FastStream: # danke gemini
    def __init__(self, url):
        # 1. FIX THE STARTUP HANG: Force instant connection
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
            "rtsp_transport;udp|"
            "fflags;nobuffer|"
            "flags;low_delay|"
            "probesize;32|"         # Stop analyzing massive chunks of data
            "analyzeduration;0"     # Stop waiting to figure out the framerate
        )

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
    def __init__(self, frame_func, *extra_args) -> None:
        self.enabled = False
        self.detections = []
        self.frame_func = frame_func
        self.extra_args = extra_args
        self.process: Process = None # type: ignore
        self.pipe: Connection = None # type: ignore

    def enable(self) -> None:
        if self.enabled:
            raise ValueError("Already turned on")
        self.enabled = True

        parent, child = Pipe()
        self.process = Process(
            target=self._target,
            args=(self.frame_func, child, self.extra_args)
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

        print(f"waiting on child to exit")
        self.process.join(3)
        print("Exited")
        
    
    @staticmethod
    def _target(frame_func, pipe: Connection, extra_args: list) -> None:
        print("Connecting to stream")
        stream = FastStream("rtsp://127.0.0.1:8554/camera")
        print("Connected to stream")
        while not pipe.poll() and not pipe.closed:
            if stream.new_frame_ready and stream.frame is not None:
                stream.new_frame_ready = False

                frame = stream.frame

                t = time.time()
                detections = frame_func(frame, *extra_args)
                #print(f"T:{time.time() - t}")

                if not pipe.closed:
                    try:
                        pipe.send(detections)
                    except BrokenPipeError:
                        print("Pipe closed")
                        break
                time.sleep(1/30)
        stream.stop()
        try:
            pipe.close()
        except BrokenPipeError:
            pass
        

    def get_detections(self) -> list:
        if self.enabled:
            while self.pipe.poll():
                self.detections = self.pipe.recv()
        return self.detections
    
from .people_detection import People_Module
from .ring_detection import Ring_Module
from .ring_follower import Ring_Follower

class AI_Module:
    def __init__(self, drone: Drone) -> None:
        self.people = People_Module()
        self.ring = Ring_Module()
        self.follower = Ring_Follower(drone)
    
    async def on_disconnect(self):
        if self.people.enabled:
            self.people.disable()
        if self.ring.enabled:
            self.ring.disable()
            await self.follower.disable()

    async def set_people_detection(self, on: bool):
        if on:
            self.people.enable()
        else:
            self.people.disable()

    async def set_ring_detection(self, on: bool):
        if on:
            self.ring.enable()
            await self.follower.enable()
        else:
            self.ring.disable()
            await self.follower.disable()

    async def get_detections(self, state: dict):
        ring = self.ring.get_detections()
        if self.ring.enabled:
            await self.follower.on_new_pos(ring, state)
        return ring + self.people.get_detections()