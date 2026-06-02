import {Component, inject, Input, WritableSignal} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import {DeviceService} from '../../service/device.service';
import { RouterLink } from "@angular/router";

@Component({
    selector: 'app-flypath',
    imports: [
    CardComponent,
    RouterLink
],
    templateUrl: './flypath.component.html',
    standalone: true,
    styleUrl: './flypath.component.css'
})
export class FlypathComponent {
    flexdirection: string = 'column';
    buttonWidth: string = '28rem';
    buttonHeight: string = '6rem';
    @Input() zweiterText:string="";

    isMobile: WritableSignal<boolean> = inject(DeviceService).isMobile;

    checkDeviceHeight() {
        if (this.isMobile()) {
            this.zweiterText = "";
            return '3rem';
        } else {
            this.zweiterText = "Ringe erkennen";
            return '6rem';
        }
    }

    checkDeviceWitdh() {
        if (this.isMobile()) {
            return '15rem';
        } else {
            return '28rem';
        }
    }

    @Input() shadow: string = "0 0 4px rgb(244, 168, 3, 0.8),\n" +
        "        0 0 4px rgb(244, 168, 3, 0.8),\n" +
        "        0 0 4px rgb(244, 168, 3, 0.8)";
    protected readonly CardVariants = CardVariants;
}
