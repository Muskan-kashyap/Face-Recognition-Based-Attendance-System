import React from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export const Select = React.forwardRef(
  ({ label, error, className, options = [], placeholder, ...props }, ref) => {
    const id = props.id || props.name || Math.random().toString(36).slice(2);

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-gray-300">
            {label}
            {props.required && <span className="ml-0.5 text-red-500">*</span>}
          </label>
        )}
        <div className="relative">
          <select
            id={id}
            ref={ref}
            className={cn(
              'flex w-full appearance-none rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 pr-10 text-sm text-white shadow-sm transition-all duration-200',
              'focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500',
              'disabled:cursor-not-allowed disabled:bg-gray-900 disabled:text-gray-500',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
        </div>
        {error && <p className="mt-1.5 text-xs font-medium text-red-400">{error}</p>}
      </div>
    );
  }
);
Select.displayName = 'Select';

