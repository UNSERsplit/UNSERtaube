import { Component, computed, effect, ElementRef, inject, ViewChild } from '@angular/core';
import { ControllerApiService } from '../app/service/controller-api.service';

@Component({
  selector: 'app-pathmap',
  standalone: true,
  templateUrl: './pathmap.component.html',
  styleUrl: './pathmap.component.css',
})

export class PathmapComponent {
  private controllerApi = inject(ControllerApiService);

  @ViewChild('canvasHtmlRef') canvasRef!: ElementRef<HTMLCanvasElement>;

  positions = computed(() => this.controllerApi.pathmapsignal() as [number,number,number][]);
  data : [number, number, number][] = [];

  constructor() {
    effect(() => {
      const currentPositions = this.positions();

      if (this.canvasRef != null && this.canvasRef.nativeElement != null) {
        this.drawPath(currentPositions);
      }
    });
  }

  private drawPath(points: [number,number,number][]) {
    const canvas = this.canvasRef.nativeElement;
    const canvasContext = canvas.getContext('2d');

    if (canvasContext === null) {
      return;
    }

    canvasContext.clearRect(0, 0, canvas.width, canvas.height);

    const padding = 50;
    const xValues = points.map(p => p[0]);
    const yValues = points.map(p => p[1]);
    const zValues = points.map(p => p[2]);

    const minX = Math.min(...xValues); // ... mappt durch jedes array element
    const maxX = Math.max(...xValues);
    const minY = Math.min(...yValues);
    const maxY = Math.max(...yValues);
    const minZ = Math.min(...zValues);
    const maxZ = Math.max(...zValues);

    let rangeX = (maxX - minX);
    let rangeY = (maxY - minY);
    let rangeZ = (maxZ - minZ);

    if(rangeX == 0){
      rangeX = 1;
    }
    if(rangeY == 0){
      rangeX = 1;
    }
    if(rangeZ == 0){
      rangeX = 1;
    }


    const scale = Math.min(
      (canvas.width - padding * 2) / rangeX,
      (canvas.height - padding * 2) / rangeY
    );

    canvasContext.lineWidth = 3;
    canvasContext.lineCap = 'round';
    canvasContext.lineJoin = 'round';

    for (let i = 0; i < points.length - 1; i++) { // Zeichnen der Linie
      const p1 = points[i];
      const p2 = points[i + 1];

      const x1 = (p1[0] - minX) * scale + padding;
      const y1 = (p1[1] - minY) * scale + padding;
      const x2 = (p2[0] - minX) * scale + padding;
      const y2 = (p2[1] - minY) * scale + padding;

      const avgZ = (p1[2] + p2[2]) / 2;
      const zPercent = (avgZ - minZ) / rangeZ;

      canvasContext.beginPath();
      canvasContext.strokeStyle = this.getHeightColor(zPercent);
      canvasContext.moveTo(x1, y1);
      canvasContext.lineTo(x2, y2);
      canvasContext.stroke();

      if (i == 0){
        this.drawMarker(canvasContext, x1, y1, 'green'); // Anfangspunkt am Canvas
      }
    }

    const lastPoint = points[points.length - 1];
    const lastX = (lastPoint[0] - minX) * scale + padding;
    const lastY = (lastPoint[1] - minY) * scale + padding;
    this.drawMarker(canvasContext, lastX, lastY, 'black'); // Endpunkt am Canvas
  }

  private getHeightColor(percent: number): string {
    let red = 0, green = 0;
    if (percent < 0.5) {
      red = Math.floor(255 * (percent * 2));
      green = 255;
    } else {
      red = 255;
      green = Math.floor(255 * (2 - percent * 2));
    }
    return `rgb(${red}, ${green}, 0)`;
  }

  private drawMarker(canvasContext: CanvasRenderingContext2D, x: number, y: number, color: string) { // Zeichnen im CanvasContext
    canvasContext.fillStyle = color;
    canvasContext.beginPath();
    canvasContext.arc(x, y, 5, 0, 2 * Math.PI);
    canvasContext.fill();
  }
}
