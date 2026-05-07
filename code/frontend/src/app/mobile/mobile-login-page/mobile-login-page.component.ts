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

@Component({
    selector: 'app-mobile-login-page',
    imports: [
        StatusComponent,
        TitelComponent,
        CardComponent,
        InputHeaderComponent,
        ButtonComponent,
        DroneCarouselComponent
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
    buttonHeight: string = '1rem';

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
