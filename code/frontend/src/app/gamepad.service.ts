import { Injectable, WritableSignal, signal } from '@angular/core';

export interface GamepadMapping {
  throttle_axis_id: number,
  roll_axis_id: number,
  pitch_axis_id: number,
  yaw_axis_id: number
}

export interface MappedData { // alles von -100 bis 100
  throttle: number,
  roll: number,
  pitch: number,
  yaw: number
}

@Injectable({
  providedIn: 'root'
})
export class GamepadService {
  private gamepad: Gamepad | null = null;
  
  public mappedData: WritableSignal<MappedData> = signal({throttle: NaN, roll: NaN, pitch: NaN, yaw: NaN});
  public currentMapping: GamepadMapping = {throttle_axis_id: 0, roll_axis_id: 1, pitch_axis_id: 2, yaw_axis_id: 3};

  constructor() {
    window.addEventListener("gamepadconnected", (e) => {
      this.onConnect(e.gamepad);
    });

    window.addEventListener("gamepaddisconnected", (e) => {
      this.onDisconnect(e.gamepad);
    });
  }

  public tick() {
    if (!this.gamepad) return;

    this.mappedData.set({
      throttle: this.gamepad.axes[this.currentMapping.throttle_axis_id] * 100,
      roll: this.gamepad.axes[this.currentMapping.roll_axis_id] * 100,
      pitch: this.gamepad.axes[this.currentMapping.pitch_axis_id] * 100,
      yaw: this.gamepad.axes[this.currentMapping.yaw_axis_id] * 100,
    })
  }

  private onConnect(gamepad: Gamepad) {
    this.gamepad = gamepad;
  }

  private onDisconnect(gamepad: Gamepad) {
    if (gamepad != this.gamepad) return;
    this.gamepad = null;
  }
}
