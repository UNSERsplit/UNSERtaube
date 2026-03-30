import {Component, inject} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {buildApplication} from '@angular-devkit/build-angular';
import { VideoStreamComponent } from '../video-stream/video-stream.component';
import {PathmapComponent} from '../pathmap/pathmap.component';
import {ControllerApiService} from './controller-api.service';
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
  controllerApi = inject(ControllerApiService)
  loadTestData() {
    console.log("Sende Testdaten an Service...");

    const mockList: [number, number, number][] =
      [
        [50, 50, 0],
        [100, 150, 20],
        [200, 100, 50],
        [300, 200, 100]
      ]
    ;

    // Das Signal im Service aktualisieren
    this.controllerApi.pathmapsignal.set(mockList);
  }
}
