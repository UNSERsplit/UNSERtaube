import {Component, computed, effect, inject, model, signal} from '@angular/core';
import {ButtonComponent} from '../../components/button/button.component';
import {InputComponent} from '../../components/input/input.component';
import {InputHeaderComponent} from '../../components/input-header/input-header.component';
import {TitelComponent} from '../../components/titel/titel.component';
import {DroneCarouselComponent} from '../../components/drone-carousel/drone-carousel.component';
import {StatusComponent} from '../../components/status/status.component';
import {ButtonVariants} from '../../components/button/button.variants';
import {CardComponent} from '../../components/card/card.component';
import {Router} from '@angular/router';
import { ControllerApiService } from '../../controller-api.service';

@Component({
    selector: 'app-desktop-login-page',
    templateUrl: './login-page.component.html',
    standalone: true,
    imports: [ButtonComponent, InputHeaderComponent, TitelComponent, DroneCarouselComponent, StatusComponent, StatusComponent, CardComponent],
    styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
    controllerApi = inject(ControllerApiService)

    protected name = signal<string>("");
    protected ip = signal<string>("");
    protected readonly ButtonVariant = ButtonVariants;
    private router = inject(Router);

    buttonWidth: string = '65rem';
    buttonHeight: string = '4rem';

    private async createAndConnect(name: string, ip: string) {
        //create
        await this.connect(name, ip)
    }

    private async connect(name: string, ip: string) {
        await this.controllerApi.connect(name, ip);
    }

    handleConnect() { //TODO validation
        this.createAndConnect(this.name(), this.ip())
    }
}
