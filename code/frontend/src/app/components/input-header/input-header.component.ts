import {Component, input, model} from '@angular/core';
import {InputComponent} from '../input/input.component';

@Component({
    selector: 'app-input-header',
    imports: [InputComponent],
    templateUrl: './input-header.component.html',
    standalone: true,
    styleUrl: './input-header.component.css'
})
export class InputHeaderComponent {
    headerText = input<string>();
    placeHolderText1 = input<string>();
    icon1 = input<string>();

    public value = model<string>("fd");
}
