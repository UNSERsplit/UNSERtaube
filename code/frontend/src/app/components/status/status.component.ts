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
}
