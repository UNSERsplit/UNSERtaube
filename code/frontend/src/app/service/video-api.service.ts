import { Injectable, signal } from '@angular/core';

declare var MediaMTXWebRTCReader: any;

@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLVideoElement | undefined;
  private stream: any;
  private reader: any;


  setMessage(msg: any) {
    console.warn(msg)
  }


  constructor() {
    var scriptTag = document.createElement('script');
    scriptTag.src = `http://${location.hostname}:8889/camera/reader.js`;

    scriptTag.onload = () => {
      console.log("FDSAFDSFDSAFDSFA")
      this.reader = new MediaMTXWebRTCReader({ // @ts-ignore
        url: new URL(`http://${location.hostname}:8889/camera/whep`),
        onError: (err: any) => {
          this.setMessage(err);
        },
        onTrack: (evt: any) => {
          this.setMessage('');
          this.stream = evt.streams[0];
          if (this.element) {
            this.element!.srcObject = evt.streams[0];
          }
        },
        onDataChannel: (evt: any) => {
          evt.channel.binaryType = 'arraybuffer';
          evt.channel.onmessage = (evt: any) => {
            console.log('data channel message', evt.data);
          };
        },
      });


    window.addEventListener('beforeunload', () => {
      
    });
  };

    document.body.appendChild(scriptTag);
  }


  initVideo(playbackId: string) {
    this.element = document.getElementById(playbackId) as HTMLVideoElement;
    this.element.controls = false;
    this.element.muted = true;
    this.element.autoplay = true;
    this.element.playsInline = true;

    if(this.stream) {
      this.element!.srcObject = this.stream;
    }
  }

  removeVideo() {
    /*if (this.reader !== null) {
      this.reader.close();
    }*/
  }
}
