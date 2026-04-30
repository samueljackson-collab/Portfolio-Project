import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

import '@testing-library/jest-dom/vitest';

describe('App', () => {
  it('renders login screen', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText(/Sign in/i)).toBeInTheDocument();
  });
});
