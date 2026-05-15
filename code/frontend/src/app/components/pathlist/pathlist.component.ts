import {Component, inject, Input} from '@angular/core';
import {CardComponent} from '../card/card.component';
import {CardVariants} from '../card/card.variants';
import {NgForOf} from '@angular/common';
import {flypath} from '../../../objects/flypath';
import { ControllerApiService } from '../../service/controller-api.service';
import { Router } from '@angular/router';


@Component({
    selector: 'app-pathlist',
    imports: [
        CardComponent,
        NgForOf
    ],
    templateUrl: './pathlist.component.html',
    standalone: true,
    styleUrl: './pathlist.component.css'
})
export class PathlistComponent {

    private controllerApi = inject(ControllerApiService);
    private router = inject(Router);

    protected readonly CardVariants = CardVariants;
    buttonWidth: string = '60rem';
    buttonHeight: string = '20rem';
    //@Input() shadow: string = "rgba(0, 255, 0, 0.75) 0px 0px 4px, rgba(0, 255, 0, 0.75) 0px 0px 4px, rgba(0, 255, 0, 0.75) 0px 0px 4px";

    droneFlights: flypath[] = [];
    protected readonly flypath = flypath;

    constructor() {
        this.controllerApi.get_paths().then(paths => {
            paths.forEach((path: any) => {
                this.droneFlights.push(new flypath(
                    path.name,
                    path.drone.name,
                    path.drone.ip,
                    parseInt(path.duration) + "",
                    parseInt(path.distance) + "",
                    path.id
                ))
            })
        })
    }

    protected async replay(pathid: string) {
        await this.controllerApi.replay_path(pathid);
        await this.router.navigate(["flyyy"])
    }
}
