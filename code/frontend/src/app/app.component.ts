import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {LoginPageComponent} from './dektop/desktop-login-page/login-page.component';
import {DektopFlugmenuComponent} from './dektop/dektop-flugmenu/dektop-flugmenu.component';


@Component({
    selector: 'app-root',
    imports: [RouterOutlet, FormsModule, LoginPageComponent, DektopFlugmenuComponent],
    styleUrl: './app.component.css',
    templateUrl: './app.component.html',
    standalone: true
})
export class AppComponent {

}
