import { Component, computed, effect, inject, model, signal, HostListener, OnInit } from '@angular/core';
import { ButtonComponent } from '../../components/button/button.component';
import { InputComponent } from '../../components/input/input.component';
import { InputHeaderComponent } from '../../components/input-header/input-header.component';
import { TitelComponent } from '../../components/titel/titel.component';
import { DroneCarouselComponent } from '../../components/drone-carousel/drone-carousel.component';
import { StatusComponent } from '../../components/status/status.component';
import { ButtonVariants } from '../../components/button/button.variants';
import { CardComponent } from '../../components/card/card.component';
import { Router } from '@angular/router';
import { ControllerApiService } from '../../service/controller-api.service';
import {DroneCarouselMobileComponent} from '../../components/drone-carousel-mobile/drone-carousel-mobile.component';

@Component({
    selector: 'app-mobile-login-page',
    imports: [
        StatusComponent,
        TitelComponent,
        CardComponent,
        InputHeaderComponent,
        ButtonComponent,
        DroneCarouselMobileComponent
    ],
    templateUrl: './mobile-login-page.component.html',
    standalone: true,
    styleUrl: './mobile-login-page.component.css'
})
export class MobileLoginPageComponent {
    controllerApi = inject(ControllerApiService)

    protected name = signal<string>("");
    protected ip = signal<string>("");
    protected readonly ButtonVariant = ButtonVariants;

    buttonWidth: string = '100%';
    buttonHeight: string = '0.8rem';


    handleConnect() { //TODO validation
        this.controllerApi.createAndConnect(this.name(), this.ip());
    }
}
