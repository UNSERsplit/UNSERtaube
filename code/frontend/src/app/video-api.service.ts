import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLVideoElement | undefined;
  private mediaSource: MediaSource | undefined;
  private sourceBuffer: SourceBuffer | undefined;


  initVideo(playbackId: string) {
    this.element = document.getElementById(playbackId) as HTMLVideoElement;

    this.mediaSource = new MediaSource();

    this.mediaSource.addEventListener("sourceopen", () => {
      console.log("Source opened")

      this.sourceBuffer = this.mediaSource?.addSourceBuffer("video/mp4")
    });

    this.mediaSource.addEventListener("sourceclose", () => {
      console.error("Source closed")
    });

    this.element.src = URL.createObjectURL(this.mediaSource);
  }

  feed(b: Blob) {
    this.element?.play()

    const updateFunction = () => {
      this.sourceBuffer?.removeEventListener("updateend", updateFunction)

      b.arrayBuffer().then(buffer => {

        this.sourceBuffer?.appendBuffer(buffer)
        console.log(this.element?.buffered, this.element?.duration, this.element?.currentTime)
        let max = 0;
        for (let index = 0; index < this.element!.buffered.length; index++) {
          let a = this.element!.buffered.end(index);
          if (a > max) {
            max = a;
          }
        }
        if (!(max == 0 || max === Infinity)) {
          this.element!.currentTime = max - 0.1;
        }
      })
    }

    if(this.sourceBuffer?.updating) {
      this.sourceBuffer.addEventListener("updateend", updateFunction)
    } else {
      updateFunction()
    }
  }
}
