import { Component, computed, effect, inject } from '@angular/core';
import {StatusComponent} from '../status/status.component';
import {Drone} from '../../../objects/drone';
import {ButtonComponent, } from '../button/button.component';
import {ButtonVariants} from '../button/button.variants';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import { ControllerApiService } from '../../controller-api.service';

@Component({
  selector: 'app-connected-drone',
    imports: [
        StatusComponent,
        ButtonComponent,
        CardComponent,
    ],
  templateUrl: './connected-drone.component.html',
  styleUrl: './connected-drone.component.css',
    standalone:true
})
export class ConnectedDroneComponent {
    private controller = inject(ControllerApiService);

    drone = computed(() => this.controller.drone()!)

    isDroneConnected = computed(() => this.controller.status() == "drone_connected");
    isDisconnected = computed(() => this.controller.status() == "ws_connected");

    protected  ButtonVariant = ButtonVariants.red;
    buttonContent: string = "Trennen";

    constructor() {
        effect(() => {
            if (this.isDroneConnected()) {
                this.buttonContent = "Trennen";
                this.ButtonVariant = ButtonVariants.red;
            } else if(this.isDisconnected()) {
                this.buttonContent = "Verbinden";
                this.ButtonVariant = ButtonVariants.green;
            }
        })
    }

    handleConnect() {
        if (this.isDroneConnected()) {
            this.controller.disconnect()
        } else if(this.isDisconnected()) {
            this.controller.connect(
                this.controller.drone()!.getName,
                this.controller.drone()!.getIp
            )
        }
    }
    flexdirection: string = 'row';
    protected readonly CardVariants = CardVariants;
}
