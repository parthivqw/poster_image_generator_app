import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; // animations

import { AppComponent } from './app.component';
import { PosterFormComponent } from './components/poster-form/poster-form.component';
import { AiGeneratorComponent } from './components/ai-generator/ai-generator.component';

@NgModule({
  declarations: [AppComponent, PosterFormComponent, AiGeneratorComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule,BrowserAnimationsModule],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
