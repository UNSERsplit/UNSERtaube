import { Component, inject } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {FormsModule} from '@angular/forms';
import { ControllerApiService } from '../app/controller-api.service';

@Component({
  selector: 'login',
    imports: [
        RouterOutlet,
        FormsModule
    ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  public controllerApi = inject(ControllerApiService);

    ipaddress = "";
    dronename = "";
    onButtonClick() {
        console.log(this.dronename);
        console.log(this.ipaddress);

        this.controllerApi.connect(this.ipaddress)
    }

    land() {
      this.controllerApi.land()
    }

    takeoff() {
      this.controllerApi.takeoff()
    }
}
