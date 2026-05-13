from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer
from aiortc.rtcrtpsender import RTCRtpSender
import av
from av import VideoFrame
import asyncio
from dronemaster.utils import log

pcs = set()

class UDPVideoTrack(VideoStreamTrack):
    def __init__(self, port):
        super().__init__()
        self.container = av.open(f"udp://0.0.0.0:{port}", format="h264", timeout=5, options={
            "fflags": "nobuffer",
            "flags": "low_delay",
            "probesize": "32",
            "analyzeduration": "0",
        })
        self.stream = self.container.streams.video[0]
        self.frame_iter = self._frame_generator()
        self.frame_callback = None

    def _frame_generator(self):
        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                yield frame

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        try:
            frame: VideoFrame = next(self.frame_iter) # type: ignore
        except StopIteration:
            await asyncio.sleep(0.01)
            return await self.recv()
        except TimeoutError as e:
            log("ERROR", "Video Timeout")
            raise e

        frame.pts = pts
        frame.time_base = time_base

        if self.frame_callback:
            self.frame_callback(frame)

        return frame
    
    def stop(self) -> None: # TODO fix with no image after reconnect to same drone, requires restart of drone...
        super().stop()
        self.container.close()

def force_codec(pc: RTCPeerConnection, sender: RTCRtpSender, forced_codec: str) -> None:
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )

# ---- WebRTC  ----
async def offer(sdp, type, port):
    offer = RTCSessionDescription(
        sdp=sdp,
        type=type
    )

    pc = RTCPeerConnection()
    pcs.add(pc)


    # --- Step 3: attach the track ---
    track = UDPVideoTrack(port=port)
    #track = VideoStreamTrack()
    video_sender = pc.addTrack(track)


    force_codec(pc, video_sender,"video/H264")
    # --- Standard negotiation ---
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "track": track
    }
