import {Component, Input} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';

@Component({
  selector: 'app-flypath',
    imports: [
        CardComponent
    ],
  templateUrl: './flypath.component.html',
  styleUrl: './flypath.component.css'
})
export class FlypathComponent {
    flexdirection: string = 'column';
    buttonWidth: string = '28rem';
    buttonHeight: string = '6rem';
    @Input() shadow: string = "0 0 4px rgb(244, 168, 3, 0.8),\n" +
        "        0 0 4px rgb(244, 168, 3, 0.8),\n" +
        "        0 0 4px rgb(244, 168, 3, 0.8)";
    protected readonly CardVariants = CardVariants;
}
