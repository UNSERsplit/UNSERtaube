import {Component, computed, effect, inject, input, model, signal} from '@angular/core';
import {ButtonComponent} from "../../components/button/button.component";
import {FormsModule} from "@angular/forms";
import {HomeButtonComponent} from "../../components/home-button/home-button.component";
import {KeyboardInputComponent} from "../../dektop/keyboard-input/keyboard-input.component";
import {LedControlButtonComponent} from "../../components/led-control-button/led-control-button.component";
import {RecordButtonComponent} from "../../components/record-button/record-button.component";
import {VideoApiService} from '../../service/video-api.service';
import {ControllerApiService} from '../../service/controller-api.service';
import {GamepadService} from '../../service/gamepad.service';
import {ButtonVariants} from '../../components/button/button.variants';
import {MobilePathMapComponent} from '../../components/mobile-path-map/mobile-path-map.component';
import { JoystickComponent, JoystickValue } from '../../components/joystick/joystick.component';
import {MobileHomeButtonComponent} from '../../components/mobile-home-button/mobile-home-button.component';
import {
    MobileLedControlButtonComponent
} from '../../components/mobile-led-control-button/mobile-led-control-button.component';
import {
    PersonDetectionButtonMobileComponent
} from '../../components/person-detection-button-mobile/person-detection-button-mobile.component';
import {RecordButtonMobileComponent} from '../../components/record-button-mobile/record-button-mobile.component';


export type Mode = "PATH" | "AUTONOMOUS" | "TOUCH"

const toString = {
    "PATH": "Flugpfad",
    "AUTONOMOUS": "Ringerkennung",
    "TOUCH" : "Touch"
}

@Component({
  selector: 'app-mobile-flug',
    imports: [
        //ButtonComponent,
        FormsModule,
        MobilePathMapComponent,
        JoystickComponent,
        MobileHomeButtonComponent,
        MobileLedControlButtonComponent,
        PersonDetectionButtonMobileComponent,
        RecordButtonMobileComponent
    ],
  templateUrl: './mobile-flug.component.html',
  styleUrl: './mobile-flug.component.css'
})
export class MobileFlugComponent {
    private videoApi = inject(VideoApiService);
    private controllerApi = inject(ControllerApiService);
    private gamepadService = inject(GamepadService);

    public currentmode = signal<Mode>("TOUCH")

    public mode = input<string | undefined>();

    private armed = signal(false);


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
    protected modeName = computed(() => toString[this.currentmode()])

    protected readonly ButtonVariant = ButtonVariants;
    buttonHeight: string = "3rem";
    buttonWidth: string = "5rem";

    protected temp = computed(() => (this.state().temph + this.state().templ) / 2);

    constructor() {
        effect(() => {
            if(this.currentmode() == "PATH" || this.currentmode() == "AUTONOMOUS") return

            if(this.gamepadService.gamepadConnected()) {
                this.currentmode.set("TOUCH")
            } else {
                this.currentmode.set("TOUCH")
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

          if(this.currentmode() == "AUTONOMOUS") {
            
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
        if(this.mode() == "ring") {
            this.currentmode.set("AUTONOMOUS");
        }else if(this.mode() == "replay") {
            this.currentmode.set("PATH");
        }
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

    // Aktuelle Sticks-Werte (1..100), falls du sie anzeigen / weiterreichen willst
    throttle = 1;
    yaw = 50;
    pitch = 50;
    roll = 50;

    /** Linker Stick: X = Yaw, Y = Throttle */
    onLeftStick(v: JoystickValue): void {
        this.yaw = v.x;
        this.throttle = v.y;
        this.sendRc();
    }

    /** Rechter Stick: X = Roll, Y = Pitch */
    onRightStick(v: JoystickValue): void {
        this.roll = v.x;
        this.pitch = v.y;
        this.sendRc();
    }

    private sendRc(): void {
        if(this.throttle == 0 && this.yaw == 0 && this.roll == 0 && this.pitch == 0) {
            this.armed.set(false);
        }
        if(!this.armed() && this.throttle < -50 && this.yaw > 50 && this.roll < -50 && this.pitch < -50) {
            this.armed.set(true);
            this.controllerApi.send_rc(0, 0, 0, 0)
            setTimeout(() => {
                this.takeoff()
            }, 500);
            
        }
        if(!this.armed()) {
            this.controllerApi.send_rc(this.yaw, this.pitch, this.roll, this.throttle)
        }
    }

}
