/**
 * LargeButton - Elderly-friendly button component
 *
 * Features:
 * - Large touch target (minimum 48x48px)
 * - High contrast colors
 * - Clear text labels
 * - Icon support with text
 * - Large font size (18px+)
 */

import React from 'react'

interface LargeButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'danger' | 'success'
  size?: 'medium' | 'large'
  icon?: React.ReactNode
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  fullWidth?: boolean
  className?: string
}

export const LargeButton: React.FC<LargeButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  icon,
  disabled = false,
  type = 'button',
  fullWidth = false,
  className = '',
}) => {
  const baseClasses =
    'flex items-center justify-center gap-3 font-semibold rounded-lg ' +
    'transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-offset-2 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed active:scale-95'

  const sizeClasses = {
    medium: 'text-lg px-6 py-3 min-h-[48px]',
    large: 'text-xl px-8 py-4 min-h-[60px]',
  }

  const variantClasses = {
    primary:
      'bg-blue-900 hover:bg-blue-950 text-white focus:ring-blue-200 ' +
      'border-2 border-blue-950',
    secondary:
      'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-300 ' +
      'border-2 border-gray-400',
    danger:
      'bg-red-600 hover:bg-red-700 text-white focus:ring-red-300 ' +
      'border-2 border-red-700',
    success:
      'bg-green-600 hover:bg-green-700 text-white focus:ring-green-300 ' +
      'border-2 border-green-700',
  }

  const widthClass = fullWidth ? 'w-full' : ''

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${widthClass}
        ${className}
      `}
    >
      {icon && <span className="text-2xl">{icon}</span>}
      <span>{children}</span>
    </button>
  )
}
