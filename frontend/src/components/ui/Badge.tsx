import React, { HTMLAttributes } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'teal' | 'blue' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  hasDot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  hasDot = false,
  className = '',
  ...props
}) => {
  const variantStyles = {
    teal: 'bg-tealAccent-light text-tealAccent border-tealAccent-border',
    blue: 'bg-blueAccent-light text-blueAccent border-blueAccent-border',
    success: 'bg-status-success-bg text-status-success border-status-success-border',
    warning: 'bg-status-warning-bg text-status-warning border-status-warning-border',
    danger: 'bg-status-danger-bg text-status-danger border-status-danger-border',
    info: 'bg-status-info-bg text-status-info border-status-info-border',
    neutral: 'bg-surface-subdued text-navy-secondary border-border-subtle',
  };

  const dotStyles = {
    teal: 'bg-tealAccent',
    blue: 'bg-blueAccent',
    success: 'bg-status-success',
    warning: 'bg-status-warning',
    danger: 'bg-status-danger',
    info: 'bg-status-info',
    neutral: 'bg-navy-muted',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-pill border ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {hasDot && <span className={`w-1.5 h-1.5 rounded-full ${dotStyles[variant]}`} />}
      {children}
    </span>
  );
};

export default Badge;
