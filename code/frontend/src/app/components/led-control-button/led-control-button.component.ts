import { Component, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { LedEditorComponent } from '../led-editor/led-editor.component';

@Component({
    selector: 'app-led-control-button',
    templateUrl: './led-control-button.component.html',
    styleUrls: ['./led-control-button.component.css'],
    standalone: true
})
export class LedControlButtonComponent {
    private dialog = inject(MatDialog);

    openLedEditor(): void {
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
