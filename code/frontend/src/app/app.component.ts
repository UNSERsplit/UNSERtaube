import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {buildApplication} from '@angular-devkit/build-angular';
import {StatusComponent} from '../status/status.component';
import {LoginComponent} from '../login/login.component';


@Component({
    selector: 'app-root',
    imports: [RouterOutlet, FormsModule, StatusComponent, LoginComponent],
    styleUrl: './app.component.css',
    templateUrl: './app.component.html',
})
export class AppComponent {

}
