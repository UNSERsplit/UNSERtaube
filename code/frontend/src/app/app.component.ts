import {Component, inject} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {buildApplication} from '@angular-devkit/build-angular';
import {StatusComponent} from '../status/status.component';
import {LoginComponent} from '../login/login.component';
import { VideoStreamComponent } from '../video-stream/video-stream.component';
import {PathmapComponent} from '../pathmap/pathmap.component';
import {ControllerApiService} from './controller-api.service';


@Component({
    selector: 'app-root',
  imports: [RouterOutlet, FormsModule, StatusComponent, LoginComponent, VideoStreamComponent, PathmapComponent],
    styleUrl: './app.component.css',
    templateUrl: './app.component.html',
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
