import {Component, inject, WritableSignal} from '@angular/core';
import { RouterModule } from '@angular/router';
import {DeviceService} from '../../service/device.service';

@Component({
    selector: 'app-start-card',
    imports: [
        RouterModule
    ],
    templateUrl: './start-card.component.html',
    styleUrl: './start-card.component.css',

    standalone: true
})
export class StartCardComponent {
    isMobile: WritableSignal<boolean> = inject(DeviceService).isMobile;

    checkDeviceHeight() {
        if (this.isMobile()) {
            return '3rem';
        } else {
            return '6rem';
        }
    }

    checkDeviceWitdh() {
        if (this.isMobile()) {
            return '15rem';
        } else {
            return '60rem';
        }
    }
}
