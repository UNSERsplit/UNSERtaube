import {Component, input, Input} from '@angular/core';
import {ButtonVariants} from '../button/button.variants';
import {CardVariants} from './card.variants';

@Component({
  selector: 'app-card',
  imports: [],
  templateUrl: './card.component.html',
  styleUrl: './card.component.css'
})
export class CardComponent {
    @Input() width: number = 60;
    @Input() flexdirection: string = "column";
    @Input() shadow: string = "";
    variant = input<CardVariants>();
}
