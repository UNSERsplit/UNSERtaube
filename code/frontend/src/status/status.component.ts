import { Component, computed, effect, inject, OnInit } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { ControllerApiService } from '../app/controller-api.service';
import { GamepadService } from '../app/gamepad.service';

@Component({
  selector: 'status',
  imports: [],
  templateUrl: './status.component.html',
  styleUrl: './status.component.css'
})
export class StatusComponent implements OnInit{
  private gamepadService = inject(GamepadService);

  public controllerApi = inject(ControllerApiService);
  public battery = computed(() => this.controllerApi.state().bat);
  public roll = computed(() => this.controllerApi.state().roll);
  public pitch = computed(() => this.controllerApi.state().pitch);
  public yaw = computed(() => this.controllerApi.state().yaw);
  
  public speed = computed(() => {
    return `x:${this.controllerApi.state().vgx} y:${this.controllerApi.state().vgy} z:${this.controllerApi.state().vgz}`
  })

  constructor() {
    effect(() => {
      this.controllerApi.send_rc(
        this.gamepadService.mappedData().yaw,
        this.gamepadService.mappedData().pitch,
        this.gamepadService.mappedData().roll,
        this.gamepadService.mappedData().throttle
      );
    })
  }

  ngOnInit(): void {
    this.gamepadService.currentMapping = {throttle_axis_id: 1, roll_axis_id: 2, pitch_axis_id: 4, yaw_axis_id: 0}

    setInterval(() => {
      this.gamepadService.tick()
    }, 10);
  }
}
