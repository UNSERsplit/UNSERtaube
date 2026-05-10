import { Component, inject } from '@angular/core';
import { MatDialogRef, MatDialogContent } from '@angular/material/dialog';
import { NgForOf } from '@angular/common';
import { flypath } from '../../../objects/flypath';
import { ControllerApiService } from '../../service/controller-api.service';
import { Router } from '@angular/router';
import {PathlistComponent} from '../pathlist/pathlist.component';

@Component({
    selector: 'app-pathlist',
    imports: [NgForOf, MatDialogContent],
    templateUrl: './pathlist-mobile.component.html',
    standalone: true,
    styleUrl: './pathlist-mobile.component.css'
})
export class PathlistMobileComponent {
    private dialogRef   = inject(MatDialogRef<PathlistComponent>);
    private controllerApi = inject(ControllerApiService);
    private router        = inject(Router);

    droneFlights: flypath[] = [];

    constructor() {
        this.controllerApi.get_paths().then(paths => {
            paths.forEach((path: any) => {
                this.droneFlights.push(new flypath(
                    path.name,
                    path.drone_name,
                    path.ip,
                    path.duration + '',
                    path.distance + '',
                    path.id
                ));
            });
        });
    }

    close(): void {
        this.dialogRef.close();
    }

    protected async replay(pathid: string): Promise<void> {
        this.dialogRef.close();
        await this.controllerApi.replay_path(pathid);
        await this.router.navigate(['flyyy']);
    }

}
