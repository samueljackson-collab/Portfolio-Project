import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center px-6 py-3 rounded-lg font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900';

  const variantStyles = {
    primary: 'bg-cyan-600 hover:bg-cyan-500 text-white focus:ring-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed disabled:opacity-50',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-white focus:ring-gray-500 disabled:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50',
    danger: 'bg-red-600 hover:bg-red-500 text-white focus:ring-red-500 disabled:bg-gray-600 disabled:cursor-not-allowed disabled:opacity-50',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
