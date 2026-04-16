import {Component, inject} from '@angular/core';
import {ButtonComponent} from '../../components/button/button.component';
import {InputComponent} from '../../components/input/input.component';
import {InputHeaderComponent} from '../../components/input-header/input-header.component';
import {TitelComponent} from '../../components/titel/titel.component';
import {DroneCarouselComponent} from '../../components/drone-carousel/drone-carousel.component';
import {StatusComponent} from '../../components/status/status.component';
import {ButtonVariants} from '../../components/button/button.variants';
import {CardComponent} from '../../components/card/card.component';
import {Router} from '@angular/router';

@Component({
    selector: 'app-desktop-login-page',
    templateUrl: './login-page.component.html',
    standalone: true,
    imports: [ButtonComponent, InputHeaderComponent, TitelComponent, DroneCarouselComponent, StatusComponent, StatusComponent, CardComponent],
    styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
    protected readonly ButtonVariant = ButtonVariants;
    isDroneConnected: boolean = false;
    buttonWidth: string = '65rem';
    buttonHeight: string = '4rem';

    private router = inject(Router);
    handleConnect() {
        this.isDroneConnected = !this.isDroneConnected;
        this.router.navigate(['/home']);

    }
}
