import {Component, input, model} from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-input',
    imports: [FormsModule],
    templateUrl: './input.component.html',
    standalone: true,
    styleUrl: './input.component.css'
})
export class InputComponent {
    placeHolderText = input<string>();
    icon = input<string>();
    public value = model<string>("");
}
