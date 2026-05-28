import {Component, inject} from '@angular/core';
import {ControllerApiService} from '../../service/controller-api.service';

@Component({
  selector: 'app-person-detection-button-mobile',
  imports: [],
  templateUrl: './person-detection-button-mobile.component.html',
  styleUrl: './person-detection-button-mobile.component.css'
})
export class PersonDetectionButtonMobileComponent {
    enabled: boolean = false;
    private controllerApi = inject(ControllerApiService);

    protected toogle(){
        this.enabled = !this.enabled;
        if (this.enabled) {
            this.controllerApi.detect_people;
        }
    }

}
