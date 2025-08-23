import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-poster-form',
  templateUrl: './poster-form.component.html',
  styleUrls: ['./poster-form.component.scss'],
})
export class PosterFormComponent {
  form = {
    main_prompt: '',
    theme: '',
    include_hero_headline: false,
    include_hero_subline: false,
    include_description: false,
    include_cta: false,
    include_testimonial: false,
    include_success_metrics: false,
    include_target_audience: false,
    include_cta_link: false,
    custom_prompt: '',
  };

  aiResponse: { [key: string]: string } = {}; // Generated fields from backend
  posterBase64: string = ''; // Holds the final image (base64)
  isLoading: boolean = false; // Controls shimmer

  constructor(private http: HttpClient) {}

  // Step 1: Call LLaMA API to get poster fields
  submitForm() {
    console.log('Sending this form data:', this.form);

    this.http
      .post<any>('http://localhost:8000/generate-fields', this.form)
      .subscribe(
        (res) => {
          console.log('Response from backend:', res);
          this.aiResponse = res?.data || {};
        },
        (err) => {
          console.error('Backend Error:', err);
        }
      );
  }

  // Step 2: Call Imagen API to generate poster
  generatePoster() {
    const payload = {
      fields: this.aiResponse,
      theme: this.form.theme,
    };

    this.isLoading = true; // Start shimmer
    this.posterBase64 = ''; // Clear previous image if any

    console.log('Sending final payload for poster generation:', payload);

    this.http
      .post<any>('http://localhost:8000/generate-poster', payload)
      .subscribe(
        (res) => {
          console.log('Final base64 image received');
          this.posterBase64 = res.image_base64;
          this.isLoading = false;
        },
        (err) => {
          console.error('Image generation failed:', err);
          this.isLoading = false;
        }
      );
  }

  getAiFieldKeys(): string[] {
    return Object.keys(this.aiResponse || {});
  }

  // Format field names for better display (e.g., "hero_headline" -> "Hero Headline")
  formatFieldName(fieldName: string): string {
    return fieldName
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
}
