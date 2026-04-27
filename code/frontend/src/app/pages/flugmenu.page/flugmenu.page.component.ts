import {Component, inject} from '@angular/core';
import {DeviceService} from '../../service/device.service';
import {DektopFlugmenuComponent} from '../../dektop/dektop-flugmenu/dektop-flugmenu.component'


@Component({
  selector: 'app-flugmenu.page',
  imports: [
      DektopFlugmenuComponent,
  ],
  templateUrl: './flugmenu.page.component.html',
  styleUrl: './flugmenu.page.component.css'
})
export class FlugmenuPageComponent {
    isMobile = inject(DeviceService).isMobile;
}
