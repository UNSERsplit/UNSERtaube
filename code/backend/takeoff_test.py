import dronemaster
import asyncio

async def __main__():
    drone = dronemaster.Drone("192.168.43.49")

    await drone.connect()
    await asyncio.sleep(1)
    await drone.takeoff()
    await asyncio.sleep(1)
    await drone.land()
    await drone.disconnect()

dronemaster.start()

try:
    asyncio.run(__main__())
finally:
    dronemaster.stop()