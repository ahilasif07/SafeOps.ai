import React, { useState } from 'react';
import { Radio, X, Plus, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Machine } from '../types';

interface MachineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess: () => void;
}

export function MachineModal({ isOpen, onClose, onSaveSuccess }: MachineModalProps) {
  const [machineCode, setMachineCode] = useState(`MCH-${Math.floor(1000 + Math.random() * 9000)}`);
  const [name, setName] = useState('');
  const [model, setModel] = useState('');
  const [location, setLocation] = useState('Sector A');
  const [status, setStatus] = useState<'OPERATIONAL' | 'MAINTENANCE' | 'HAZARDOUS' | 'OFFLINE'>('OPERATIONAL');
  const [safetyRating, setSafetyRating] = useState<number>(90);
  const [requiresLoto, setRequiresLoto] = useState<boolean>(true);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !model) {
      setErrorMsg('Please enter machine name and model number.');
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/v1/machines/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          machine_code: machineCode,
          name,
          model,
          location,
          status,
          safety_rating: Number(safetyRating),
          requires_loto: requiresLoto
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to register machine.');
      }

      onSaveSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred while creating machine.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-slate-100">Register New Industrial Machine</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Machine Code
              </label>
              <input 
                type="text" 
                value={machineCode}
                onChange={e => setMachineCode(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-amber-300 focus:outline-none focus:border-amber-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Location Sector
              </label>
              <input 
                type="text" 
                value={location}
                placeholder="e.g. Sector B - Fabrication"
                onChange={e => setLocation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Machine Name
            </label>
            <input 
              type="text" 
              placeholder="e.g. CNC Automated Milling Lathe"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Model / Serial
              </label>
              <input 
                type="text" 
                placeholder="e.g. Haas VF-4SS"
                value={model}
                onChange={e => setModel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Initial Status
              </label>
              <select 
                value={status}
                onChange={e => setStatus(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value="OPERATIONAL">OPERATIONAL</option>
                <option value="MAINTENANCE">MAINTENANCE</option>
                <option value="HAZARDOUS">HAZARDOUS</option>
                <option value="OFFLINE">OFFLINE</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Safety Rating (0 - 100)
              </label>
              <input 
                type="number" 
                min={0}
                max={100}
                value={safetyRating}
                onChange={e => setSafetyRating(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-emerald-400 font-bold focus:outline-none focus:border-amber-500"
              />
            </div>
            <div className="flex items-center pt-5">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300 font-medium">
                <input 
                  type="checkbox" 
                  checked={requiresLoto}
                  onChange={e => setRequiresLoto(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500 w-4 h-4"
                />
                <span>Mandatory LOTO Protocol</span>
              </label>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl transition flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
            >
              <Plus className="w-4 h-4 stroke-[3]" />
              <span>{isSubmitting ? 'Registering...' : 'Save Machine'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
