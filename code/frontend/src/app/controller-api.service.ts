import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ControllerApiService {
  public status = signal("offline");
  
  private ws: WebSocket;

  constructor() {
    this.ws = new WebSocket(`wss://${location.hostname}:${location.port}/api/ws`);
    this.ws.addEventListener("open", ev => {
      console.log(ev)

      this.status.set("ok")
    });

    this.ws.addEventListener("error", ev => {
      console.error(ev)

      this.status.set("error")
    });

    let i = 0;
    this.ws.addEventListener("message", ev => {
      console.error(ev.data)

      this.status.set("message " + i);
      i++;
    });
  }

  takeoff() {
    this.ws.send(JSON.stringify({"type":"takeoff"}))
  }

  land() {
    this.ws.send(JSON.stringify({"type":"land"}))
  }

  connect(ip: string) {
    this.ws.send(JSON.stringify({"type":"select_drone", "ip": ip}))
  }
}
