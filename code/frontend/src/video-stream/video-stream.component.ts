import { Component, ElementRef, inject, OnInit, ViewChild } from '@angular/core';
import { VideoApiService } from '../app/service/video-api.service';
import { OverlayComponent } from './overlay/overlay.component';

@Component({
  selector: 'video-stream',
  imports: [OverlayComponent],
  templateUrl: './video-stream.component.html',
  styleUrl: './video-stream.component.css'
})
export class VideoStreamComponent implements OnInit{
  private videoApi = inject(VideoApiService);
  @ViewChild("video") video: ElementRef<HTMLVideoElement> | undefined;

  ngOnInit(): void {
    this.videoApi.initVideo("video-stream")
  }
}
