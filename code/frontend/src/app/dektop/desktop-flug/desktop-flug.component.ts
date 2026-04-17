import { Component, computed, effect, HostListener, inject, OnInit, signal } from '@angular/core';
import { VideoApiService } from '../../video-api.service';
import { ControllerApiService } from '../../controller-api.service';
import { KeyboardInputComponent } from '../keyboard-input/keyboard-input.component';
import { GamepadService } from '../../gamepad.service';
import { ControllerInputComponent } from '../controller-input/controller-input.component';

export type Mode = "CONTROLLER" | "KEYBOARD" | "PATH" | "AUTONOMOUS"

const toString = {
  "CONTROLLER":"Controller",
  "KEYBOARD": "Keyboard",
  "PATH": "Flugpfad",
  "AUTONOMOUS": "Ringerkennung"
}

@Component({
  selector: 'app-desktop-flug',
  imports: [
    KeyboardInputComponent,
    ControllerInputComponent
  ],
  templateUrl: './desktop-flug.component.html',
  styleUrl: './desktop-flug.component.css'
})
export class DesktopFlugComponent implements OnInit{
  private videoApi = inject(VideoApiService);
  private controllerApi = inject(ControllerApiService);
  private gamepadService = inject(GamepadService);

  public mode = signal<Mode>("KEYBOARD")

  protected state = this.controllerApi.state.asReadonly()
  protected speedInDMS = computed(() => Math.sqrt(Math.pow(this.state().vgx, 2) + Math.pow(this.state().vgy, 2) + Math.pow(this.state().vgz, 2)))
  protected speed = computed(() => this.speedInDMS() / 2778)

  protected drone = computed(() => this.controllerApi.drone()!)
  protected modeName = computed(() => toString[this.mode()])
  protected temp = computed(() => (this.state().temph + this.state().templ) / 2);

  constructor() {
    effect(() => {
      if(this.mode() == "PATH" || this.mode() == "AUTONOMOUS") return

      if(this.gamepadService.gamepadConnected()) {
        this.mode.set("CONTROLLER")
      } else {
        this.mode.set("KEYBOARD")
      }
    })
  }

  ngOnInit(): void {
    this.videoApi.initVideo("video")
  }

  takeoff() {
    this.controllerApi.takeoff()
  }

  land() {
    this.controllerApi.land()
  }

  record() {
    this.controllerApi.start_recording()
  }

  async stop() {
    const name = await this.controllerApi.stop_recording()
    alert(name)
  }
}

