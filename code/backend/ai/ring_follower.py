from dronemaster import Drone

import numpy as np
import time
import json
import os

from .debug_thread import Debug_Thread


class PID:
    def __init__(self, kp: float, ki: float, kd: float,
                 output_limit: float = 100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit = output_limit
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.time()

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.time()

    def compute(self, error: float) -> float:
        now = time.time()
        dt = max(now - self._prev_time, 1e-4)

        self._integral += error * dt
        derivative = (error - self._prev_error) / dt

        p_term = self.kp * error
        i_term = self.ki * self._integral
        d_term = self.kd * derivative

        output = p_term + i_term + d_term

        if abs(output) >= self.limit:
            self._integral -= error * dt

        output = float(np.clip(output, -self.limit, self.limit))

        self._prev_error = error
        self._prev_time = now
        return output


class Ring_Follower:
    def __init__(self, drone: Drone) -> None:
        self.drone = drone
        self.state = "SEARCH"


        self.roll =     PID(0.06, 0.00, 0.02)
        self.throttle = PID(0.09, 0.00, 0.02)
        self.pitch =    PID(0.02, 0.00, 0.00)
        self.yaw =      PID(0.12, 0.00, 0.00)

        self.last_seen_frame = None
        self.centre_hold_start = None
        self.fly_through_start = None

        self.debug = Debug_Thread()

    async def enable(self):
        self.state = "SEARCH"
        self.roll.reset()
        self.throttle.reset()
        self.pitch.reset()
        self.yaw.reset()
        self.fly(
            roll=0,
            pitch=0,
            throttle=0,
            yaw=0
        )

        self.debug.start()
        await self.drone.flight.takeoff()

    async def disable(self):
        await self.drone.flight.stop()
        await self.drone.flight.land()

        self.debug.stop()
    
    
    async def on_new_pos(self, detections, drone_state: dict):
        if detections:
            self.last_seen_frame = time.time()
            if detections[0]["accuracy"] < 500:
                detections = []
        
        TARGET_RADIUS_RATIO = 0.35
        TILT_YAW_GAIN       = 0.5
        CENTRE_THRESHOLD_PX = 30
        CENTRE_HOLD_TIME    = 1.5
        FLY_THROUGH_TIME    = 2.0
        FLY_THROUGH_PITCH   = 50 
        
        match self.state:
            case "SEARCH":
                if not detections:
                    self.fly(
                        roll=0,
                        pitch=0,
                        throttle=0,
                        yaw=20
                    )
                else:
                    self.state = "ALIGN"
                    self.roll.reset()
                    self.throttle.reset()
                    self.pitch.reset()
                    self.yaw.reset()
                    self.fly(
                        roll=0,
                        pitch=0,
                        throttle=0,
                        yaw=0
                    )
            case "ALIGN":
                if not detections:
                    if self.last_seen_frame is not None and time.time() - self.last_seen_frame > 5:
                        self.state = "SEARCH"
                    self.fly(
                        roll=0,
                        pitch=0,
                        throttle=0,
                        yaw=0
                    )
                else:
                    cx, cy = detections[0]["center"]
                    r      = detections[0]["radius"]
                    tilt   = detections[0]["tilt"]
                    angle  = detections[0]["angle"]
                    target_r = TARGET_RADIUS_RATIO * min(720, 960)
                    print(r, target_r)

                    err_x = cx - 960 / 2
                    err_y = 720 / 3 - cy # oberes drittel
                    
                    err_size = target_r - r

                    yaw_cmd = 0.0
                    yaw_error = 0
                    if tilt > 15:
                        yaw_error = (angle - 90.0)
                        yaw_cmd = self.yaw.compute(yaw_error * TILT_YAW_GAIN)

                    self.debug.plot(err_x, err_y, err_size, yaw_error)

                    roll_cmd     = self.roll.compute(err_x)
                    throttle_cmd = self.throttle.compute(err_y)
                    pitch_cmd = self.pitch.compute(err_size)

                    self.fly(roll=roll_cmd, pitch=pitch_cmd, throttle=throttle_cmd, yaw=0)

                    centred = (abs(err_x) < CENTRE_THRESHOLD_PX
                               and abs(err_y) < CENTRE_THRESHOLD_PX)

                    #if centred:
                    #    if self.centre_hold_start is None:
                    #        self.centre_hold_start = time.time()
                    #    elif time.time() - self.centre_hold_start >= CENTRE_HOLD_TIME:
                    #        self.fly_through_start = time.time()
                    #        self.state = "FLY"
                    #else:
                    #    self.centre_hold_start = None
            case "FLY":
                assert self.fly_through_start is not None
                elapsed = time.time() - self.fly_through_start
                if elapsed < FLY_THROUGH_TIME:
                    self.fly(throttle=0, yaw=0,
                        pitch=FLY_THROUGH_PITCH, roll=0)
                else:
                    self.fly(throttle=0, yaw=0, pitch=0, roll=0)
                    self.roll.reset()
                    self.throttle.reset()
                    self.pitch.reset()
                    self.yaw.reset()
                    self.centre_hold_start = None
                    self.state = "SEARCH"
    
    def fly(self, roll, pitch, throttle, yaw):
        for _ in range(3):
            self.drone.flight.rc(roll, pitch, throttle, yaw)