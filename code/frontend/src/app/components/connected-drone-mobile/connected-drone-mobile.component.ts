import {Component, computed, effect, inject, Input, WritableSignal} from '@angular/core';
import {ControllerApiService} from '../../service/controller-api.service';
import {DeviceService} from '../../service/device.service';
import {ButtonVariants} from '../button/button.variants';
import {ButtonComponent} from '../button/button.component';
import {CardComponent} from '../card/card.component';
import {StatusComponent} from '../status/status.component';
import {CardVariants} from '../card/card.variants';

@Component({
    selector: 'app-connected-drone-mobile',
    imports: [
        ButtonComponent,
        CardComponent,
        StatusComponent
    ],
    templateUrl: './connected-drone-mobile.component.html',
    standalone: true,
    styleUrl: './connected-drone-mobile.component.css'
})
export class ConnectedDroneMobileComponent {
    private controller = inject(ControllerApiService);

    drone = computed(() => this.controller.drone()!)

    isDroneConnected = computed(() => this.controller.status() == "drone_connected");
    isDisconnected = computed(() => this.controller.status() == "ws_connected");

    protected  ButtonVariant = ButtonVariants.red;
    buttonContent: string = "Trennen";
    buttonWidth: string = '15rem';
    buttonHeight: string = '3rem';

    @Input() setButtonWidth: string = '';
    @Input() setButtonheight: string='';
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
                this.controller.drone()!.getId
            )
        }
    }
    flexdirection: string = 'row';
    protected readonly CardVariants = CardVariants;
}
