import {Component, input} from '@angular/core';

@Component({
    selector: 'app-input',
    imports: [],
    templateUrl: './input.component.html',
    standalone: true,
    styleUrl: './input.component.css'
})
export class InputComponent {
    placeHolderText = input<string>();
    icon = input<string>();
}
