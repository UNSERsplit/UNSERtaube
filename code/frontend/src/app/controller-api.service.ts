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
  public state = signal<State>({pitch: NaN, roll: NaN, yaw: NaN, vgx: NaN, vgy: NaN, vgz: NaN, bat: NaN, templ: NaN, temph: NaN, agx: NaN, agy: NaN, agz: NaN})
  private videoApi = inject(VideoApiService);
  private waiting_messages: {
    [index: string]: [(value: object | PromiseLike<object>) => void, (reason?: any) => void]
  } = {}

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
        
      } else {

        const data = JSON.parse(ev.data);
        if (data.type === "validation_error") {
          alert("Validation error, fix the ws message format");
          alert(data.context);
        }

        switch(data.type) {
          case "state": {
            const newState:State = data.state
            console.log(data.state.vgx, data.state.vgy, data.state.vgz)
            this.state.set(newState);
            break;
          }
        }

        const waiting_message = this.waiting_messages[data.type];
        if (waiting_message) {
          waiting_message[0](data); // resolve promise
          delete this.waiting_messages[data.type]
        }

        this.status.set("message:" + data.type + ":" + i);
        i++;
      }
    });
  }

  wait_for_response(required_type: string, timeout:number): Promise<object> {
    const promise = new Promise((resolve, reject) => {
      const auto_reject = setTimeout(() => {
        if(this.waiting_messages[required_type]) {
          reject({"type": "timeout", "required_message": required_type, timeout})
          delete this.waiting_messages[required_type]
        }
      }, timeout)
      this.waiting_messages[required_type] = [resolve, reject]
    }) as Promise<object>

    return promise;
  }

  takeoff() {
    this.ws.send(JSON.stringify({"type":"takeoff"}))
  }

  land() {
    this.ws.send(JSON.stringify({"type":"land"}))
  }

  start_recording() {
    this.ws.send(JSON.stringify({"type":"record_start"}))
  }

  send_rc(yaw: number, pitch: number, roll: number, throttle: number) {
    this.ws.send(JSON.stringify({"type":"rc", yaw, pitch, roll, throttle}))
  }

  async stop_recording() {
    this.ws.send(JSON.stringify({"type":"record_stop"}))
    const data: any = await this.wait_for_response("recording_name", 5_000);
    return data.name;
  }

  async connect(ip: string) {
    const conn = await this.videoApi.connect();
    this.ws.send(JSON.stringify({"type":"select_drone", "ip": ip, "rtc_sdp": conn.sdp, "rtc_type": conn.type}))
    const data: any = await this.wait_for_response("drone_connected",10_000);
    await this.videoApi.set_rtc({
      type: data.rtc_type,
      sdp: data.rtc_sdp
    })
  }
}
