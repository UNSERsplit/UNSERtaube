import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLCanvasElement | undefined;
  private context: CanvasRenderingContext2D | undefined;
  private jmuxer: any;

  initVideo(playbackId: string) {
    this.jmuxer = eval(`new JMuxer({
			node: "${playbackId}",
			mode: 'video',
			flushingTime: 0,
			fps: 30,
			debug: true
		 });`);
    //this.element = document.getElementById(playbackId) as HTMLCanvasElement;

    //this.context = this.element.getContext("2d") as CanvasRenderingContext2D;
  }

  feed(b: Blob) {
    b.bytes().then(d => {
      this.jmuxer.feed({
        video: d
      });
    });

    /*var blob = new Blob([b], {type: 'image/bmp'});
    var url = URL.createObjectURL(blob);
    var img = new Image;

    img.onload = () => {
        this.context!.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
    }
    img.src = url;*/
  }
}
