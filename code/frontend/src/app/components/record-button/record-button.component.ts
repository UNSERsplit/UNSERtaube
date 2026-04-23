import { Component, inject, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ControllerApiService } from '../../service/controller-api.service';

@Component({
    selector: 'app-record-button',
    standalone: true,
    imports: [
        CommonModule, // Für [class.x], *ngIf etc.
        FormsModule   // Für [(ngModel)] im Eingabefeld
    ],
    templateUrl: './record-button.component.html',
    styleUrl: './record-button.component.css',
})
export class RecordButtonComponent implements OnDestroy {

    // ─── UI-Zustände ───────────────────────────────────────────────────────────

    isRecording = false;       // Läuft gerade eine Aufnahme?
    showStopPopup = false;     // Popup 1 sichtbar? (Aufnahme beenden)
    showSavePopup = false;     // Popup 2 sichtbar? (Speichern + Vorschau)
    statusLabel = 'Aufnahme starten'; // Text unter dem Button
    timerDisplay = '';         // Laufzeit MM:SS
    recordingName = '';        // Eingabe aus dem Namensfeld in Popup 2

    // ─── Private Felder ────────────────────────────────────────────────────────

    private seconds = 0;      // Vergangene Sekunden seit Aufnahmestart
    private interval: ReturnType<typeof setInterval> | null = null; // Timer-Referenz

    // ─── Template-Methoden ─────────────────────────────────────────────────────

    private controllerApi = inject(ControllerApiService);

    /** Aufnahme starten oder Popup 1 öffnen falls bereits aufgenommen wird */
    toggleRecording(): void {
        if (this.isRecording) {
            this.showStopPopup = true;
        } else {
            this.controllerApi.start_recording()
            this.startRecording();
        }
    }

    /** Popup 1 → "Abbrechen": Aufnahme verwerfen ohne zu speichern */
    async discardRecording(): Promise<void> {
        this.closePopups();
        this.isRecording = false;
        await this.controllerApi.stop_recording("")
        this.stopRecording('Aufnahme abgebrochen');
    }

    /** Popup 1 → "Speichern": Wechsel zu Popup 2, Eingabefeld zurücksetzen */
    openSavePopup(): void {
        this.showStopPopup = false;
        this.showSavePopup = true;
        this.recordingName = '';
    }

    /** Popup 2 → "Speichern": Aufnahme speichern und Status kurz anzeigen */
    async saveRecording(): Promise<void> {
        if (!this.recordingName.trim()) return; // Zusätzliche Absicherung zum disabled-Attribut
        this.closePopups();
        this.isRecording = false;
        const videoName = await this.controllerApi.stop_recording(this.recordingName.trim())
        window.open("/video/" + videoName, "_blank")
        this.stopRecording(`"${this.recordingName}" gespeichert`);
    }

    /** Alle Popups schließen (auch per Klick auf den Overlay-Hintergrund) */
    closePopups(): void {
        this.showStopPopup = false;
        this.showSavePopup = false;
    }

    // ─── Private Hilfsmethoden ─────────────────────────────────────────────────

    /** Aufnahme starten: Zustand setzen + Sekundentimer starten */
    private startRecording(): void {
        this.isRecording = true;
        this.statusLabel = 'Aufnahme läuft …';
        this.seconds = 0;
        this.timerDisplay = '00:00';

        this.interval = setInterval(() => {
            this.seconds++;
            const m = String(Math.floor(this.seconds / 60)).padStart(2, '0');
            const s = String(this.seconds % 60).padStart(2, '0');
            this.timerDisplay = `${m}:${s}`;
        }, 1000);
    }

    /** Aufnahme stoppen: Statusmeldung anzeigen, nach 2,5 s zurücksetzen */
    private stopRecording(message: string): void {
        this.statusLabel = message;
        this.clearTimer();
        setTimeout(() => {
            this.statusLabel = 'Aufnahme starten';
            this.timerDisplay = '';
        }, 2500);
    }

    /** Timer stoppen und Referenz leeren (verhindert Memory Leaks) */
    private clearTimer(): void {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    // ─── Lifecycle ─────────────────────────────────────────────────────────────

    /** Timer aufräumen wenn die Komponente zerstört wird */
    ngOnDestroy(): void {
        this.clearTimer();
    }
}
