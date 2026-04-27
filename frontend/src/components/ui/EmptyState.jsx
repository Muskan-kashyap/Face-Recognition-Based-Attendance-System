import React from 'react';
import { Inbox } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon = Inbox,
  title = 'No data found',
  description = 'There are no items to display at the moment.',
  actionText,
  onAction,
  className,
}) => (
  <div
    className={cn(
      'flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-700 bg-gray-900/50 p-12 text-center',
      className
    )}
  >
    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-800">
      <Icon className="h-6 w-6 text-gray-500" />
    </div>
    <h3 className="text-base font-semibold text-white">{title}</h3>
    <p className="mt-1 max-w-xs text-sm text-gray-400">{description}</p>
    {actionText && onAction && (
      <Button variant="primary" size="sm" className="mt-4" onClick={onAction}>
        {actionText}
      </Button>
    )}
  </div>
);

