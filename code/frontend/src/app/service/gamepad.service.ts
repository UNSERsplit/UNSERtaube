import { Injectable, Signal, WritableSignal, effect, inject, signal } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GamepadCalibrationComponent } from '../components/gamepad-calibration/gamepad-calibration.component';

export interface GamepadMapping {
  throttle: GamepadAxisButtonMapping,
  roll: GamepadAxisButtonMapping,
  pitch: GamepadAxisButtonMapping,
  yaw: GamepadAxisButtonMapping
}

export interface GamepadAxisButtonMapping {
  type: "axis" | "button",
  index: number,
  invert: boolean
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
  public gamepad: Gamepad | null = null;

  public gamepadConnected = signal(false);
  
  public mappedData: WritableSignal<MappedData> = signal({throttle: 0, roll: 0, pitch: 0, yaw: 0});
  public unmappedData = signal<{axes: ReadonlyArray<number>, buttons: ReadonlyArray<number>}>({axes: [], buttons: []});
  public currentMapping: GamepadMapping | null = null;

  private dialog = inject(MatDialog);
  private knownMappings: {[index: string]: GamepadMapping} = {}

  constructor() {
    const _raw = localStorage.getItem("knownMappings");
    if (_raw != null) {
      this.knownMappings = JSON.parse(_raw)
    }

    window.addEventListener("gamepadconnected", (e) => {
      this.onConnect(e.gamepad);
      this.gamepadConnected.set(true)
    });

    window.addEventListener("gamepaddisconnected", (e) => {
      this.onDisconnect(e.gamepad);
      this.gamepadConnected.set(false);
    });

    setInterval(() => {
      this.tick()
    }, 10);
  }

  private tick() {
    if (!this.gamepad) return;
    const gp = navigator.getGamepads()[this.gamepad.index]!;
    if(!gp) return;

    this.unmappedData.update(origData => {
      const btns = gp.buttons.map(btn => btn.touched ? btn.value : NaN);

      if(origData.axes.toString() == gp.axes.toString() && origData.buttons.toString() == btns.toString()) {
        return origData;
      }

      return {
        axes: gp.axes,
        buttons: btns
      }
    })

    this.mappedData.update(old => {
      if (this.currentMapping == null) {
        return old;
      }

      const map = (mapping: GamepadAxisButtonMapping) => {
        if(mapping.type == "axis") {
          return Math.floor(gp.axes[mapping.index] * 100) * (mapping.invert ? -1 : 1)
        } else if(mapping.type == "button") {
          const btn = gp.buttons[mapping.index];
          //console.log(btn.pressed, btn.touched, btn.value)
          return btn.value != 0 ? Math.floor((btn.value - 0.5) * 200) * (mapping.invert ? -1 : 1) : 0
        } else {
          throw new Error("Nope");
        }
      }

      const newData = {
        throttle: map(this.currentMapping.throttle),
        roll: map(this.currentMapping.roll),
        pitch: map(this.currentMapping.pitch),
        yaw: map(this.currentMapping.yaw)
      }

      let name: keyof typeof newData;
      for (name in newData) {
        if(!Number.isNaN(newData[name]) && newData[name] != old[name]) {
          return newData;
        }
      }

      return old;
    })
  }

  private onConnect(gamepad: Gamepad) {
    this.gamepad = gamepad;

    if(this.knownMappings[gamepad.id] !== undefined) {
      this.currentMapping = this.knownMappings[gamepad.id]
    } else {
      this.currentMapping = null;

      this.dialog.open(GamepadCalibrationComponent,
        {
          width: 'auto',
          height: 'auto',
          minHeight: 'auto',
          panelClass: [],
          maxWidth: 'none',
          maxHeight: 'none',
          disableClose: true
        });
    }
  }

  private onDisconnect(gamepad: Gamepad) {
    if (gamepad != this.gamepad) return;
    this.gamepad = null;
  }

  public createKnownMapping(id: string, mapping: GamepadMapping) {
    this.knownMappings[id] = mapping;
    localStorage.setItem("knownMappings", JSON.stringify(this.knownMappings))
  }
}
