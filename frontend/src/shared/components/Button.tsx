import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-1';
  
  const variantClasses = {
    primary: 'bg-primary-blue text-white hover:bg-primary-blue/90 focus:ring-primary-blue',
    secondary: 'bg-white text-text-primary border border-border hover:border-primary-blue hover:text-primary-blue focus:ring-primary-blue',
    ghost: 'text-text-primary hover:bg-bg-hover focus:ring-primary-blue',
    danger: 'bg-status-error text-white hover:bg-status-error/90 focus:ring-status-error',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm gap-1.5',
    md: 'px-4 py-2 text-base gap-2',
    lg: 'px-6 py-3 text-lg gap-2.5',
  };

  const isDisabled = disabled || isLoading;

  return (
    <motion.button
      whileHover={!isDisabled ? { scale: 1.02, y: -1 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      disabled={isDisabled}
      {...props}
    >
      {isLoading ? (
        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : icon ? (
        <>
          {icon}
          {children && <span>{children}</span>}
        </>
      ) : (
        children
      )}
    </motion.button>
  );
};