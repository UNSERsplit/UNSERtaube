import { Routes } from '@angular/router';
import {LoginPageComponent} from './pages/login.page/login.page.component';
import {FlugmenuPageComponent} from './pages/flugmenu.page/flugmenu.page.component';
import {FlugPageComponent} from './pages/flug.page/flug.page.component';


export const routes: Routes = [
    { path: 'login-page', component: LoginPageComponent },
    { path: 'home', component: FlugmenuPageComponent },
    {path: 'flyyy', component: FlugPageComponent },
    { path: '', redirectTo: 'login-page', pathMatch: 'full' }
];
