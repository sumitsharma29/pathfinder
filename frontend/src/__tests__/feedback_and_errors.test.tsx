import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoadingSpinner, EmptyState, ErrorMessage } from '../components/common/FeedbackStates';

describe('Feedback, Loading and Error States Tests', () => {
  it('renders LoadingSpinner with custom message', () => {
    render(<LoadingSpinner message="Assembling real-time learning metrics..." />);
    expect(screen.getByText('Assembling real-time learning metrics...')).toBeInTheDocument();
  });

  it('renders EmptyState with title, description and call-to-action', () => {
    render(
      <EmptyState
        title="No Resources Matched"
        description="Try broadening your search query."
        action={<button>Reset Filters</button>}
      />
    );

    expect(screen.getByText('No Resources Matched')).toBeInTheDocument();
    expect(screen.getByText('Try broadening your search query.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reset filters/i })).toBeInTheDocument();
  });

  it('renders ErrorMessage with retry button and triggers callback', () => {
    const handleRetry = vi.fn();
    render(
      <ErrorMessage
        title="Network Failure"
        message="Unable to reach API server"
        onRetry={handleRetry}
      />
    );

    expect(screen.getByText('Network Failure')).toBeInTheDocument();
    expect(screen.getByText('Unable to reach API server')).toBeInTheDocument();

    const retryBtn = screen.getByRole('button', { name: /retry/i });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});
