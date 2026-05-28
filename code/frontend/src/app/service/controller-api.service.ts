import { inject, Injectable, signal, ViewChild } from '@angular/core';
import { VideoApiService } from './video-api.service';
import { Drone } from '../../objects/drone';

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

  /** tof distance in cm */
  tof: number;

  /** height relative to takeoff point in cm */
  h: number;

  /** motor time in s */
  time: number;

  /** height above sea level by barometer */
  baro: number;

  /** is the drone connected */
  connected: boolean;

  /** timestamp of the last update */
  last_update: number

  /** delta since this an the previous state */
  delta: number

  /** position x in cm */
  posx: number;

  /** position y in cm */
  posy: number;

  /** position z in cm */
  posz: number;

  /** distance in dm */
  distance: number;

  /** speed in dm/s */
  speed: number

  detections: {type:string, cords:[number, number, number, number]}[]
}

export type Status = "offline" | "ws_connected" | "drone_connected" | "replaying" | "error" | "connecting";


@Injectable({
  providedIn: 'root'
})
export class ControllerApiService {
  public status = signal<Status>("offline");
  public drone = signal<Drone>(new Drone("","",""));
  public state = signal<State>({pitch: NaN, roll: NaN, yaw: NaN, vgx: NaN, vgy: NaN, vgz: NaN, bat: NaN, templ: NaN, temph: NaN, agx: NaN, agy: NaN, agz: NaN, h: NaN, time: NaN, tof: NaN, baro: NaN, connected: false, last_update: NaN, delta: NaN, posx: NaN, posy: NaN, posz: NaN, distance: NaN, speed: NaN, detections: [{type:"person", cords:[10,20,950,710]}]})
  private videoApi = inject(VideoApiService);
  private waiting_messages: {
    [index: string]: [(value: object | PromiseLike<object>) => void, (reason?: any) => void, string[]]
  } = {}

  private ws!: WebSocket;

  constructor() {
    

    this.start((d: any) => this.handle_message(d))


    // Für debug zwecke die raw commands exposen
    // @ts-ignore
    window.control = this
    // @ts-ignore
    window.send_command = (command, timeout) => {
      /*this.send_debug_command(command, timeout).then((v) => {
        console.log("ANSWER:", v)
      }).catch(e => {
        console.error(e)
      });*/ 
      // TODO
    };
  }

  start(callback: any){
    this.ws = new WebSocket(`wss://${location.hostname}:8000/live/ws`);
    this.ws.addEventListener("open", e => {
        this.status.set("ws_connected");
    });
    this.ws.addEventListener("error", e => {
        this.status.set("error")
    });
    this.ws.addEventListener("close", e => {
      this.status.set("offline");
        setTimeout(() => this.start(callback), 1000);
    });
    this.ws.addEventListener("message", e => {
        callback(e.data);
    });
  }


  async action(method: string, url: string, body: any) {
    if (body) {
      body = JSON.stringify(body);
    }


    let resp = await fetch(`https://${location.hostname}:8000/` + url, {
      method: method,
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: body
    });

    if(!resp.ok) {
      const text = await resp.text();
      console.error(method, url, body, text);

      if (resp.status == 418) {
        alert("Protocol error: " + text)
      }

      throw Error(text);
    }

    const json = await resp.json()

    console.log(method, url, body, json)

    return json
  }

  async get_drones() {
    return await this.action("GET", "drone", undefined);
  }

  async get_paths() {
    return await this.action("GET", "recording", undefined);
  }

  private handle_message(d: any) {
    if (d instanceof Blob) {
      return;
    }
    const data = JSON.parse(d);
    if (!data.connected) {
      this.status.set("ws_connected");
    } else {
      if(this.status() != "drone_connected") {
        this.status.set("drone_connected");
        this.action("GET", "live/connected", undefined).then(drone => {
          this.drone.set(new Drone(drone.name, drone.ip, drone.id))
        });
      }
    
    }
    this.state.set(data);
  }

  async takeoff() {
    await this.action("POST", "live/flight/takeoff", undefined)
  }

  async land() {
    await this.action("POST", "live/flight/land", undefined)
  }

  async start_recording() {
    await this.action("POST", "recording/start", undefined)
  }

  async stop_recording() {
    await this.action("POST", "recording/stop", undefined)
  }

  async discard_recording() {
    await this.action("POST", "recording/discard", undefined)
  }

  async save_recording(name: string) {
    await this.action("POST", "recording/save?name=" + name, undefined)
  }

  send_rc(yaw: number, pitch: number, roll: number, throttle: number) { // alle Zahlen von -100 bis 100
    if(this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({"type":"rc", yaw, pitch, roll, throttle}))
  }

  async matrix(data: string) {
    await this.action("POST", "live/matrix/pattern?pattern=" + data, undefined);
  }

  async get_matrix() {
    return await this.action("GET", "live/matrix/pattern", undefined);
  }

  async flash(r1: number, r2: number, g1: number, g2: number, b1: number, b2: number, freq: number) {
    await this.action("POST", "live/rgb/flash?frequency=" + freq, {
      rgb1: [
        r1,
        g1,
        b1
      ],
      rgb2: [
        r2,
        g2,
        b2
      ]
    })
  }

  async replay_path(id: string) {
    this.status.set("replaying");
    this.action("POST", "recording/replay/" + id, undefined).catch(console.error).then(v => {
      alert(v)
    }).finally(() => {
      this.status.set("drone_connected");
    })
  }

  async emergency() {
    await this.action("POST", "live/flight/stop", undefined);
  }

  async detect_people(enable: boolean) {
    await this.action("POST", `live/people_detection?on=${enable}`, undefined)
  }

  async detect_rings(enable: boolean) {
    await this.action("POST", `live/ring_detection?on=${enable}`, undefined)
  }

  async connect(id: string) {
    this.status.set("connecting");
    
    try {
      let resp = await this.action("POST", "live/connect?drone_id=" + id, undefined)
    } catch(e) {
      this.status.set("ws_connected");
      return
    }
    let drone = await this.action("GET", "live/connected", undefined);

    this.drone.set(new Drone(drone.name, drone.ip, drone.id))

    this.status.set("drone_connected");
  }

  async createAndConnect(name: string, ip: string) {
    let drones = await this.get_drones();

    for (const drone of drones) {
      if(drone.ip == ip) {
        return await this.connect(drone.id);
      }
    }

    const drone = await this.action("POST", "drone/", {
      "name": name,
      "ip": ip
    });

    return await this.connect(drone.id);
  }

  disconnect() {
    //TODO
    this.status.set("ws_connected");
  }
}
