import {Component, inject} from '@angular/core';
import {DeviceService} from '../../service/device.service';
import {LoginPageComponentx} from '../../dektop/desktop-login-page/login-page.component';

@Component({
  selector: 'app-login.page',
    imports: [
        LoginPageComponentx,
    ],
  templateUrl: './login.page.component.html',
  styleUrl: './login.page.component.css'
})
export class LoginPageComponent {
    isMobile = inject(DeviceService).isMobile;
}
