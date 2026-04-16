import dronemaster
import asyncio
import pygame
import av, av.error
import threading
import numpy as np

class FrameReader:
    def __init__(self, port) -> None:
        self.container = av.open(f"udp://0.0.0.0:{port}", timeout=(5, None))
        self.frame = None
        self.stopped = False

        self.thread = threading.Thread(target=self._update_frame, daemon=True)
    
    def start(self):
        self.thread.start()
    
    def _update_frame(self):
        try:
            for frame in self.container.decode(video=0):
                self.frame = np.array(frame.to_image())
                if self.stopped:
                    self.container.close()
                    break
        except av.error.ExitError:
            print('Do not have enough frames for decoding, please try again or increase video fps before get_frame_read()')

async def __main__():
    drone = dronemaster.Drone("192.168.43.49")

    await drone.connect()

    #await drone.connection.send_control_message("motoron")

    await drone.ext.led_set(0, 0, 15)
    await drone.startstream()

    reader = FrameReader(drone.get_video_port())
    reader.start()

    window = pygame.display.set_mode((640,480))

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            frame = reader.frame
            if frame is None:
                continue
            video_surf = pygame.image.frombuffer(
                frame.tobytes(), frame.shape[1::-1], "RGB")
            
            window.blit(video_surf, (0, 0))
            pygame.display.flip()
    finally:
        reader.stopped = True
        pygame.quit()
        await drone.disconnect()

dronemaster.start()

try:
    asyncio.run(__main__())
finally:
    dronemaster.stop()