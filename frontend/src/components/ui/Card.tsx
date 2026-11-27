import React, { HTMLAttributes, forwardRef } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  elevation?: 'flat' | 'card' | 'hover';
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, elevation = 'card', className = '', ...props }, ref) => {
    const elevationStyles = {
      flat: 'border border-border-subtle shadow-none',
      card: 'border border-border-subtle shadow-card',
      hover: 'border border-border-subtle shadow-card hover:shadow-card-hover transition-shadow',
    };

    return (
      <div
        ref={ref}
        className={`bg-surface rounded-card p-6 ${elevationStyles[elevation]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';

export const CardHeader: React.FC<HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={`space-y-1.5 mb-4 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <h3 className={`text-base font-bold text-navy tracking-tight ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<HTMLAttributes<HTMLParagraphElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <p className={`text-xs text-navy-muted leading-relaxed ${className}`} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={className} {...props}>
    {children}
  </div>
);

export default Card;
