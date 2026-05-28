import { Component, computed, effect, HostListener, inject, model, OnDestroy, OnInit, signal } from '@angular/core';
import { VideoApiService } from '../../service/video-api.service';
import { ControllerApiService } from '../../service/controller-api.service';
import { KeyboardInputComponent } from '../keyboard-input/keyboard-input.component';
import { GamepadService } from '../../service/gamepad.service';
import { ControllerInputComponent } from '../controller-input/controller-input.component';
import {ButtonComponent} from '../../components/button/button.component';
import {ButtonVariants} from '../../components/button/button.variants';
import { FormsModule } from '@angular/forms';
import {RecordButtonComponent} from '../../components/record-button/record-button.component';
import {LedControlButtonComponent} from '../../components/led-control-button/led-control-button.component';
import {HomeButtonComponent} from '../../components/home-button/home-button.component';
import { PathMapComponent } from '../../components/path-map/path-map.component';
import {
    PersonDetectionButtonComponent
} from '../../components/person-detection-button/person-detection-button.component';

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
        HomeButtonComponent,
        PathMapComponent,
        PersonDetectionButtonComponent
    ],
  templateUrl: './desktop-flug.component.html',
  styleUrl: './desktop-flug.component.css'
})
export class DesktopFlugComponent implements OnInit, OnDestroy{
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
      const detections = this.state().detections;
      const element = document.querySelector("canvas#detection-overlay") as HTMLCanvasElement;
      const ctx = element.getContext("2d")!;

      ctx.clearRect(0,0,960,720);

      detections.forEach((v) => {
        if (v.type === "person") {
          const [x1,y1,x2,y2] = v.cords

          const color = "red"

          ctx.strokeStyle = color
          ctx.strokeRect(x1, y1, x2-x1, y2-y1);
          ctx.fillStyle = color
          
          const metrics = ctx.measureText(v.type)
          ctx.fillText(v.type, x1 + 2, y1 + metrics.fontBoundingBoxAscent)
        } else if (v.type === "ring") {
          const accuracy = v.accuracy;
          const center = v.center;
          const axis = v.axis;
          const tilt = v.tilt;

          let text = `${accuracy}/${parseInt((axis[0] / axis[1]) * 1000 + "")}`

          ctx.fillStyle = "lime"
          
          ctx.beginPath();
          ctx.arc(center[0], center[1], 5, 0, 2 * Math.PI);
          ctx.fill();

          const metrics = ctx.measureText(text)
          ctx.fillText(text, center[0] + 2, center[1] + metrics.fontBoundingBoxAscent)

          if(this.mode() == "AUTONOMOUS") {
            
          }
        }
      })
    })


    /*effect(() => {
      this.controllerApi.send_debug_finetune({
        show_processed_output: this.showProcessed(),
        hue_lower: this.hue_lower(),
        hue_upper: this.hue_upper(),
        saturation_lower: this.saturation_lower(),
        saturation_upper: this.saturation_upper(),
        value_lower: this.value_lower(),
        value_upper: this.value_upper()
      })
    })*/

    // @ts-ignore
    window.showDebugHud = this.showDebugHud;
  }

  ngOnInit(): void {
    this.videoApi.initVideo("video")
    document.body.requestFullscreen({navigationUI: "hide"})
  }

  ngOnDestroy(): void {
    this.videoApi.removeVideo()
    if(document.fullscreenElement) {
      document.exitFullscreen()
    }
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
}

