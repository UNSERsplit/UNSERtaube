import { Component, effect, HostListener, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { ControllerApiService } from '../../controller-api.service';

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
    "Control": false,
    "Shift": false
  })

  private controllerApi = inject(ControllerApiService);

  constructor() {
    effect(() => {
      const throttle = (this.keys()["Shift"] ? 100 : 0) + (this.keys()["Control"] ? -100 : 0)
      const roll = (this.keys()["a"] ? 100 : 0) + (this.keys()["d"] ? -100 : 0)
      const pitch = (this.keys()["w"] ? 100 : 0) + (this.keys()["s"] ? -100 : 0)
      const yaw = (this.keys()["q"] ? 100 : 0) + (this.keys()["e"] ? -100 : 0)

      this.controllerApi.send_rc(
        yaw/2, pitch/2, roll/2, throttle/2
      )
    })
  }

  @HostListener("window:keydown", ['$event'])
  onKeyDown(event: KeyboardEvent) {
    if(!(event.key in this.keys())) return
    this.keys.update((v) => {
      v[event.key] = true;
      return structuredClone(v);
    });
  }

  @HostListener("window:keyup", ['$event'])
  onKeyUp(event: KeyboardEvent) {
    if(!(event.key in this.keys())) return
    this.keys.update((v) => {
      v[event.key] = false;
      return structuredClone(v);
    });
  }
}
