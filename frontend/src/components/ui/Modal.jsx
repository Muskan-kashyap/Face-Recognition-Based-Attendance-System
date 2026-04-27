import React from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';

export const Modal = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  className,
  showClose = true
}) => {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4 sm:p-6 md:items-center">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-gray-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Content */}
      <div
        className={cn(
          'relative w-full rounded-xl bg-gray-900 shadow-xl border border-gray-800 animate-fade-in',
          className
        )}
      >
        {(title || showClose) && (
          <div className="flex items-start justify-between p-6 pb-0">
            <div className="space-y-1">
              {title && (
                <h3 className="text-lg font-semibold leading-none text-white">
                  {title}
                </h3>
              )}
              {description && (
                <p className="text-sm text-gray-400">{description}</p>
              )}
            </div>

            {showClose && (
              <button
                onClick={onClose}
                className="rounded-lg p-1 text-gray-400 hover:bg-gray-800 hover:text-white transition-colors duration-200"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        )}

        <div className="p-6">{children}</div>
      </div>
    </div>,
    document.body
  );
};

