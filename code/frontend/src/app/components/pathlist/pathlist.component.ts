import {Component, Input} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import {NgForOf} from '@angular/common';
import {flypath} from '../../../objects/flypath';


@Component({
  selector: 'app-pathlist',
    imports: [
        CardComponent,
        NgForOf
    ],
  templateUrl: './pathlist.component.html',
  styleUrl: './pathlist.component.css'
})
export class PathlistComponent {

    protected readonly CardVariants = CardVariants;
    buttonWidth: string = '60rem';
    buttonHeight: string = '20rem';
    //@Input() shadow: string = "rgba(0, 255, 0, 0.75) 0px 0px 4px, rgba(0, 255, 0, 0.75) 0px 0px 4px, rgba(0, 255, 0, 0.75) 0px 0px 4px";

    items = ['Angular lernen', 'Einkaufen gehen', 'Fitnessstudio', 'Projekt abschließen'];

    dachCheck = new flypath(
        'Dachinspektion',
        'Max',
        '192.168.0.12',
        '12', // in Minuten (ohne Einheit)
        '450' // in Metern (ohne Einheit)
    );

    gartenRunde = new flypath(
        'Garten-Scan',
        'Sophie',
        '192.168.0.15',
        '8',
        '120'
    );

    parkTest = new flypath(
        'Manövertest',
        'Lukas',
        '10.0.0.42',
        '25',
        '2100'
    );

    droneFlights: flypath[] = [
        this.dachCheck,
        this.gartenRunde,
        this.parkTest,
    ];
    protected readonly flypath = flypath;
}
