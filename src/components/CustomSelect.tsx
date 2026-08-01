import React from 'react';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
  value: number | string;
  label: string;
  sublabel?: string;
  badge?: string;
}

interface CustomSelectProps {
  options: SelectOption[];
  value: number | string;
  onChange: (value: any) => void;
  placeholder?: string;
  className?: string;
  icon?: React.ReactNode;
}

export function CustomSelect({
  options,
  value,
  onChange,
  placeholder = "Select option...",
  className = "",
  icon
}: CustomSelectProps) {
  const selectedOption = options.find(o => String(o.value) === String(value)) || options[0];

  return (
    <div className={`relative w-full ${className}`}>
      <div className="relative flex items-center">
        {icon && (
          <div className="absolute left-3 z-10 pointer-events-none flex items-center justify-center">
            {icon}
          </div>
        )}
        <select
          value={value !== undefined && value !== null ? value : ''}
          onChange={(e) => {
            const raw = e.target.value;
            const matched = options.find(o => String(o.value) === raw);
            if (matched) {
              onChange(matched.value);
            } else {
              onChange(raw);
            }
          }}
          className={`w-full bg-slate-950 border border-slate-700 hover:border-amber-500/50 text-amber-300 font-bold rounded-xl ${
            icon ? 'pl-9' : 'pl-3.5'
          } pr-9 py-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 cursor-pointer appearance-none truncate shadow-sm transition-all`}
        >
          {options.length === 0 ? (
            <option value="" disabled className="bg-slate-900 text-slate-400">
              {placeholder}
            </option>
          ) : (
            options.map((opt) => (
              <option 
                key={opt.value} 
                value={opt.value} 
                className="bg-slate-900 text-slate-100 py-2 font-medium"
              >
                {opt.label} {opt.badge ? `[${opt.badge}]` : ''} {opt.sublabel ? `— ${opt.sublabel}` : ''}
              </option>
            ))
          )}
        </select>
        <ChevronDown className="w-4 h-4 text-amber-400 absolute right-3 pointer-events-none stroke-[2.5]" />
      </div>
      {selectedOption?.sublabel && (
        <p className="text-[10px] text-slate-400 mt-1 pl-1 truncate">
          {selectedOption.sublabel} {selectedOption.badge ? `(${selectedOption.badge})` : ''}
        </p>
      )}
    </div>
  );
}

