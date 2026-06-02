import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    EventEmitter,
    Input,
    OnInit,
    Output,
    ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';

export interface JoystickValue {
    /** 1 (links) … 50 (mitte) … 100 (rechts) */
    x: number;
    /** 1 (unten) … 50 (mitte) … 100 (oben) */
    y: number;
}

@Component({
    selector: 'app-joystick',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './joystick.component.html',
    styleUrls: ['./joystick.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JoystickComponent implements OnInit {
    @Input() label = '';
    @Input() xLabel = 'X';
    @Input() yLabel = 'Y';

    /** Größe der Joystick-Basis in Pixeln */
    @Input() size = 200;

    /** X-Achse federt beim Loslassen zurück zur Mitte */
    @Input() springBackX = true;
    /** Y-Achse federt beim Loslassen zurück (z. B. für Throttle aus = false) */
    @Input() springBackY = true;

    /** Startposition X (-1 … 1), 0 = Mitte */
    @Input() initialX = 0;
    /** Startposition Y (-1 … 1), -1 = oben, 1 = unten */
    @Input() initialY = 0;

    @Output() valueChange = new EventEmitter<JoystickValue>();

    @ViewChild('base', { static: true }) baseRef!: ElementRef<HTMLDivElement>;

    // Normalisierte Position (-1 … 1)
    private normX = 0;
    private normY = 0;

    // Pixel-Offset für den Stick
    stickX = 0;
    stickY = 0;

    isActive = false;
    private pointerId: number | null = null;

    ngOnInit(): void {
        this.normX = this.clamp(this.initialX, -1, 1);
        this.normY = this.clamp(this.initialY, -1, 1);
        this.updateStickVisual();
        // initialen Wert direkt rausgeben
        queueMicrotask(() => this.emit());
    }

    get xValue(): number {
        // -1..1  ->  1..100
        return Math.round(this.normX * 100)
        //return Math.round(((this.normX + 1) / 2) * 99 + 1);
    }

    get yValue(): number {
        // Y wird invertiert: oben = hoher Wert
        return Math.round(this.normY * -100)
        //return Math.round(((-this.normY + 1) / 2) * 99 + 1);
    }

    get currentValue(): JoystickValue {
        return { x: this.xValue, y: this.yValue };
    }

    onPointerDown(event: PointerEvent): void {
        event.preventDefault();
        this.isActive = true;
        this.pointerId = event.pointerId;
        (event.target as HTMLElement).setPointerCapture(event.pointerId);
        this.updatePosition(event);
    }

    onPointerMove(event: PointerEvent): void {
        if (!this.isActive || event.pointerId !== this.pointerId) return;
        event.preventDefault();
        this.updatePosition(event);
    }

    onPointerUp(event: PointerEvent): void {
        if (event.pointerId !== this.pointerId) return;
        this.isActive = false;
        this.pointerId = null;

        if (this.springBackX) this.normX = this.initialX;
        if (this.springBackY) this.normY = this.initialY;

        this.updateStickVisual();
        this.emit();
    }

    private updatePosition(event: PointerEvent): void {
        const rect = this.baseRef.nativeElement.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = event.clientX - cx;
        const dy = event.clientY - cy;
        const radius = rect.width / 2;

        let nx = dx / radius;
        let ny = dy / radius;

        // Auf Kreis begrenzen
        const dist = Math.sqrt(nx * nx + ny * ny);
        if (dist > 1) {
            nx /= dist;
            ny /= dist;
        }

        this.normX = nx;
        this.normY = ny;
        this.updateStickVisual();
        this.emit();
    }

    private updateStickVisual(): void {
        const radius = this.size / 2;
        this.stickX = this.normX * radius;
        this.stickY = this.normY * radius;
    }

    private emit(): void {
        this.valueChange.emit(this.currentValue);
    }

    private clamp(v: number, min: number, max: number): number {
        return Math.max(min, Math.min(max, v));
    }
}
