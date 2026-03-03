/**
 * Tooltip Component
 *
 * Accessible hover/focus tooltip for displaying technical descriptions.
 * Renders a dark bubble with an arrow pointer in the specified direction.
 */

import React, { useState } from 'react'

interface TooltipProps {
  /** Tooltip body text — keep concise but informative */
  content: string
  children: React.ReactNode
  /** Preferred placement relative to the trigger element */
  position?: 'top' | 'bottom' | 'left' | 'right'
  /** Tailwind max-width class, e.g. "max-w-xs" or "max-w-sm" */
  maxWidth?: string
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  maxWidth = 'max-w-xs',
}) => {
  const [visible, setVisible] = useState(false)

  const positionClasses: Record<string, string> = {
    top: 'bottom-full mb-2 left-1/2 -translate-x-1/2',
    bottom: 'top-full mt-2 left-1/2 -translate-x-1/2',
    left: 'right-full mr-2 top-1/2 -translate-y-1/2',
    right: 'left-full ml-2 top-1/2 -translate-y-1/2',
  }

  const arrowClasses: Record<string, string> = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 border-l-transparent border-r-transparent border-b-transparent',
    bottom:
      'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 border-l-transparent border-r-transparent border-t-transparent',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 border-t-transparent border-b-transparent border-r-transparent',
    right:
      'right-full top-1/2 -translate-y-1/2 border-r-gray-900 border-t-transparent border-b-transparent border-l-transparent',
  }

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div
          role="tooltip"
          className={`absolute z-50 pointer-events-none ${positionClasses[position]}`}
        >
          <div
            className={`px-3 py-2 text-xs text-white bg-gray-900 rounded-lg shadow-xl ${maxWidth} whitespace-normal leading-relaxed`}
          >
            {content}
          </div>
          <div className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`} />
        </div>
      )}
    </div>
  )
}
