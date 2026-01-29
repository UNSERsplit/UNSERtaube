import { Component } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {FormsModule} from '@angular/forms';

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
    ipaddress = "";
    dronename = "";
    onButtonClick() {
        console.log(this.dronename);
        console.log(this.ipaddress);
    }
}
