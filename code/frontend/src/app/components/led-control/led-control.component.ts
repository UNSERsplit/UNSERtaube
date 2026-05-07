import {Component, inject, input, Input, WritableSignal} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import {MatDialog} from '@angular/material/dialog';
import {LedEditorComponent} from '../led-editor/led-editor.component';
import {DeviceService} from '../../service/device.service';

@Component({
    selector: 'app-led-control',
    imports: [
        CardComponent
    ],
    templateUrl: './led-control.component.html',
    standalone: true,
    styleUrl: './led-control.component.css'
})
export class LedControlComponent {
    flexdirection: string = 'column';
    buttonWidth: string = '28rem';
    buttonHeight: string = '6rem';

    isMobile: WritableSignal<boolean> = inject(DeviceService).isMobile;
    @Input() zweiterText: string="";

    checkDeviceHeight() {
        if (this.isMobile()) {
            this.zweiterText="";
            return '3rem';
        } else {
            this.zweiterText="Choose Mode";
            return '6rem';
        }
    }

    checkDeviceWitdh() {
        if (this.isMobile()) {
            return '15rem';
        } else {
            return '28rem';
        }
    }

    @Input() shadow: string = "0 0 4px rgba(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(244, 3, 252, 0.8),\n" +
        "        0 0 4px rgb(2244, 3, 252, 0.8)";
    protected readonly CardVariants = CardVariants;

    constructor(public dialog: MatDialog) {}

    openPopup() {
        if (this.isMobile()) {

        }
        else {
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
}
