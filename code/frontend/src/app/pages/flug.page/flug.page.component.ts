import {Component, inject} from '@angular/core';
import {DeviceService} from '../../service/device.service';
import {DesktopFlugComponent} from '../../dektop/desktop-flug/desktop-flug.component';
import {MobileFlugComponent} from '../../mobile/mobile-flug/mobile-flug.component';

@Component({
  selector: 'app-flug.page',
    imports: [
        DesktopFlugComponent,
        MobileFlugComponent
    ],
  templateUrl: './flug.page.component.html',
  styleUrl: './flug.page.component.css'
})
export class FlugPageComponent {
    isMobile = inject(DeviceService).isMobile;
}
