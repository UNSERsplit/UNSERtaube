import {Component, input, Input} from '@angular/core';
import {ButtonVariants} from '../button/button.variants';
import {CardVariants} from './card.variants';

@Component({
    selector: 'app-card',
    imports: [],
    templateUrl: './card.component.html',
    standalone: true,
    styleUrl: './card.component.css'
})
export class CardComponent {
    @Input() width: string = '60rem';
    @Input() height: string = '6rem';
    @Input() flexdirection: string = "column";
    @Input() shadow: string = "";
    variant = input<CardVariants>();
}
