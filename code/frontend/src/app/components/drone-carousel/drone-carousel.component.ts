import {Component, inject} from '@angular/core';
import {Drone} from '../../../objects/drone';
import {Router} from '@angular/router';
import { ControllerApiService } from '../../controller-api.service';

@Component({
  selector: 'app-drone-carousel',
  imports: [],
  templateUrl: './drone-carousel.component.html',
  styleUrl: './drone-carousel.component.css', standalone: true,

})
export class DroneCarouselComponent {
    private router = inject(Router);
    private controller = inject(ControllerApiService);

    items : any = [
        {
            name: "Drone 7 Hotspot",
            ip: "192.168.43.49",
            id: "hotspot7",
            color: '#ffadad'
        },
        {
            name: "Drone 2",
            ip: "4.3.2.1",
            id: "myid2",
            color: '#ffd6a5'
        }
        /*{color: '#ffadad' },
        { title: 'Card 2', color: '#ffd6a5' },
        { title: 'Card 3', color: '#fdffb6' },
        { title: 'Card 4', color: '#caffbf' },
        { title: 'Card 5', color: '#9bf6ff' },
        { title: 'Card 6', color: '#a0c4ff' }*/
    ]; // TODO get from server

    currentIndex = 0;

    next() {
        console.log(this.items.length);
        // Verhindert das Überlaufen (zeigt immer 3 an)
        if (this.currentIndex < this.items.length - 3) {
            this.currentIndex++;
        } else {
            this.currentIndex = 0; // Loop zurück zum Anfang
        }
    }

    prev() {
        console.log(this.items.length);
        if (this.currentIndex > 0) {
            this.currentIndex--;
        } else {
            this.currentIndex = this.items.length - 3; // Loop zum Ende
        }
    }

    selectDrone(drone: any){
        this.controller.connect(drone.name, drone.ip);
    }
}
