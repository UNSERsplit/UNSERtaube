import { inject, Injectable, signal, ViewChild } from '@angular/core';
import { VideoApiService } from './video-api.service';
import { Drone } from '../objects/drone';

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

export type Status = "offline" | "ws_connected" | "drone_connected" | "error" | "connecting";


@Injectable({
  providedIn: 'root'
})
export class ControllerApiService {
  public status = signal<Status>("offline");
  public drone = signal<Drone | undefined>(undefined);
  public state = signal<State>({pitch: NaN, roll: NaN, yaw: NaN, vgx: NaN, vgy: NaN, vgz: NaN, bat: NaN, templ: NaN, temph: NaN, agx: NaN, agy: NaN, agz: NaN})
  private videoApi = inject(VideoApiService);
  private waiting_messages: {
    [index: string]: [(value: object | PromiseLike<object>) => void, (reason?: any) => void, string[]]
  } = {}
  public pathmapsignal = signal<[number, number, number][]>([]);

  private ws: WebSocket;

  constructor() {
    this.ws = new WebSocket(`wss://${location.hostname}:${location.port}/api/ws`);
    this.ws.addEventListener("open", ev => {
      console.log(ev)
      this.status.set("ws_connected");
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
          case "waypoints": {
            this.pathmapsignal.set(data.context);
          }
        }

        const waiting_message = this.waiting_messages[data.type];
        if (waiting_message) {
          waiting_message[0](data); // resolve promise
          this.clear_waiting_message(data.type)
        }

        i++;
      }
    });
  }

  private clear_waiting_message(type: string) {
    if (!this.waiting_messages[type]) return;

    const reject_types = this.waiting_messages[type][2];
    delete this.waiting_messages[type]
    reject_types.forEach(reject => {
      this.clear_waiting_message(reject);
    })
  }

  wait_for_response(required_type: string, timeout:number, reject_types: string[] = []): Promise<object> {
    const promise = new Promise((resolve, reject) => {
      const auto_reject = setTimeout(() => {
        if(this.waiting_messages[required_type]) {
          reject({"type": "timeout", "required_message": required_type, timeout})
          this.clear_waiting_message(required_type)
        }
      }, timeout)
      this.waiting_messages[required_type] = [resolve, reject, reject_types]
      reject_types.forEach(type => {
        this.waiting_messages[type] = [reject, resolve, [...reject_types, required_type]]
      })
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

  send_rc(yaw: number, pitch: number, roll: number, throttle: number) { // alle Zahlen von -100 bis 100
    if(this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({"type":"rc", yaw, pitch, roll, throttle}))
  }

  async stop_recording() {
    this.ws.send(JSON.stringify({"type":"record_stop"}))
    const data: any = await this.wait_for_response("recording_name", 5_000);
    return data.name;
  }

  async connect(name: string, ip: string) {
    this.status.set("connecting");
    const conn = await this.videoApi.connect();
    this.ws.send(JSON.stringify({"type":"select_drone", "ip": ip, "rtc_sdp": conn.sdp, "rtc_type": conn.type}))
    try {
      const data: any = await this.wait_for_response("drone_connected",10_000, ["drone_disconnected"]);
      await this.videoApi.set_rtc({
        type: data.rtc_type,
        sdp: data.rtc_sdp
      })
    } catch (e: any) {
      this.status.set("ws_connected");
      alert(e.reason)
      return;
    }

    this.drone.set(new Drone(name, ip))

    this.status.set("drone_connected");
  }

  disconnect() {
    //TODO
    this.status.set("ws_connected");
  }
}
