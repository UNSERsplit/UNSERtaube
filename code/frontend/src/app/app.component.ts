import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  styleUrl: './app.component.css',
  template: `
    <H1> Welcome to {{title}}!</H1>
    <router-outlet/>
  `
})
export class AppComponent {
  title = 'frontend';
}
