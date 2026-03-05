import { Component, input, HostBinding } from '@angular/core';
import {ButtonVariants} from "./button.variants"

@Component({
    selector: 'app-button',
    imports: [],
    templateUrl: './button.component.html',
    standalone: true,
    styleUrl: './button.component.css'
})
export class ButtonComponent {
    text = input<string>();
    variant = input<ButtonVariants>();
}
