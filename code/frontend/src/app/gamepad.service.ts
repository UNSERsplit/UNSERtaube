import { Injectable, Signal, WritableSignal, signal } from '@angular/core';

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

  public gamepadConnected = signal(false);
  
  public mappedData: WritableSignal<MappedData> = signal({throttle: NaN, roll: NaN, pitch: NaN, yaw: NaN});
  public unmappedAxisData = signal<number[]>([]);
  public currentMapping: GamepadMapping = {throttle_axis_id: 0, roll_axis_id: 1, pitch_axis_id: 2, yaw_axis_id: 3};

  constructor() {
    window.addEventListener("gamepadconnected", (e) => {
      this.onConnect(e.gamepad);
      this.gamepadConnected.set(true)
    });

    window.addEventListener("gamepaddisconnected", (e) => {
      this.onDisconnect(e.gamepad);
      this.gamepadConnected.set(false);
    });
  }

  public tick() {
    if (!this.gamepad) return;
    const gp = navigator.getGamepads()[this.gamepad.index]!;

    this.unmappedAxisData.update(data => {
      if(data.toString() != gp.axes.toString()) {
        return [...gp.axes];
      }
      return data;
    })

    this.mappedData.update(mappedData => {
      const throttle = [
        mappedData.throttle,
        Math.floor(gp.axes[this.currentMapping.throttle_axis_id] * 100)
      ]

      const roll = [
        mappedData.roll,
        Math.floor(gp.axes[this.currentMapping.roll_axis_id] * 100)
      ]

      const pitch = [
        mappedData.pitch,
        Math.floor(gp.axes[this.currentMapping.pitch_axis_id] * 100)
      ]

      const yaw = [
        mappedData.yaw,
        Math.floor(gp.axes[this.currentMapping.yaw_axis_id] * 100)
      ]

      if(throttle[0] != throttle[1] || roll[0] != roll[1] || pitch[0] != pitch[1] || yaw[0] != yaw[1]) {
        return {
          throttle: throttle[1],
          roll: roll[1],
          pitch: pitch[1],
          yaw: yaw[1]
        }
      }
      return mappedData;
    });
  }

  private onConnect(gamepad: Gamepad) {
    this.gamepad = gamepad;
  }

  private onDisconnect(gamepad: Gamepad) {
    if (gamepad != this.gamepad) return;
    this.gamepad = null;
  }
}
