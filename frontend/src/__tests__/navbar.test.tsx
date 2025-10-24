import { describe, expect, it } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { render, screen } from '@testing-library/react'
import Navbar from '../components/Navbar'
import { AuthProvider } from '../context/AuthContext'

describe('Navbar', () => {
  it('renders navigation links', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <Navbar />
        </AuthProvider>
      </MemoryRouter>
    )

    expect(screen.getByText(/Portfolio Platform/)).toBeInTheDocument()
    expect(screen.getByText(/Home/)).toBeInTheDocument()
  })
})
