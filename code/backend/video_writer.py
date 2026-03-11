from av import VideoFrame
from typing import Optional
import av, av.container
import os
import subprocess

class VideoWriter:
    def __init__(self) -> None:
        self.container: Optional[av.container.OutputContainer] = None
        self.stream: Optional[av.VideoStream] = None
        self.target_name: str = ""
        self.original_name: str = ""
        self.base_dir = os.environ["VIDEO_BASE_DIR"]
        self.original_base_dir = "/tmp"

    def start(self, filename_without_extention: str):
        self.original_name = f"{filename_without_extention}.h264"
        self.target_name = f"{filename_without_extention}.mp4"
        path = os.path.join(self.original_base_dir, self.original_name)
        self.container = av.open(path, "w", format="h264", options={ # it saves correctly but browsers dont like raw h264
            "fflags": "nobuffer",
            "probesize": "32",
            "analyzeduration": "0"
        })
        self.stream = self.container.add_stream("h264")
        return self.target_name
    
    def end(self):
        if not self.container or not self.stream: return

        for packet in self.stream.encode(None):
            self.container.mux(packet)

        self.container.close()

        self.convert()

        return self.target_name
    
    def convert(self):
        p = subprocess.Popen(["/usr/bin/ffmpeg", "-i", os.path.join(self.original_base_dir, self.original_name), "-c", "copy", os.path.join(self.base_dir, self.target_name)], stdout=subprocess.PIPE)
        if p.wait() != 0:
            print("ffmpeg exited with", p.returncode)

    def feed(self, frame: VideoFrame):
        if not self.container or not self.stream: return
        
        for packet in self.stream.encode(frame):
            self.container.mux(packet)
