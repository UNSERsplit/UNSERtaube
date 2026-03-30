import dronemaster
import asyncio

IP = "192.168.43.49"
#IP = "192.168.0.104"
#IP = "10.225.62.132" # David

async def __main__():
    drone = dronemaster.Drone(IP)

    await drone.connect()
    i = input(">")
    while i != "exit":
        if i.startswith("rc") or i.startswith("emergency") or i.startswith("keepalive") or i.startswith("reboot"):
            drone.connection.send_message_noanswer(i)
        else:
            print(await drone.connection.send_raw_message(i, timeout=20, repeat=0))
        i = input(">")
    
    await drone.disconnect()

dronemaster.start()

try:
    asyncio.run(__main__())
finally:
    dronemaster.stop()