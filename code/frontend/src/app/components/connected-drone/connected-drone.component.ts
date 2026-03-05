import { Component } from '@angular/core';
import {StatusComponent} from '../status/status.component';
import {Drone} from '../../../objects/drone';
import {ButtonComponent, } from '../button/button.component';
import {ButtonVariants} from '../button/button.variants';

@Component({
  selector: 'app-connected-drone',
    imports: [
        StatusComponent,
        ButtonComponent,
    ],
  templateUrl: './connected-drone.component.html',
  styleUrl: './connected-drone.component.css',
    standalone:true
})
export class ConnectedDroneComponent {
    drone: Drone = new Drone("Herbert", "192.168.0.2");
    protected  ButtonVariant = ButtonVariants.red;
    isDroneConnected: boolean = true;
    buttonContent: string = "Verbindung trennen";
    handleConnect() {
        this.isDroneConnected = !this.isDroneConnected;
        if (this.isDroneConnected) {
            this.buttonContent = "Verbindung trennen";
            this.ButtonVariant = ButtonVariants.red;
        }else{
            this.buttonContent = "Verbinden";
            this.ButtonVariant = ButtonVariants.green;
        }
    }
}
