import { Component } from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-mobile-home-button',
  imports: [],
  templateUrl: './mobile-home-button.component.html',
  styleUrl: './mobile-home-button.component.css'
})
export class MobileHomeButtonComponent {
    constructor(private router: Router) {}

    protected readonly history = history;
}
