import {Component, Input} from '@angular/core';
import {
    MatDialogModule,
} from '@angular/material/dialog';
import {CommonModule} from '@angular/common';
import {MatSliderModule} from '@angular/material/slider';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button';
import {FormsModule} from '@angular/forms';
import { CardVariants } from '../card/card.variants';
import {CardComponent} from '../card/card.component';
import {ButtonComponent} from '../button/button.component';
import {ButtonVariants} from '../button/button.variants';

interface Led{
    ledstatus: number;
}

enum LedStatus {
    OFF = 0,
    BLUE = 1,
    PURPLE = 2,
    RED = 3
}

@Component({
    selector: 'app-led-editor',
    imports: [
        CommonModule,
        MatDialogModule,
        MatSliderModule,
        MatIconModule,
        MatButtonModule,
        FormsModule,
        CardComponent,
        ButtonComponent
    ],
    templateUrl: './led-editor.component.html',
    standalone: true,
    styleUrl: './led-editor.component.css'
})

export class LedEditorComponent {
    readonly CardVariants = CardVariants;
    flexdirection: string = 'row';
    selectedColor: number = 0;
    buttonWidth1: string = 'auto';
    buttonHeight1: string = 'auto';
    buttonWidth2: string = 'auto';
    buttonHeight2: string = 'auto';
    buttonWidth3: string = '20rem';
    buttonHeight3: string = '30rem';


    leds: Led[][] = []// Das Haupt-Array
    colorCodes = ['#21262d', '#0066FF', '#A040FF', '#fa3f3f'];

    buttonText: string = "Clear";
    protected  ButtonVariant = ButtonVariants.blue;

    constructor() {
        for (let i = 0; i < 8; i++) {
            this.leds[i] = [];
            for (let j = 0; j < 8; j++) {
                this.leds[i][j] = { ledstatus: LedStatus.OFF };
            }
        }
    }

    // Setzt die LED auf die aktuell gewählte Farbe aus der Sidebar
    setLedColor(rowIndex: number, colIndex: number) {
        this.leds[rowIndex][colIndex].ledstatus = this.selectedColor;
    }

    // Hilfsfunktion für das Template, um den Hex-Code zu bekommen
    getLedColor(status: number): string {
        return this.colorCodes[status];
    }

    clearLeds(){
        for (let i = 0; i < 8; i++) {
            this.leds[i] = [];
            for (let j = 0; j < 8; j++) {
                this.leds[i][j] = { ledstatus: LedStatus.OFF };
            }
        }
    }
}
