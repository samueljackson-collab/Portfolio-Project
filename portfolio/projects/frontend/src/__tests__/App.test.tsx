import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';
import * as client from '../api/client';

vi.mock('../api/client');

const mockedClient = vi.mocked(client);

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedClient.fetchProjects.mockResolvedValue([
      {
        id: 'proj-123',
        name: 'Sample Project',
        description: 'A sample project',
        tags: ['fastapi'],
        url: 'https://example.com',
      },
    ]);
    mockedClient.fetchHealth.mockResolvedValue({ status: 'ok', environment: 'test' });
  });

  it('renders project cards after loading data', async () => {
    render(<App />);

    expect(await screen.findByText('Sample Project')).toBeInTheDocument();
    expect(screen.getByText(/Backend status/)).toBeInTheDocument();
  });
});
