import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hoverable = false,
  onClick,
}) => {
  const Component = hoverable ? motion.div : 'div';
  
  return (
    <Component
      whileHover={hoverable ? { y: -4 } : {}}
      onClick={onClick}
      className={`
        card-base p-6
        ${hoverable ? 'cursor-pointer card-hover' : ''}
        ${className}
      `}
    >
      {children}
    </Component>
  );
};