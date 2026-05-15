import {Component, effect, inject} from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {buildApplication} from '@angular-devkit/build-angular';
import {ControllerApiService} from './service/controller-api.service';
import {LoginPageComponentx} from './dektop/desktop-login-page/login-page.component';
import {DektopFlugmenuComponent} from './dektop/dektop-flugmenu/dektop-flugmenu.component';
import { patch } from './service/ws_service.patch';


@Component({
    selector: 'app-root',
    imports: [RouterOutlet, FormsModule],
    styleUrl: './app.component.css',
    templateUrl: './app.component.html',
    standalone: true
})
export class AppComponent {
  controllerApi = inject(ControllerApiService)
  private router = inject(Router);

  constructor() {
    if(window.location.port == "4200") {
      patch(this.controllerApi);
    }
    effect(() => {
      const status = this.controllerApi.status()
      if(status == "ws_connected") {
        this.router.navigate(["/login-page"])
      } else if(status == "drone_connected") {
        this.router.navigate(["/home"])
      }
    })
  }
}
