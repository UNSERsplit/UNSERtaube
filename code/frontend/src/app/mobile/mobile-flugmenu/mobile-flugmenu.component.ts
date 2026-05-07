import { Component, HostListener, OnInit } from '@angular/core';
import {TitelComponent} from '../../components/titel/titel.component';
import {ConnectedDroneComponent} from '../../components/connected-drone/connected-drone.component';
import {StartCardComponent} from '../../components/start-drone/start-card.component';
import {FlypathComponent} from '../../components/flypath/flypath.component';
import {LedControlComponent} from '../../components/led-control/led-control.component';
import {PathlistComponent} from '../../components/pathlist/pathlist.component';
import {MatDialog} from '@angular/material/dialog';
import {LedEditorComponent} from '../../components/led-editor/led-editor.component';
import {ConnectedDroneMobileComponent} from '../../components/connected-drone-mobile/connected-drone-mobile.component';
import {CardComponent} from '../../components/card/card.component';
import {CardVariants} from '../../components/card/card.variants';
import {LedEditorMobileComponent} from '../../components/led-editor-mobile/led-editor-mobile.component';
import {PathlistMobileComponent} from '../../components/pathlist-mobile/pathlist-mobile.component';

@Component({
    selector: 'app-mobile-flugmenu',
    imports: [
        TitelComponent,
        FlypathComponent,
        LedControlComponent,
        ConnectedDroneMobileComponent,
        StartCardComponent,
        CardComponent
    ],
    templateUrl: './mobile-flugmenu.component.html',
    styleUrl: './mobile-flugmenu.component.css',
    standalone: true,
})
export class MobileFlugmenuComponent {
    cwitdh:string="34rem";
    cheight:string="3rem";

    titleFontSize: number = 48;
    titleMargin: number = 3;

    private get isMobileLandscape(): boolean {
        return window.innerWidth > window.innerHeight && window.innerHeight < 500;
    }

    ngOnInit(): void {
        this.updateLayout();
    }

    @HostListener('window:resize')
    @HostListener('window:orientationchange')
    onOrientationChange(): void {
        // Kurze Verzögerung, damit der Browser das Layout fertig berechnet
        setTimeout(() => this.updateLayout(), 100);
    }

    private updateLayout(): void {
        if (this.isMobileLandscape) {
            this.titleFontSize = 28;
            this.titleMargin = 4;
        } else {
            this.titleFontSize = 72;
            this.titleMargin = 10;
        }
    }

    protected readonly CardVariants = CardVariants;
    protected flexdirection: string = 'column';

    constructor(public dialog: MatDialog) {}

    openPopup() {
        this.dialog.open(LedEditorMobileComponent, {
            width: 'auto',
            height: 'auto',
            minHeight: 'auto',
            panelClass: ['scrollbar-dark', 'purpleShadow'],
            maxWidth: 'none',
            maxHeight: 'none',
        });
    }
    openPathlist(): void {
        this.dialog.open(PathlistMobileComponent, {
            // Nimmt die volle Breite, Bottom-Sheet-Stil im Landscape
            width:     '100vw',
            height: '100vw',
            maxWidth:  '90vw',
            maxHeight: '80dvh',
            panelClass: ['scrollbar-dark', 'purpleShadow'],
            enterAnimationDuration: '200ms',
            exitAnimationDuration:  '150ms',

        });
}}
