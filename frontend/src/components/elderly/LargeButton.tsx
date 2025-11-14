import React from 'react'
import clsx from 'clsx'

type Variant = 'primary' | 'secondary'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-blue-700 hover:bg-blue-800 text-white focus:ring-blue-300 border-2 border-blue-900',
  secondary:
    'bg-white text-blue-900 border-2 border-blue-200 hover:bg-blue-50 focus:ring-blue-200',
}

export const LargeButton: React.FC<Props> = ({ variant = 'primary', className, children, type = 'button', ...rest }) => {
  return (
    <button
      type={type}
      className={clsx(
        'w-full min-h-[3.25rem] rounded-xl text-lg font-semibold tracking-wide transition-colors focus:outline-none focus:ring-4',
        variantClasses[variant],
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  )
}
