import {Component, Input} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';

@Component({
  selector: 'app-led-control',
    imports: [
        CardComponent
    ],
  templateUrl: './led-control.component.html',
  styleUrl: './led-control.component.css'
})
export class LedControlComponent {
    flexdirection: string = 'column';
    @Input() shadow: string = "0 0 4px rgba(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(2244, 3, 252, 0.8)";
    protected readonly CardVariants = CardVariants;
}
