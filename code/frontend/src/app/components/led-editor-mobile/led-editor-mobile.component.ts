import {Component, inject, Output, EventEmitter, OnInit} from '@angular/core';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { ControllerApiService } from '../../service/controller-api.service';
import { MatDialogRef } from '@angular/material/dialog';
import {ButtonComponent} from '../button/button.component';
import {ButtonVariants} from '../button/button.variants';

interface Led {
    ledstatus: number;
}

enum LedStatus {
    OFF    = 0,
    BLUE   = 1,
    PURPLE = 2,
    RED    = 3
}

@Component({
    selector: 'app-led-editor',
    standalone: true,
    imports: [
        CommonModule,
        MatDialogModule,
        MatIconModule,
        MatButtonModule,
        ButtonComponent,
    ],
    templateUrl: './led-editor-mobile.component.html',
    styleUrl:    './led-editor-mobile.component.css'
})
export class LedEditorMobileComponent implements OnInit {
    /** Schließt das Popup — Parent kann (closePopup) binden */
    @Output() closePopup = new EventEmitter<void>();

    protected  ButtonVariant2 = ButtonVariants.green;

    private controllerApi = inject(ControllerApiService);

    selectedColor = 0;
    colorCodes    = ['#21262d', '#0066FF', '#A040FF', '#fa3f3f'];
    leds: Led[][]  = [];

    constructor(private dialogRef: MatDialogRef<LedEditorMobileComponent>) {
        this.initGrid();
    }

    // ── Grid-Initialisierung ────────────────────────────────────────────

    private initGrid(): void {
        this.leds = Array.from({ length: 8 }, () =>
            Array.from({ length: 8 }, () => ({ ledstatus: LedStatus.OFF }))
        );
    }

    // ── LED-Aktionen ────────────────────────────────────────────────────

    setLedColor(row: number, col: number): void {
        this.leds[row][col].ledstatus = this.selectedColor;
        this.pushToApi();
    }

    getLedColor(status: number): string {
        return this.colorCodes[status];
    }

    clearLeds(): void {
        this.initGrid();
        this.pushToApi();
    }

    ngOnInit(): void {
        const MAPPING: {[index: string]: LedStatus} = {
            "0": 0,
            "b": 1,
            "p": 2,
            "r": 3
        }

        this.controllerApi.get_matrix().then((pattern: string) => {
            for (let i = 0; i < 8; i++) {
                for (let j = 0; j < 8; j++) {
                    this.leds[i][j] = { ledstatus: MAPPING[pattern[i * 8 + j]] };
                }
            }
        })
    }

    // ── API-Sync ─────────────────────────────────────────────────────────

    private pushToApi(): void {
        const MAPPING: Record<number, string> = { 0: '0', 1: 'b', 2: 'p', 3: 'r' };
        const data = this.leds.flat().map(v => MAPPING[v.ledstatus]).join('');
        this.controllerApi.matrix(data);
    }

    // ── Popup-Steuerung ──────────────────────────────────────────────────

    close(): void {
        this.dialogRef.close();  // ← so schließt sich ein MatDialog
    }

    blinkPolice() {
        this.controllerApi.flash(255,0,0,0,0,255, 1)
    }

}
