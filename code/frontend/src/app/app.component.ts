import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {LoginPageComponent} from './login-page/login-page.component';


@Component({
    selector: 'app-root',
    imports: [RouterOutlet, FormsModule, LoginPageComponent],
    styleUrl: './app.component.css',
    templateUrl: './app.component.html',
    standalone: true
})
export class AppComponent {

}
