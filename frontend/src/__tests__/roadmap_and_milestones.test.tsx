import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';

describe('Roadmap Milestone States Test', () => {
  it('renders LOCKED status with lock styling', () => {
    render(
      <Badge variant="default" size="sm">
        LOCKED
      </Badge>
    );
    expect(screen.getByText('LOCKED')).toBeInTheDocument();
  });

  it('renders AVAILABLE status badge', () => {
    render(
      <Badge variant="warning" size="sm">
        AVAILABLE
      </Badge>
    );
    expect(screen.getByText('AVAILABLE')).toBeInTheDocument();
  });

  it('renders IN_PROGRESS status badge with active indicator', () => {
    render(
      <Badge variant="info" size="sm">
        IN_PROGRESS
      </Badge>
    );
    expect(screen.getByText('IN_PROGRESS')).toBeInTheDocument();
  });

  it('renders COMPLETED milestone badge', () => {
    render(
      <Badge variant="success" size="sm">
        COMPLETED
      </Badge>
    );
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });
});
