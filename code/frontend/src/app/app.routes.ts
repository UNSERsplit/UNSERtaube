import { Routes } from '@angular/router';
import {LoginPageComponent} from './dektop/desktop-login-page/login-page.component';
import {DektopFlugmenuComponent} from './dektop/dektop-flugmenu/dektop-flugmenu.component';


export const routes: Routes = [
    { path: 'login-page', component: LoginPageComponent },
    { path: 'home', component: DektopFlugmenuComponent },
    { path: '', redirectTo: 'login-page', pathMatch: 'full' }
];
