import { Component, inject } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { ControllerApiService } from '../app/controller-api.service';

@Component({
  selector: 'status',
  imports: [],
  templateUrl: './status.component.html',
  styleUrl: './status.component.css'
})
export class StatusComponent {
  public controllerApi = inject(ControllerApiService);

  
}
