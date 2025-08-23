import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PosterFormComponent } from './poster-form.component';

describe('PosterFormComponent', () => {
  let component: PosterFormComponent;
  let fixture: ComponentFixture<PosterFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PosterFormComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PosterFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
