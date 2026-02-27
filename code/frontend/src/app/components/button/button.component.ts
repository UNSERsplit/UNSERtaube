import { Component, input, HostBinding } from '@angular/core';

export enum ButtonVariant {
    blue = 'blue',
    secondary = 'secondary',
    success = 'success',
    warning = 'warning',
    danger = 'danger'
}

@Component({
    selector: 'app-button',
    imports: [],
    templateUrl: './button.component.html',
    standalone: true,
    styleUrl: './button.component.css'
})
export class ButtonComponent {
    text = input<string>();
    variant = input<ButtonVariant>();
}
