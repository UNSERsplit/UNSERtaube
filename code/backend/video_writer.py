from av import VideoFrame
from typing import Optional
import av, av.container
import os

class VideoWriter:
    def __init__(self) -> None:
        self.container: Optional[av.container.OutputContainer] = None
        self.stream: Optional[av.VideoStream] = None
        self.base_dir = os.environ["VIDEO_BASE_DIR"]

    def start(self, filename_without_extention: str):
        path = f"{os.path.join(self.base_dir, filename_without_extention)}.mp4"
        self.container = av.open(path, "w", format="h264", options={
            "fflags": "nobuffer",
            "probesize": "32",
            "analyzeduration": "0",
        })
        self.stream = self.container.add_stream("h264")
        return path

    def end(self):
        if not self.container or not self.stream: return

        for packet in self.stream.encode(None):
            self.container.mux(packet)

        self.container.close()

    def feed(self, frame: VideoFrame):
        if not self.container or not self.stream: return
        
        for packet in self.stream.encode(frame):
            self.container.mux(packet)
