import { InputHTMLAttributes, forwardRef, ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
  leftIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, helperText, error, leftIcon, className = '', id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="space-y-1 w-full text-left">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold text-navy">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3 text-navy-muted pointer-events-none flex items-center">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={`w-full py-2 ${
              leftIcon ? 'pl-9' : 'pl-3'
            } pr-3 rounded-standard bg-canvas border ${
              error ? 'border-status-danger focus:border-status-danger' : 'border-border-default focus:border-border-focus'
            } text-xs text-navy placeholder:text-navy-muted focus:outline-none transition shadow-subtle ${className}`}
            {...props}
          />
        </div>
        {error ? (
          <p className="text-[11px] text-status-danger font-medium">{error}</p>
        ) : helperText ? (
          <p className="text-[11px] text-navy-muted">{helperText}</p>
        ) : null}
      </div>
    );
  }
);
Input.displayName = 'Input';
export default Input;
