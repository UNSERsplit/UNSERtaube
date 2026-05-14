from typing import TypedDict, Dict

import math

class TelemetryData(TypedDict):
    connected: bool
    pitch: int
    roll: int
    yaw: int
    vgx: int
    vgy: int
    vgz: int
    templ: int
    temph: int
    tof: int
    h: int
    bat: int
    baro: float
    time: int
    agx: float
    agy: float
    agz: float
    last_update: float
    delta: float

class StateComputation:
    def __init__(self) -> None:
        self.posx = 0
        self.posy = 0
        self.posz = 0
        self.distance = 0

    def on_state(self, tele: TelemetryData) -> Dict:
        state = dict(tele)

        state["speed"] = math.sqrt(tele["vgx"] ** 2 + tele["vgy"] ** 2 + tele["vgz"] ** 2)

        agx, agy, agz = self.remove_gravity(tele["roll"], tele["pitch"], tele["yaw"], tele["agx"], tele["agy"], tele["agz"])
        agx, agy, agz = self.local_to_global(tele["roll"], tele["pitch"], tele["yaw"], agx, agy, agz)

        state["agx"] = agx
        state["agy"] = agy
        state["agz"] = agz

        self.posx += tele["vgx"] * tele["delta"]
        self.posy += tele["vgy"] * tele["delta"]
        self.posz += tele["vgz"] * tele["delta"]

        state["posx"] = self.posx
        state["posy"] = self.posy
        state["posz"] = self.posz

        self.distance += math.sqrt((tele["vgx"] * tele["delta"]) ** 2 + (tele["vgy"] * tele["delta"]) ** 2 + (tele["vgz"] * tele["delta"]) ** 2)

        state["distance"] = self.distance

        return state
    
    def local_to_global(self, roll, pitch, yaw, lx, ly, lz): # danke gemini
        pitch = math.radians(pitch)
        roll = math.radians(roll)
        yaw = math.radians(yaw)

        # 1. Rotate around Roll (X-axis)
        # 2. Rotate around Pitch (Y-axis)
        # 3. Rotate around Yaw (Z-axis)
        
        # Pre-calculate trig values for performance
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)
        cy, sy = math.cos(yaw), math.sin(yaw)

        # Standard Rotation Matrix (Z-Y-X order)
        # This calculates the Global X, Y, and Z
        gx = lx * (cy * cp) + \
            ly * (cy * sp * sr - sy * cr) + \
            lz * (cy * sp * cr + sy * sr)

        gy = lx * (sy * cp) + \
            ly * (sy * sp * sr + cy * cr) + \
            lz * (sy * sp * cr - cy * sr)

        gz = lx * (-sp) + \
            ly * (cp * sr) + \
            lz * (cp * cr)
        
        return gx, gy, gz
    
    def remove_gravity(self, roll, pitch, yaw, ax, ay, az):
        p = math.radians(pitch)
        r = math.radians(roll)
        y = math.radians(yaw)

        g = 1010

        agx = ax - (g * math.sin(p))
        agy = ay + (g * math.sin(r) * math.cos(p))
        agz = az + (g * math.cos(r) * math.cos(p))

        return agx, agy, agz