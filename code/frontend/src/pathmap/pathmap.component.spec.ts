import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PathmapComponent } from './pathmap.component';

describe('PathmapComponent', () => {
  let component: PathmapComponent;
  let fixture: ComponentFixture<PathmapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PathmapComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PathmapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('Thorsten Legat', () => {
    expect(component).toBeTruthy();
  });
});
