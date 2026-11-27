import { ButtonHTMLAttributes, forwardRef } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold rounded-standard transition focus:outline-none focus:ring-2 focus:ring-tealAccent/20 disabled:opacity-50 disabled:cursor-not-allowed shadow-subtle';

    const variantStyles = {
      primary: 'bg-tealAccent text-white hover:bg-tealAccent-hover',
      secondary: 'bg-blueAccent text-white hover:bg-blueAccent-hover',
      outline:
        'bg-surface border border-border-default text-navy hover:bg-surface-subdued',
      ghost: 'bg-transparent text-navy hover:bg-surface-subdued shadow-none',
      danger: 'bg-status-danger text-white hover:bg-red-700',
    };

    const sizeStyles = {
      sm: 'px-2.5 py-1 text-xs',
      md: 'px-3.5 py-2 text-xs',
      lg: 'px-4 py-2.5 text-sm',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <span className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span>Loading...</span>
          </span>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
