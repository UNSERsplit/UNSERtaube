import {Component, Input, signal} from '@angular/core';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-status',
    imports: [
        FormsModule
    ],
  templateUrl: './status.component.html',
  styleUrl: './status.component.css', standalone: true
})
export class StatusComponent {
    @Input() isConnected: boolean = false;
    @Input() fontsize: number = 32;
    @Input() margin: number = 10;
    @Input() padding: number = 12;
}
