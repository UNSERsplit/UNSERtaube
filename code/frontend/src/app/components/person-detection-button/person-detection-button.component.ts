import {Component, inject} from '@angular/core';
import {ControllerApiService} from '../../service/controller-api.service';

@Component({
  selector: 'app-person-detection-button',
  imports: [],
  templateUrl: './person-detection-button.component.html',
  styleUrl: './person-detection-button.component.css'
})
export class PersonDetectionButtonComponent {
    enabled: boolean = false;
    private controllerApi = inject(ControllerApiService);

    protected toogle(){
        this.enabled = !this.enabled;
        if (this.enabled) {
            this.controllerApi.detect_people;
        }
    }
}
