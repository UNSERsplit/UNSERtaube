import {Component, Input} from '@angular/core';

@Component({
    selector: 'app-titel',
    imports: [],
    templateUrl: './titel.component.html',
    standalone: true,
    styleUrl: './titel.component.css'
})
export class TitelComponent {
    @Input() fontsize: number = 92;
    @Input() margin: number = 50;
}
