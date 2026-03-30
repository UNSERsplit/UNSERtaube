import dronemaster
import asyncio

async def __main__():
    drone = dronemaster.Drone("192.168.43.49")

    await drone.connect()

    await drone.ext.led_set(0, 255, 255)

    await drone.takeoff()


    await drone.ext.led_pulse(255, 255, 255, 0.1)

    await asyncio.sleep(1.5)

    await drone.ext.led_flash(0, 255, 0, 1.0, 0, 0, 255)

    await drone.land()
    await drone.disconnect()

dronemaster.start()

try:
    asyncio.run(__main__())
finally:
    dronemaster.stop()