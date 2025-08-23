import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AiGeneratorComponent } from './ai-generator.component';

describe('AiGeneratorComponent', () => {
  let component: AiGeneratorComponent;
  let fixture: ComponentFixture<AiGeneratorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AiGeneratorComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AiGeneratorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
