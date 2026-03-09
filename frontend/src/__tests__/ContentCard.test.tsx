import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ContentCard } from '../components/ContentCard'

const mockContent = {
  id: '1',
  title: 'Test Content Title',
  body: 'This is the content body text for testing purposes.',
  is_published: true,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
  owner_id: 'user-1',
}

const mockDraftContent = {
  ...mockContent,
  id: '2',
  title: 'Draft Content',
  is_published: false,
}

describe('ContentCard', () => {
  it('renders content title', () => {
    render(<ContentCard content={mockContent} />)
    expect(screen.getByText('Test Content Title')).toBeInTheDocument()
  })

  it('renders content body', () => {
    render(<ContentCard content={mockContent} />)
    expect(screen.getByText(/This is the content body text/)).toBeInTheDocument()
  })

  it('displays Published status for published content', () => {
    render(<ContentCard content={mockContent} />)
    expect(screen.getByText('Published')).toBeInTheDocument()
  })

  it('displays Draft status for unpublished content', () => {
    render(<ContentCard content={mockDraftContent} />)
    expect(screen.getByText('Draft')).toBeInTheDocument()
  })

  it('formats the creation date correctly', () => {
    render(<ContentCard content={mockContent} />)
    expect(screen.getByText(/January 15, 2024/)).toBeInTheDocument()
  })

  it('does not show action buttons by default', () => {
    render(<ContentCard content={mockContent} />)
    expect(screen.queryByText('Edit')).not.toBeInTheDocument()
    expect(screen.queryByText('Delete')).not.toBeInTheDocument()
  })

  it('shows edit button when showActions is true and onEdit is provided', () => {
    const onEdit = vi.fn()
    render(<ContentCard content={mockContent} showActions={true} onEdit={onEdit} />)
    expect(screen.getByText('Edit')).toBeInTheDocument()
  })

  it('shows delete button when showActions is true and onDelete is provided', () => {
    const onDelete = vi.fn()
    render(<ContentCard content={mockContent} showActions={true} onDelete={onDelete} />)
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('calls onEdit with content when edit button is clicked', () => {
    const onEdit = vi.fn()
    render(<ContentCard content={mockContent} showActions={true} onEdit={onEdit} />)

    fireEvent.click(screen.getByText('Edit'))

    expect(onEdit).toHaveBeenCalledTimes(1)
    expect(onEdit).toHaveBeenCalledWith(mockContent)
  })

  it('calls onDelete with content id when delete button is clicked', () => {
    const onDelete = vi.fn()
    render(<ContentCard content={mockContent} showActions={true} onDelete={onDelete} />)

    fireEvent.click(screen.getByText('Delete'))

    expect(onDelete).toHaveBeenCalledTimes(1)
    expect(onDelete).toHaveBeenCalledWith('1')
  })

  it('handles content without body', () => {
    const contentWithoutBody = { ...mockContent, body: '' }
    render(<ContentCard content={contentWithoutBody} />)
    expect(screen.getByText('Test Content Title')).toBeInTheDocument()
  })
})
