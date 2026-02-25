from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.rtcrtpsender import RTCRtpSender
import av
from av import VideoFrame
import asyncio
from dronemaster.utils import log

pcs = set()

class UDPVideoTrack(VideoStreamTrack):
    def __init__(self, port):
        super().__init__()
        self.container = av.open(f"udp://0.0.0.0:{port}", format="h264", timeout=5)
        self.stream = self.container.streams.video[0]
        self.frame_iter = self._frame_generator() # we block when the drone does not send data, maybe fix?

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

        frame.pts = pts
        frame.time_base = time_base
        return frame



# ---- WebRTC  ----
async def offer(sdp, type, port):
    log(1)
    offer = RTCSessionDescription(
        sdp=sdp,
        type=type
    )
    log(2, offer)

    pc = RTCPeerConnection()
    pcs.add(pc)

    log(3)

    # --- Step 1: create a video transceiver ---
    transceiver = pc.addTransceiver("video", direction="sendonly")

    # --- Step 2: force H264 codec ---
    log(4)
    capabilities = RTCRtpSender.getCapabilities("video")
    h264_codecs = [c for c in capabilities.codecs if c.mimeType == "video/H264"]
    transceiver.setCodecPreferences(h264_codecs)
    log(5, h264_codecs)

    # --- Step 3: attach the track ---
    track = UDPVideoTrack(port=port)
    transceiver.sender.replaceTrack(track)

    log(6)
    # --- Standard negotiation ---
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    log(7, answer)
    await pc.setLocalDescription(answer)

    log(8)
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
