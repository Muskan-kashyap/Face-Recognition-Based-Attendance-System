import React from 'react';
import { cn, getInitials, stringToColor } from '../../lib/utils';

export const Avatar = React.forwardRef(({ src, name, size = 'md', className, ...props }, ref) => {
  const sizeClasses = {
    xs: 'h-6 w-6 text-[10px]',
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg',
  };

  const initials = getInitials(name);
  const bgColor = stringToColor(name);

  return (
    <div
      ref={ref}
      className={cn(
        'relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full font-medium text-white',
        sizeClasses[size],
        className
      )}
      style={{ backgroundColor: !src ? bgColor : undefined }}
      {...props}
    >
      {src ? (
        <img src={src} alt={name || 'Avatar'} className="h-full w-full object-cover" />
      ) : (
        initials
      )}
    </div>
  );
});
Avatar.displayName = 'Avatar';
