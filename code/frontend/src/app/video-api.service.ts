import { Injectable, signal } from '@angular/core';
import JMuxer from 'jmuxer';

@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private muxer:  JMuxer | undefined;

  initVideo(playbackId: string) {
    this.muxer = new JMuxer({
      node: playbackId,
      mode: "video",
      debug: true
    })
  }

  feed(blob: Blob) {
    blob.arrayBuffer().then(array => {
      this.muxer?.feed({
        video: new Uint8Array(array)
      });
    })
  }
}
