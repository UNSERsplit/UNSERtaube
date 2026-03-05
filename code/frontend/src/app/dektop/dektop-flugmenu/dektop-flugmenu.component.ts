import { Component } from '@angular/core';
import {TitelComponent} from '../../components/titel/titel.component';
import {ConnectedDroneComponent} from '../../components/connected-drone/connected-drone.component';
import {StartCardComponent} from '../../components/start-drone/start-card.component';

@Component({
  selector: 'app-dektop-flugmenu',
    imports: [
        TitelComponent,
        ConnectedDroneComponent,
        StartCardComponent
    ],
  templateUrl: './dektop-flugmenu.component.html',
  styleUrl: './dektop-flugmenu.component.css'
})
export class DektopFlugmenuComponent {

}
