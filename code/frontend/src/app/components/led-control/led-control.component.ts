import {Component, Input} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import {MatDialog} from '@angular/material/dialog';
import {LedEditorComponent} from '../led-editor/led-editor.component';

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
    buttonWidth: string = '28rem';
    buttonHeight: string = '6rem';
    @Input() shadow: string = "0 0 4px rgba(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(2244, 3, 252, 0.8)";
    protected readonly CardVariants = CardVariants;

    constructor(public dialog: MatDialog) {}

    openPopup() {
        this.dialog.open(LedEditorComponent, {
            width: 'auto',
            height: 'auto',
            minHeight: 'auto',
            panelClass: ['scrollbar-dark', 'purpleShadow'],
            maxWidth: 'none',
            maxHeight: 'none',
        });
    }
}
