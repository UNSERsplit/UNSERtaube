import {Component, inject} from '@angular/core';
import {MatDialog} from '@angular/material/dialog';
import {LedEditorMobileComponent} from '../led-editor-mobile/led-editor-mobile.component';

@Component({
  selector: 'app-mobile-led-control-button',
  imports: [],
  templateUrl: './mobile-led-control-button.component.html',
  styleUrl: './mobile-led-control-button.component.css'
})
export class MobileLedControlButtonComponent {
    private dialog = inject(MatDialog);

    openLedEditor(): void {
        this.dialog.open(LedEditorMobileComponent, {
            width: 'auto',
            height: 'auto',
            minHeight: 'auto',
            panelClass: ['scrollbar-dark', 'purpleShadow'],
            maxWidth: 'none',
            maxHeight: 'none',
        });
    }
}
