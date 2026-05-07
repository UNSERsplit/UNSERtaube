import { Component, inject, Output, EventEmitter } from '@angular/core';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { ControllerApiService } from '../../service/controller-api.service';
import { MatDialogRef } from '@angular/material/dialog';

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
    ],
    templateUrl: './led-editor-mobile.component.html',
    styleUrl:    './led-editor-mobile.component.css'
})
export class LedEditorMobileComponent {
    /** Schließt das Popup — Parent kann (closePopup) binden */
    @Output() closePopup = new EventEmitter<void>();

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

    // ── API-Sync ─────────────────────────────────────────────────────────

    private pushToApi(): void {
        const MAPPING: Record<number, string> = { 0: '0', 1: 'b', 2: 'p', 3: 'r' };
        const data = this.leds.flat().map(v => MAPPING[v.ledstatus]).join('');
        this.controllerApi.matrix('set_matrix', data);
    }

    // ── Popup-Steuerung ──────────────────────────────────────────────────



    close(): void {
        this.dialogRef.close();  // ← so schließt sich ein MatDialog
    }

}
