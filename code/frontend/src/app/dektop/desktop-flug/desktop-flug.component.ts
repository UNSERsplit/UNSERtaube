import { Component, computed, effect, HostListener, inject, model, OnInit, signal } from '@angular/core';
import { VideoApiService } from '../../video-api.service';
import { ControllerApiService } from '../../controller-api.service';
import { KeyboardInputComponent } from '../keyboard-input/keyboard-input.component';
import { GamepadService } from '../../gamepad.service';
import { ControllerInputComponent } from '../controller-input/controller-input.component';
import {ButtonComponent} from '../../components/button/button.component';
import {ButtonVariants} from '../../components/button/button.variants';
import { FormsModule } from '@angular/forms';
import {RecordButtonComponent} from '../../components/record-button/record-button.component';
import {LedControlButtonComponent} from '../../components/led-control-button/led-control-button.component';
import {HomeButtonComponent} from '../../components/home-button/home-button.component';

export type Mode = "CONTROLLER" | "KEYBOARD" | "PATH" | "AUTONOMOUS"

const toString = {
  "CONTROLLER":"Controller",
  "KEYBOARD": "Keyboard",
  "PATH": "Flugpfad",
  "AUTONOMOUS": "Ringerkennung"
}

// @ts-ignore
@Component({
  selector: 'app-desktop-flug',
    imports: [
        KeyboardInputComponent,
        ControllerInputComponent,
        ButtonComponent,
        FormsModule,
        RecordButtonComponent,
        LedControlButtonComponent,
        HomeButtonComponent
    ],
  templateUrl: './desktop-flug.component.html',
  styleUrl: './desktop-flug.component.css'
})
export class DesktopFlugComponent implements OnInit{
  private videoApi = inject(VideoApiService);
  private controllerApi = inject(ControllerApiService);
  private gamepadService = inject(GamepadService);

  public mode = signal<Mode>("KEYBOARD")

  protected showProcessed = model(false);
  protected hue_lower = model(5)
  protected hue_upper = model(170)
  protected saturation_lower = model(85)
  protected saturation_upper = model(255)
  protected value_lower = model(70)
  protected value_upper = model(255)

  protected showDebugHud = signal(false);

  protected state = this.controllerApi.state.asReadonly()

  protected speedInDMS = computed<{"x":number, "y":number, "z":number}>(() => {
    return {
      "x": this.state().vgx,
      "y": this.state().vgy,
      "z": this.state().vgz,
    }
  })
  protected speed = computed(() => Math.sqrt(Math.pow(this.speedInDMS().z, 2) + Math.pow(this.speedInDMS().y, 2) + Math.pow(this.speedInDMS().z, 2)))

  protected drone = computed(() => this.controllerApi.drone()!)
  protected modeName = computed(() => toString[this.mode()])

  protected readonly ButtonVariant = ButtonVariants;
  buttonHeight: string = "3rem";
  buttonWidth: string = "5rem";

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


    effect(() => {
      this.controllerApi.send_debug_finetune({
        show_processed_output: this.showProcessed(),
        hue_lower: this.hue_lower(),
        hue_upper: this.hue_upper(),
        saturation_lower: this.saturation_lower(),
        saturation_upper: this.saturation_upper(),
        value_lower: this.value_lower(),
        value_upper: this.value_upper()
      })
    })

    // @ts-ignore
    window.showDebugHud = this.showDebugHud;
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

  emergency(){
    this.controllerApi.emergency()
  }

  record() {
    this.controllerApi.start_recording()
  }

  async stop() {
    const name = await this.controllerApi.stop_recording("")
    window.open("/video/" + name, "_blank")
    alert(name)
  }
}

