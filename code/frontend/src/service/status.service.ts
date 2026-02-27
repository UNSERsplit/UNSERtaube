import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root' // Das sorgt dafür, dass die ganze App denselben Service nutzt
})
export class StatusService {
    // 1. Der "Sender" (intern)
    private statusTrigger = new Subject<void>();

    // 2. Der "Funkkanal" (extern für die Komponenten)
    statusObservable$ = this.statusTrigger.asObservable();

    // 3. Die Methode, um das Signal auszulösen
    triggerStatusChange() {
        this.statusTrigger.next(); // "Pling! Es hat sich was geändert!"
    }
}
