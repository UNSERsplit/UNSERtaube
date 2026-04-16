import { Component, effect, HostListener, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { ControllerApiService } from '../../controller-api.service';
import { GamepadService } from '../../gamepad.service';

@Component({
  selector: 'app-controller-input',
  imports: [],
  template: "",
  styleUrl: './controller-input.component.css'
})
export class ControllerInputComponent implements OnInit, OnDestroy{
  ngOnInit(): void {
    this.gamepadService.currentMapping = {throttle_axis_id: 1, roll_axis_id: 0, pitch_axis_id: 4, yaw_axis_id: 2}

    setInterval(() => {
      this.gamepadService.tick()
    }, 10);
  }
  ngOnDestroy(): void {
    
  }

  private controllerApi = inject(ControllerApiService);
  private gamepadService = inject(GamepadService);

  private gamepadEnabled = signal(true);

  constructor() {
    effect(() => {
      if (this.gamepadEnabled()) {
        this.controllerApi.send_rc(
          this.gamepadService.mappedData().yaw,
          this.gamepadService.mappedData().pitch,
          this.gamepadService.mappedData().roll,
          this.gamepadService.mappedData().throttle
        );
      }
    })
  }
}
