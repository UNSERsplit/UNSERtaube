import {Component, computed, inject, Input, signal} from '@angular/core';
import {FormsModule} from '@angular/forms';
import { ControllerApiService } from '../../service/controller-api.service';

const LOOKUP = {
  "offline": "No Internet",
  "ws_connected": "Not Connected",
  "drone_connected": "Connected",
  "error": "Websocket Error",
  "connecting": "Connecting"
}

@Component({
  selector: 'app-status',
    imports: [
        FormsModule
    ],
  templateUrl: './status.component.html',
  styleUrl: './status.component.css', standalone: true
})
export class StatusComponent {
  controllerApi = inject(ControllerApiService)

  protected text = computed(() => LOOKUP[this.controllerApi.status()])


  @Input() fontsize: number = 32;
  @Input() margin: number = 10;
  @Input() padding: number = 12;
}
