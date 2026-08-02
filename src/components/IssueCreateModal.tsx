import React, { useState } from 'react';
import { Bug, X, Plus, AlertTriangle, Cog as MachineIcon, User, Calendar, Building2 } from 'lucide-react';
import { Machine, Worker } from '../types';

interface IssueCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess: () => void;
  machines: Machine[];
  workers: Worker[];
  currentWorkerId?: number;
}

export function IssueCreateModal({
  isOpen,
  onClose,
  onSaveSuccess,
  machines,
  workers,
  currentWorkerId
}: IssueCreateModalProps) {
  const [issueCode, setIssueCode] = useState(`ISS-${Math.floor(1000 + Math.random() * 9000)}`);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [machineId, setMachineId] = useState<number | undefined>(machines[0]?.id);
  const [department, setDepartment] = useState('PLANT_OPS');
  const [priority, setPriority] = useState<'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'>('MEDIUM');
  const [status, setStatus] = useState<'Open' | 'In Progress' | 'Waiting' | 'Resolved' | 'Closed'>('Open');
  const [reporterId, setReporterId] = useState<number | undefined>(currentWorkerId || workers[0]?.id);
  const [assignedWorkerId, setAssignedWorkerId] = useState<number | undefined>(workers[0]?.id);
  const [assignedSupervisorId, setAssignedSupervisorId] = useState<number | undefined>(
    workers.find(w => w.role === 'SUPERVISOR')?.id || workers[0]?.id
  );
  const [dueDate, setDueDate] = useState<string>('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) {
      setErrorMsg('Please enter an issue title and description.');
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/v1/issues/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          issue_code: issueCode,
          title,
          description,
          machine_id: machineId ? Number(machineId) : undefined,
          department,
          priority,
          status,
          reporter_id: reporterId ? Number(reporterId) : undefined,
          assigned_worker_id: assignedWorkerId ? Number(assignedWorkerId) : undefined,
          assigned_supervisor_id: assignedSupervisorId ? Number(assignedSupervisorId) : undefined,
          due_date: dueDate ? new Date(dueDate).toISOString() : undefined
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create issue.');
      }

      onSaveSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred while creating issue.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <Bug className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-slate-100">Log Industrial Issue</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Issue Code
              </label>
              <input 
                type="text" 
                value={issueCode}
                onChange={e => setIssueCode(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-amber-300 focus:outline-none focus:border-amber-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Department
              </label>
              <select 
                value={department}
                onChange={e => setDepartment(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value="PLANT_OPS">PLANT_OPS</option>
                <option value="ELECTRICAL">ELECTRICAL</option>
                <option value="MECHANICAL">MECHANICAL</option>
                <option value="SAFETY_DEPT">SAFETY_DEPT</option>
                <option value="CHEMICAL">CHEMICAL</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Issue Title
            </label>
            <input 
              type="text" 
              placeholder="e.g. Hydraulic pressure dropping below 500 PSI on Press 4"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Description & Observed Faults
            </label>
            <textarea 
              rows={3}
              placeholder="Describe symptoms, safety hazards, equipment behavior, or error codes..."
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 resize-none"
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Machine
              </label>
              <select 
                value={machineId || ''}
                onChange={e => setMachineId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 truncate"
              >
                <option value="">None / Facility General</option>
                {machines.map(m => (
                  <option key={m.id} value={m.id}>{m.name} ({m.machine_code})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Priority
              </label>
              <select 
                value={priority}
                onChange={e => setPriority(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
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
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Waiting">Waiting</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Reporter
              </label>
              <select 
                value={reporterId || ''}
                onChange={e => setReporterId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 truncate"
              >
                {workers.map(w => (
                  <option key={w.id} value={w.id}>{w.full_name} ({w.role})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Assigned Worker
              </label>
              <select 
                value={assignedWorkerId || ''}
                onChange={e => setAssignedWorkerId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 truncate"
              >
                <option value="">Unassigned</option>
                {workers.map(w => (
                  <option key={w.id} value={w.id}>{w.full_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Assigned Supervisor
              </label>
              <select 
                value={assignedSupervisorId || ''}
                onChange={e => setAssignedSupervisorId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 truncate"
              >
                <option value="">None</option>
                {workers.filter(w => w.role === 'SUPERVISOR' || w.role === 'SAFETY_OFFICER').map(w => (
                  <option key={w.id} value={w.id}>{w.full_name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Target Resolution Due Date
            </label>
            <input 
              type="date" 
              value={dueDate}
              onChange={e => setDueDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end gap-3 shrink-0">
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
              <span>{isSubmitting ? 'Logging...' : 'Create Issue'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
