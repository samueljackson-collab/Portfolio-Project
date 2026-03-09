import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import App from '../src/App'

global.fetch = () => Promise.resolve({ json: () => Promise.resolve([]) })

jest.mock('axios', () => ({
  create: () => ({
    post: jest.fn(() => Promise.resolve({ data: { access_token: 'token', id: 1 } })),
    get: jest.fn(() => Promise.resolve({ data: [] }))
  })
}))

describe('App', () => {
  it('renders authentication form by default', () => {
    render(<App />)
    expect(screen.getByText(/Authenticate/)).toBeInTheDocument()
  })

  it('allows filling login form', () => {
    render(<App />)
    const userInput = screen.getByLabelText(/Username/)
    fireEvent.change(userInput, { target: { value: 'tester' } })
    expect(userInput.value).toBe('tester')
  })
})
