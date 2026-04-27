import React from 'react';
import { cn } from '../../lib/utils';

export const Input = React.forwardRef(
  ({ className, type = 'text', label, error, icon: Icon, helperText, ...props }, ref) => {
    const id = props.id || props.name || Math.random().toString(36).slice(2);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="mb-1.5 block text-sm font-medium text-gray-300"
          >
            {label}
            {props.required && <span className="ml-0.5 text-red-500">*</span>}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <Icon className="h-4 w-4 text-gray-500" />
            </div>
          )}
          <input
            id={id}
            type={type}
            ref={ref}
            className={cn(
              'flex w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-white shadow-sm transition-all duration-200',
              'placeholder:text-gray-500',
              'focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500',
              'disabled:cursor-not-allowed disabled:bg-gray-900 disabled:text-gray-500',
              Icon && 'pl-10',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 text-xs font-medium text-red-400">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-xs text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

