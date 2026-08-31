import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { App } from '../App';

describe('Routing and Navigation Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders landing page on root route /', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText(/Autonomous Career Navigation Engine/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Start Free Assessment/i })).toBeInTheDocument();
  });

  it('redirects unauthenticated users attempting to access /dashboard to /login', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Welcome back/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });

  it('redirects unauthenticated users attempting to access /roadmap to /login', () => {
    render(
      <MemoryRouter initialEntries={['/roadmap']}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Welcome back/i })).toBeInTheDocument();
  });

  it('redirects unauthenticated users attempting to access /settings to /login', () => {
    render(
      <MemoryRouter initialEntries={['/settings']}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Welcome back/i })).toBeInTheDocument();
  });
});
