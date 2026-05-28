import {Component, computed, effect, inject, model, signal} from '@angular/core';
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
        ButtonComponent,
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

    public mode = signal<Mode>("TOUCH")

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
                this.mode.set("TOUCH")
            } else {
                this.mode.set("TOUCH")
            }
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
        // Hier z. B. an deinen Drone-Service übergeben:
        // this.drone().sendRc(this.roll, this.pitch, this.throttle, this.yaw);
        // Werte sind 1..100, mappe sie ggf. auf -100..100 falls dein Backend das erwartet:
        // const map = (v: number) => Math.round(((v - 1) / 99) * 200 - 100);
    }

}
