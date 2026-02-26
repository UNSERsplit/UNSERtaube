import { Component, ElementRef, inject, OnInit, ViewChild } from '@angular/core';
import { VideoApiService } from '../app/video-api.service';

@Component({
  selector: 'video-stream',
  imports: [],
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
