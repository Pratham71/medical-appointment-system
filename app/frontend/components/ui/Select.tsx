"use client";
import { type SelectHTMLAttributes, forwardRef } from "react";

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {
  wrapperClassName?: string;
}

const Select = forwardRef<HTMLSelectElement, Props>(
  ({ wrapperClassName = "", className = "", children, ...props }, ref) => (
    <div className={`relative ${wrapperClassName}`}>
      <select
        ref={ref}
        {...props}
        className={`w-full appearance-none bg-white border border-brand-border rounded-btn px-3 py-2.5 pr-8 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-1 transition cursor-pointer hover:border-teal-400 ${className}`}
      >
        {children}
      </select>
      <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2.5 text-brand-muted">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </span>
    </div>
  )
);

Select.displayName = "Select";
export default Select;
