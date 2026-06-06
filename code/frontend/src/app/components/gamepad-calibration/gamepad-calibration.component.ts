import { Component, effect, inject, OnInit, signal } from '@angular/core';
import { GamepadMapping, GamepadService } from '../../service/gamepad.service';
import { ButtonComponent } from '../button/button.component';
import { ButtonVariants } from '../button/button.variants';
import { MatDialog } from '@angular/material/dialog';

const STEPS = [
  "Move all sticks a bit and then center all",
  "Move the throttle stick to 100%",
  "Move the throttle stick back to center",
  "Move the roll stick to 100%",
  "Move the roll stick back to center",
  "Move the pitch stick to 100%",
  "Move the pitch stick back to center",
  "Move the yaw stick to 100%",
  "Move the yaw stick back to center",
  "All done, is this correct?"
]

@Component({
  selector: 'app-gamepad-calibration',
  imports: [
    ButtonComponent
  ],
  templateUrl: './gamepad-calibration.component.html',
  styleUrl: './gamepad-calibration.component.css'
})
export class GamepadCalibrationComponent implements OnInit{
  protected ButtonVariants = ButtonVariants;
  protected gp: Gamepad | null = null;
  protected service = inject(GamepadService);

  protected stepNumber = signal(1)
  protected stepText = signal("")

  private nonZeroAxis: number[] = [];
  private nonZeroButtons: number[] = [];

  private dialog = inject(MatDialog);

  private mapping: GamepadMapping = {
    throttle: {
      type: "axis",
      index: -1
    },
    roll: {
      type: "axis",
      index: -1
    },
    pitch: {
      type: "axis",
      index: -1
    },
    yaw: {
      type: "axis",
      index: -1
    },
  }

  constructor() {
    effect(() => {
      this.stepText.set(STEPS[this.stepNumber() - 1]);
    })

    effect(() => {
      const d = this.service.unmappedData();

      const find100 = () => {
        let double = false;
        let axisId = -1;
        let btnId = -1;

        d.axes.forEach((axis, index) => {
          if(axis > 0.9) {
            if(axisId == -1) {
              axisId = index;
            } else {
              double = true;
            }
          }
        })

        d.buttons.forEach((btn, index) => {
          if(btn > 0.8) {
            if(btnId == -1) {
              btnId = index;
            } else {
              double = true;
            }
          }
        })

        if (btnId != -1 && axisId != -1) {
          double = true;
        }

        if (double) {
          alert("Only move one stick to 100%")
          return [null, -1];
        }

        if(axisId != -1) {
          return ["axis", axisId];
        }
        
        if(btnId != -1) {
          return ["button", btnId];
        }

        return [null, -1];
      }

      d.axes.forEach((axis, index) => {
        if (axis != 0 && !this.nonZeroAxis.includes(index)) {
          this.nonZeroAxis.push(index);
        }
      })

      d.buttons.forEach((btn, index) => {
        if(btn != 0 && !Number.isNaN(btn) && !this.nonZeroButtons.includes(index)) {
          this.nonZeroButtons.push(index);
        }
      })

      if ([1,3,5,7,9].includes(this.stepNumber())) { // center all
        let centered = true;
        let centeredCount = 0;

        console.log("Start center")

        d.axes.forEach((axis, index) => {
          if(!this.nonZeroAxis.includes(index)) return; // ignore all axes that have always been 0

          if(Math.abs(axis) > 0.1) {
            console.log(index, "failed center axis")
            centered = false;
          } else {
            centeredCount++;
          }
        });

        d.buttons.forEach((btn, index) => {
          if(!this.nonZeroButtons.includes(index)) return;

          if(Math.abs(btn - 0.5) > 0.1) {
            console.log(index, "failed center btn")
            centered = false;
          } else {
            centeredCount++;
          }
        })

        console.log("Centered", centered, centeredCount)

        if(centeredCount >= 4 && centered) {
          this.stepNumber.update(s => s + 1);
        }
      }

      if (this.stepNumber() == 2) {
        const [type, index] = find100();
        if (type != null) {
          this.mapping.throttle = {
            type: type as "button" | "axis",
            index: index as number
          }

          this.stepNumber.set(3);
        }
      }

      if (this.stepNumber() == 4) {
        const [type, index] = find100();
        if (type != null) {
          this.mapping.roll = {
            type: type as "button" | "axis",
            index: index as number
          }

          this.stepNumber.set(5);
        }
      }

      if (this.stepNumber() == 6) {
        const [type, index] = find100();
        if (type != null) {
          this.mapping.pitch = {
            type: type as "button" | "axis",
            index: index as number
          }

          this.stepNumber.set(7);
        }
      }

      if (this.stepNumber() == 8) {
        const [type, index] = find100();
        if (type != null) {
          this.mapping.yaw = {
            type: type as "button" | "axis",
            index: index as number
          }

          this.stepNumber.set(9);
        }
      }

      if(this.stepNumber() == 10) {
        this.service.currentMapping = this.mapping
      }
    })
  }



  ngOnInit(): void {
    this.gp = this.service.gamepad;
  }

  retry() {
    this.stepNumber.set(1);
    this.mapping = {
      throttle: {
        type: "axis",
        index: -1
      },
      roll: {
        type: "axis",
        index: -1
      },
      pitch: {
        type: "axis",
        index: -1
      },
      yaw: {
        type: "axis",
        index: -1
      },
    }
    this.nonZeroAxis = []
    this.nonZeroButtons = []
    this.service.currentMapping = null;
  }

  accept() {
    this.service.createKnownMapping(this.gp!.id, this.mapping)
    this.dialog.closeAll()
  }
}
