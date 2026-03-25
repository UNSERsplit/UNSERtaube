import dronemaster
import asyncio

async def __main__():
    drone = dronemaster.Drone("192.168.43.49")

    await drone.connect()
    i = input(">")
    while i != "exit":
        drone.connection.send_message_noanswer(i)
        i = input(">")
    
    await drone.disconnect()

dronemaster.start()

try:
    asyncio.run(__main__())
finally:
    dronemaster.stop()