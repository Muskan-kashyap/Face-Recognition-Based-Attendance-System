import React, { createContext, useContext, useState } from 'react';
import { cn } from '../../lib/utils';

const TabsContext = createContext(null);

export const Tabs = ({ defaultValue, value, onValueChange, children, className }) => {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const currentValue = value !== undefined ? value : internalValue;
  const setValue = onValueChange || setInternalValue;

  return (
    <TabsContext.Provider value={{ value: currentValue, setValue }}>
      <div className={cn('w-full', className)}>{children}</div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ children, className }) => (
  <div className={cn('inline-flex h-10 items-center justify-center rounded-lg bg-gray-800 p-1', className)}>
    {children}
  </div>
);

export const TabsTrigger = ({ value, children, className }) => {
  const ctx = useContext(TabsContext);
  const isActive = ctx?.value === value;

  return (
    <button
      type="button"
      onClick={() => ctx?.setValue(value)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
        isActive
          ? 'bg-gray-700 text-white shadow-sm'
          : 'text-gray-400 hover:text-gray-200',
        className
      )}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ value, children, className }) => {
  const ctx = useContext(TabsContext);
  if (ctx?.value !== value) return null;

  return (
    <div className={cn('mt-2 focus-visible:outline-none', className)}>
      {children}
    </div>
  );
};

