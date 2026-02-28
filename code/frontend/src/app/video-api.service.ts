import { Injectable, signal } from '@angular/core';


@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLVideoElement | undefined;
  private mediaSource: MediaSource | undefined;
  private sourceBuffer: SourceBuffer | undefined;
  private peer: RTCPeerConnection;

  constructor() {
    this.peer = new RTCPeerConnection();
    this.peer.addTransceiver('video', { direction: 'recvonly' });
  }


  initVideo(playbackId: string) {
    this.peer.addEventListener("track", event => {
      this.element!.srcObject = event.streams[0];
      this.element?.play()
    })

    this.element = document.getElementById(playbackId) as HTMLVideoElement;
  }

  async connect(): Promise<RTCSessionDescription> {
    const offer = await  this.peer.createOffer();
    await this.peer.setLocalDescription(offer);

    return this.peer.localDescription!;
  }

  async set_rtc(desc: RTCSessionDescriptionInit): Promise<undefined> {
    await this.peer.setRemoteDescription(desc);
  }
}
