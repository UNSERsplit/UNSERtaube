import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class DeviceService {
    isMobile = signal(window.innerWidth <= 932);

    constructor() {
        window.addEventListener('resize', () => {
            this.isMobile.set(window.innerWidth <= 932);
        });
    }
}
