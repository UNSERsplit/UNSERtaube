import {Component, inject} from '@angular/core';
import {Drone} from '../../../objects/drone';
import {Router} from '@angular/router';
import { ControllerApiService } from '../../controller-api.service';

const COLORS = [
    '#ffadad',
    '#ffd6a5',
    '#fdffb6',
    '#caffbf',
    '#9bf6ff',
    '#a0c4ff'
]

@Component({
  selector: 'app-drone-carousel',
  imports: [],
  templateUrl: './drone-carousel.component.html',
  styleUrl: './drone-carousel.component.css', standalone: true,

})
export class DroneCarouselComponent {
    private router = inject(Router);
    private controller = inject(ControllerApiService);

    items: {name: string, ip: string, id: string, color: string}[] = []; // TODO get from server

    currentIndex = 0;

    constructor() {
        this.items = []
        this.controller.get_drones().then(drones => {
            drones.forEach((v: any) => {
                console.log(v.id)
                const hash = BigInt("0x" + v.id.replaceAll("-",""))
                const color = COLORS[Number(hash % BigInt(COLORS.length))]

                this.items.push(
                    {
                        name: v.name,
                        ip: v.ip,
                        id: v.id,
                        color: color
                    }
                )
            })
        })
    }

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
