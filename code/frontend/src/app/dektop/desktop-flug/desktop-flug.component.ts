import { Component, inject, OnInit } from '@angular/core';
import { VideoApiService } from '../../video-api.service';

@Component({
  selector: 'app-desktop-flug',
  imports: [],
  templateUrl: './desktop-flug.component.html',
  styleUrl: './desktop-flug.component.css'
})
export class DesktopFlugComponent implements OnInit{
  private videoApi = inject(VideoApiService);

  constructor() {
    
  }

  ngOnInit(): void {
    this.videoApi.initVideo("video")
  }
}
