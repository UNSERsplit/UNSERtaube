import { Component } from '@angular/core';
import {TitelComponent} from '../../components/titel/titel.component';
import {ConnectedDroneComponent} from '../../components/connected-drone/connected-drone.component';
import {StartCardComponent} from '../../components/start-drone/start-card.component';
import {FlypathComponent} from '../../components/flypath/flypath.component';
import {LedControlComponent} from '../../components/led-control/led-control.component';
import {PathlistComponent} from '../../components/pathlist/pathlist.component';

@Component({
  selector: 'app-dektop-flugmenu',
    imports: [
        TitelComponent,
        ConnectedDroneComponent,
        StartCardComponent,
        FlypathComponent,
        LedControlComponent,
        PathlistComponent
    ],
  templateUrl: './dektop-flugmenu.component.html',
  styleUrl: './dektop-flugmenu.component.css'
})
export class DektopFlugmenuComponent {


}
