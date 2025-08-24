import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-ai-generator',
  templateUrl: './ai-generator.component.html',
  styleUrls: ['./ai-generator.component.scss'],
  animations: [
    trigger('slideInOut', [
      state('poster', style({ transform: 'translateX(0)', opacity: 1 })),
      state('image', style({ transform: 'translateX(100%)', opacity: 0 })),
      transition('poster => image', [
        animate(
          '400ms ease-in-out',
          style({ transform: 'translateX(100%)', opacity: 0 })
        ),
      ]),
      transition('image => poster', [
        animate(
          '400ms ease-in-out',
          style({ transform: 'translateX(0)', opacity: 1 })
        ),
      ]),
    ]),
    trigger('fadeInUp', [
      state('void', style({ opacity: 0, transform: 'translateY(20px)' })),
      state('*', style({ opacity: 1, transform: 'translateY(0)' })),
      transition('void => *', [animate('300ms ease-out')]),
      transition('* => void', [
        animate(
          '300ms ease-in',
          style({ opacity: 0, transform: 'translateY(20px)' })
        ),
      ]),
    ]),
  ],
})
export class AiGeneratorComponent {
  apiBase = environment.apiUrl;

  // Poster generator forms and states
  posterForm: any = {
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

  generatedFields: any = null;
  posterImage: string | null = null;

  isGeneratingFields = false;
  isGeneratingPoster = false;

  // Image generator forms and states
  imageForm: any = {
    main_prompt: '',
    aspect_ratio: '1:1',
    count: 1,
  };
  generatedImages: string[] = [];
  isGeneratingImages = false;

  // UI mode toggle
  currentMode: 'poster' | 'image' = 'poster';
  isAnimating = false;

  constructor(private http: HttpClient) {
     console.log('API base URL:', this.apiBase);
     console.log("Hi")
  }

  // Getter for animation state
  get slideState(): string {
    return this.currentMode; // 'poster' or 'image'
  }

  // ===== Poster Generator Step 1: Generate Fields =====
  generatePosterFields() {
    this.isGeneratingFields = true;
    this.generatedFields = null;
    this.posterImage = null;

    const url = `${this.apiBase}/generate-fields`;
    const body = { ...this.posterForm };

    console.log('[UI] → POST', url, body);
    this.http.post<any>(url, body).subscribe({
      next: (res) => {
        console.log('[UI] ← /generate-fields OK', res);
        this.generatedFields = res?.data || {};
        if (!this.posterForm.theme && this.generatedFields?.suggested_theme) {
          this.posterForm.theme = this.generatedFields.suggested_theme;
        }
      },
      error: (err) => {
        console.error('[UI] /generate-fields ERROR', err);
      },
      complete: () => {
        this.isGeneratingFields = false;
      },
    });
  }

  // ===== Poster Generator Step 2: Generate Poster Image =====
  generatePosterImage() {
    if (
      !this.generatedFields ||
      Object.keys(this.generatedFields).length === 0
    ) {
      console.warn(
        '[UI] No generated fields yet — call generatePosterFields() first.'
      );
      return;
    }

    this.isGeneratingPoster = true;
    this.posterImage = null;

    const url = `${this.apiBase}/generate-poster`;
    const body = {
      fields: this.generatedFields,
      theme: this.posterForm.theme || null,
    };

    console.log('[UI] → POST', url, body);
    this.http.post<any>(url, body).subscribe({
      next: (res) => {
        console.log('[UI] ← /generate-poster OK', res);
        this.posterImage = res?.image_base64 || null;
        if (!this.posterImage) {
          console.warn('[UI] /generate-poster returned no image_base64');
        }
      },
      error: (err) => {
        console.error('[UI] /generate-poster ERROR', err);
      },
      complete: () => {
        this.isGeneratingPoster = false;
      },
    });
  }

  // ===== Raw Image Generator =====
  generateImages() {
    this.isGeneratingImages = true;
    this.generatedImages = [];

    const url = `${this.apiBase}/generate-images`;
    const body = { ...this.imageForm };

    console.log('[UI] → POST', url, body);
    this.http.post<any>(url, body).subscribe({
      next: (res) => {
        console.log('[UI] ← /generate-images OK', res);
        this.generatedImages = Array.isArray(res?.images) ? res.images : [];
      },
      error: (err) => {
        console.error('[UI] /generate-images ERROR', err);
      },
      complete: () => {
        this.isGeneratingImages = false;
      },
    });
  }

  // Helpers for UI
  getFieldKeys(): string[] {
    return this.generatedFields
      ? Object.keys(this.generatedFields).filter(
          (k) => !['suggested_theme', 'custom_prompt'].includes(k)
        )
      : [];
  }

  trackByField = (_: number, key: string) => key;

  formatFieldName(key: string) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  adjustCount(delta: number) {
    const newCount = this.imageForm.count + delta;
    if (newCount >= 1 && newCount <= 3) {
      this.imageForm.count = newCount;
    }
  }

  switchMode(mode: 'poster' | 'image') {
    if (this.isAnimating) return;
    this.isAnimating = true;
    this.currentMode = mode;
    setTimeout(() => (this.isAnimating = false), 500);
  }
}

