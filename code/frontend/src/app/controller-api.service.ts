import { inject, Injectable, signal, ViewChild } from '@angular/core';
import { VideoApiService } from './video-api.service';

export interface State {
  /** pitch in degrees */
  pitch: number;

  /** roll in degrees */
  roll: number;

  /** yaw in degrees */
  yaw: number;

  /** speed x in dm/s */
  vgx: number;

  /** speed y in dm/s */
  vgy: number;

  /** speed z in dm/s */
  vgz: number;

  /** battery in percent */
  bat: number;

  /** temperature range low in °C */
  templ: number;

  /** temperature range high in °C */
  temph: number;

  /** acceleration x in cm/s² */
  agx: number;

  /** acceleration y in cm/s² */
  agy: number;

  /** acceleration z in cm/s² */
  agz: number;
}


@Injectable({
  providedIn: 'root'
})
export class ControllerApiService {
  public status = signal("offline");
  video: any;
  public state = signal<State>({pitch: NaN, roll: NaN, yaw: NaN, vgx: NaN, vgy: NaN, vgz: NaN, bat: NaN, templ: NaN, temph: NaN, agx: NaN, agy: NaN, agz: NaN})
  private videoApi = inject(VideoApiService);

  private ws: WebSocket;

  constructor() {
    this.ws = new WebSocket(`wss://${location.hostname}:${location.port}/api/ws`);
    this.ws.addEventListener("open", ev => {
      console.log(ev)
      this.status.set("ok");
    });

    this.ws.addEventListener("error", ev => {
      console.error(ev)

      this.status.set("error")
    });

    let i = 0;
    this.ws.addEventListener("message", ev => {
      if(ev.data instanceof Blob) {
        // video frame
        this.videoApi.setFrame(ev.data);
      } else {

        const data = JSON.parse(ev.data);
        if (data.type === "validation_error") {
          alert("Validation error, fix the ws message format");
          alert(data.context);
        }

        switch(data.type) {
          case "state": {
            const newState:State = data.state
            this.state.set(newState);
            break;
          }
        }

        this.status.set("message:" + data.type + ":" + i);
        i++;
      }
    });
  }

  takeoff() {
    this.ws.send(JSON.stringify({"type":"takeoff"}))
  }

  land() {
    this.ws.send(JSON.stringify({"type":"land"}))
  }

  connect(ip: string) {
    this.videoApi.setElement(this.video);
    this.videoApi.initVideo();
    this.ws.send(JSON.stringify({"type":"select_drone", "ip": ip}))
  }
}
