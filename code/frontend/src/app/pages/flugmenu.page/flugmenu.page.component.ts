import {Component, inject} from '@angular/core';
import {DeviceService} from '../../service/device.service';
import {DektopFlugmenuComponent} from '../../dektop/dektop-flugmenu/dektop-flugmenu.component'
import {MobileLoginPageComponent} from '../../mobile/mobile-login-page/mobile-login-page.component';
import {MobileFlugmenuComponent} from '../../mobile/mobile-flugmenu/mobile-flugmenu.component';


@Component({
    selector: 'app-flugmenu.page',
    imports: [
        DektopFlugmenuComponent,
        MobileFlugmenuComponent,
    ],
    templateUrl: './flugmenu.page.component.html',
    standalone: true,
    styleUrl: './flugmenu.page.component.css'
})
export class FlugmenuPageComponent {
    isMobile = inject(DeviceService).isMobile;
}
