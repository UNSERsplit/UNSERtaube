import { Component, effect, HostListener, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { ControllerApiService } from '../../service/controller-api.service';

@Component({
  selector: 'app-keyboard-input',
  imports: [],
  template: "",
  styleUrl: './keyboard-input.component.css'
})
export class KeyboardInputComponent implements OnInit, OnDestroy{
  ngOnInit(): void {

  }
  ngOnDestroy(): void {

  }
  private keys = signal<{
    [index: string]: boolean
  }>({
    "w": false,
    "a": false,
    "s": false,
    "d": false,
    "q": false,
    "e": false,
    "arrowup": false,
    "arrowdown": false
  })

  private controllerApi = inject(ControllerApiService);

  constructor() {
    effect(() => {
      const throttle = (this.keys()["arrowup"] ? 100 : 0) + (this.keys()["arrowdown"] ? -100 : 0)
      const roll = (this.keys()["a"] ? -100 : 0) + (this.keys()["d"] ? 100 : 0)
      const pitch = (this.keys()["w"] ? 100 : 0) + (this.keys()["s"] ? -100 : 0)
      const yaw = (this.keys()["q"] ? -100 : 0) + (this.keys()["e"] ? 100 : 0)

      this.controllerApi.send_rc(
        yaw, pitch, roll, throttle
      )
    })
  }

  @HostListener("window:keydown", ['$event'])
  onKeyDown(event: KeyboardEvent) {
    console.log(event.key)
    if(!(event.key.toLowerCase() in this.keys())) return
    this.keys.update((v) => {
      v[event.key.toLowerCase()] = true;
      return structuredClone(v);
    });
  }

  @HostListener("window:keyup", ['$event'])
  onKeyUp(event: KeyboardEvent) {
    if(!(event.key.toLowerCase() in this.keys())) return
    this.keys.update((v) => {
      v[event.key.toLowerCase()] = false;
      return structuredClone(v);
    });
  }
}
