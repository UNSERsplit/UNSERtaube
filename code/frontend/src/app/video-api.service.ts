import { Injectable, signal } from '@angular/core';


@Injectable({
  providedIn: 'root'
})
export class VideoApiService {
  private element: HTMLVideoElement | undefined;
  private stream: MediaStream | undefined;
  private peer: RTCPeerConnection;

  constructor() {
    this.peer = new RTCPeerConnection();
    this.peer.addTransceiver('video', { direction: 'recvonly' });

    this.peer.addEventListener("track", event => {
        this.stream = event.streams[0];

        if(this.element) {
          this.element.srcObject = this.stream!;
          this.element.play()
        }
      })
  }


  initVideo(playbackId: string) {
    this.element = document.getElementById(playbackId) as HTMLVideoElement;

    if(this.stream) {
      this.element.srcObject = this.stream!;
      this.element.play()
    }
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
