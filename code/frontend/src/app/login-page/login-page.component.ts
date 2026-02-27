import { Component } from '@angular/core';
import {ButtonComponent, ButtonVariant} from '../components/button/button.component';
import {InputComponent} from '../components/input/input.component';
import {InputHeaderComponent} from '../components/input-header/input-header.component';
import {TitelComponent} from '../components/titel/titel.component';
import {DroneCarouselComponent} from '../components/drone-carousel/drone-carousel.component';
import {StatusComponent} from '../components/status/status.component';

@Component({
    selector: 'app-login-page',
    templateUrl: './login-page.component.html',
    standalone: true,
    imports: [ButtonComponent, InputComponent, InputHeaderComponent, TitelComponent, DroneCarouselComponent, StatusComponent, StatusComponent],
    styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
    protected readonly ButtonVariant = ButtonVariant;
    isDroneConnected: boolean = false;
    handleConnect() {
        this.isDroneConnected = !this.isDroneConnected; // Toggle oder Logik hier
    }
}
