import { Component } from '@angular/core';
import {Drone} from '../../../objects/drone';

@Component({
  selector: 'app-drone-carousel',
  imports: [],
  templateUrl: './drone-carousel.component.html',
  styleUrl: './drone-carousel.component.css', standalone: true,

})
export class DroneCarouselComponent {
    drone: Drone = new Drone("Herbert", "192.168.0.2");

    items : any = [
        {color: '#ffadad' },
        { title: 'Card 2', color: '#ffd6a5' },
        { title: 'Card 3', color: '#fdffb6' },
        { title: 'Card 4', color: '#caffbf' },
        { title: 'Card 5', color: '#9bf6ff' },
        { title: 'Card 6', color: '#a0c4ff' }
    ];

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
}
