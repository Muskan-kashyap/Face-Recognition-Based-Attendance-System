import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines clsx and tailwind-merge for clean conditional class names.
 * @param {...(string|object|boolean)} inputs
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date to a readable string.
 * @param {string|Date} date
 * @param {object} options
 * @returns {string}
 */
export function formatDate(date, options = {}) {
  if (!date) return 'N/A';
  const d = new Date(date);
  if (isNaN(d.getTime())) return 'Invalid date';
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    ...options,
  });
}

/**
 * Format a time string.
 * @param {string|Date} date
 * @returns {string}
 */
export function formatTime(date) {
  if (!date) return 'N/A';
  const d = new Date(date);
  if (isNaN(d.getTime())) return 'Invalid time';
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format currency in USD.
 * @param {number} amount
 * @returns {string}
 */
export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '$0';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a number with commas.
 * @param {number} num
 * @returns {string}
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0';
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Truncate text with ellipsis.
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 50) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Capitalize first letter of each word.
 * @param {string} str
 * @returns {string}
 */
export function titleCase(str) {
  if (!str) return '';
  return str
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

/**
 * Debounce function.
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Get initials from a full name.
 * @param {string} name
 * @returns {string}
 */
export function getInitials(name) {
  if (!name) return '?';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Generate a random color from a name (for avatar backgrounds).
 * @param {string} name
 * @returns {string}
 */
export function stringToColor(name) {
  if (!name) return '#6366f1';
  const colors = [
    '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
    '#06b6d4', '#10b981', '#f59e0b', '#ef4444',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

