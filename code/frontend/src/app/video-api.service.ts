import { Injectable, signal } from '@angular/core';


@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLCanvasElement | undefined;
  private ctx: CanvasRenderingContext2D | null = null;

  constructor() {
    
  }


  initVideo(playbackId: string) {
    this.element = document.getElementById(playbackId) as HTMLCanvasElement;

    this.ctx = this.element.getContext("2d");
  }

  set_frame(buf: ArrayBuffer) {
    if(!this.ctx) return;
    const view = new DataView(buf);

    const width = view.getUint32(0, true);
    const height = view.getUint32(4, true);

    this.ctx.canvas.width  = width;
    this.ctx.canvas.height = height;

    const src = new Uint8Array(buf, 12); // RGB data
    const dst = new Uint8ClampedArray(width * height * 4);

    let j = 0;
    for (let i = 0; i < src.length; i += 3) {
      dst[j++] = src[i]; // R
      dst[j++] = src[i + 1]; // G
      dst[j++] = src[i + 2];     // B
      dst[j++] = 255;        // A
    }

    const imageData = new ImageData(dst, width, height);
    this.ctx.putImageData(imageData, 0, 0);
  }
}
