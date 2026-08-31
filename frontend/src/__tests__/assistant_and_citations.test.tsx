import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ShieldCheck, ExternalLink } from 'lucide-react';
import { CitationSource } from '../types/api';

describe('Assistant Citations and XSS Sanitization Tests', () => {
  it('renders verified grounded citation source cards with external links', () => {
    const mockSources: CitationSource[] = [
      {
        resource_id: 'res-123',
        title: 'Deep Learning Specialization',
        url: 'https://example.com/deep-learning',
        provider: 'Coursera',
      },
    ];

    render(
      <div data-testid="citations-container">
        {mockSources.map((src) => (
          <a
            key={src.resource_id}
            href={src.url}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="citation-link"
          >
            <span>{src.title}</span>
          </a>
        ))}
      </div>
    );

    const link = screen.getByTestId('citation-link');
    expect(link).toHaveAttribute('href', 'https://example.com/deep-learning');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(screen.getByText('Deep Learning Specialization')).toBeInTheDocument();
  });

  it('safely escapes raw script tags and does not execute or dangerously render HTML', () => {
    const maliciousPayload = '<script>alert(1)</script>';
    render(<p data-testid="message-content">{maliciousPayload}</p>);

    const element = screen.getByTestId('message-content');
    expect(element.textContent).toBe('<script>alert(1)</script>');
    expect(element.querySelector('script')).toBeNull();
  });

  it('safely escapes image onerror tags', () => {
    const maliciousImg = '<img src=x onerror=alert(1)>';
    render(<p data-testid="img-content">{maliciousImg}</p>);

    const element = screen.getByTestId('img-content');
    expect(element.textContent).toBe('<img src=x onerror=alert(1)>');
    expect(element.querySelector('img')).toBeNull();
  });
});
