import {Component, inject} from '@angular/core';
import {DeviceService} from '../../service/device.service';
import {LoginPageComponentx} from '../../dektop/desktop-login-page/login-page.component';
import {MobileLoginPageComponent} from '../../mobile/mobile-login-page/mobile-login-page.component';

@Component({
  selector: 'app-login.page',
    imports: [
        LoginPageComponentx,
        MobileLoginPageComponent,
    ],
  templateUrl: './login.page.component.html',
  styleUrl: './login.page.component.css'
})
export class LoginPageComponent {
    isMobile = inject(DeviceService).isMobile;
}
