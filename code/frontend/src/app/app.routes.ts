import { Routes } from '@angular/router';
import {LoginPageComponent} from './dektop/desktop-login-page/login-page.component';
import {DektopFlugmenuComponent} from './dektop/dektop-flugmenu/dektop-flugmenu.component';
import {DesktopFlugComponent} from './dektop/desktop-flug/desktop-flug.component';


export const routes: Routes = [
    { path: 'login-page', component: LoginPageComponent },
    { path: 'home', component: DektopFlugmenuComponent },
    {path: 'flyyy', component: DesktopFlugComponent },
    { path: '', redirectTo: 'login-page', pathMatch: 'full' }
];
