import { Component, computed, inject } from '@angular/core';
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
  public battery = computed(() => this.controllerApi.state().bat);
  public roll = computed(() => this.controllerApi.state().roll);
  public pitch = computed(() => this.controllerApi.state().pitch);
  public yaw = computed(() => this.controllerApi.state().yaw);
  
}
