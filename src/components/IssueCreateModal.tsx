import React, { useState, useEffect } from 'react';
import { Bug, X, Plus, AlertTriangle, Cog as MachineIcon, User, Calendar, Building2, Search, ArrowRight, ShieldAlert, Cpu } from 'lucide-react';
import { Machine, Worker } from '../types';

interface DuplicateMatch {
  issue_id: number;
  issue_code: string;
  title: string;
  description: string;
  machine_id?: number;
  machine_name?: string;
  status: string;
  priority: string;
  created_at: string;
  similarity_score: number;
  similarity_percentage: number;
}

interface DuplicateCheckResult {
  is_possible_duplicate: boolean;
  threshold_used: number;
  existing_issue_id?: number;
  existing_issue_code?: string;
  similarity_score: number;
  similarity_percentage: number;
  top_match?: DuplicateMatch;
  all_matches: DuplicateMatch[];
}

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

  // Duplicate Detector State
  const [threshold, setThreshold] = useState<number>(0.55);
  const [duplicateResult, setDuplicateResult] = useState<DuplicateCheckResult | null>(null);
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false);
  const [bypassWarning, setBypassWarning] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Debounced live duplicate detection engine call
  useEffect(() => {
    if (!title.trim() || title.length < 3) {
      setDuplicateResult(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsCheckingDuplicates(true);
      try {
        const res = await fetch('/api/v1/issues/check-duplicates', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            description,
            machine_id: machineId ? Number(machineId) : undefined,
            threshold
          })
        });
        if (res.ok) {
          const data: DuplicateCheckResult = await res.json();
          setDuplicateResult(data);
        }
      } catch (err) {
        console.error('Error running duplicate detection engine:', err);
      } finally {
        setIsCheckingDuplicates(false);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [title, description, machineId, threshold]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) {
      setErrorMsg('Please enter an issue title and description.');
      return;
    }

    // If duplicate detected and worker hasn't explicitly acknowledged/bypassed, ask for confirmation
    if (duplicateResult?.is_possible_duplicate && !bypassWarning) {
      setBypassWarning(true);
      setErrorMsg('Possible duplicate detected! Please review the warning above and click "Create Issue" again to proceed.');
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

          {/* Live Duplicate Detection Engine Card */}
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-slate-200">Duplicate Detection Engine</span>
                <span className="text-[10px] text-slate-500 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                  Fuzzy String Matching (Vector Search Ready)
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[10px] text-slate-400">Threshold:</span>
                <input 
                  type="range" 
                  min="0.30" 
                  max="0.90" 
                  step="0.05"
                  value={threshold}
                  onChange={e => setThreshold(parseFloat(e.target.value))}
                  className="w-20 accent-amber-500 cursor-pointer"
                />
                <span className="text-amber-400 font-mono font-bold text-xs">{Math.round(threshold * 100)}%</span>
              </div>
            </div>

            {isCheckingDuplicates ? (
              <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl text-xs text-slate-400 flex items-center gap-2">
                <Search className="w-4 h-4 text-amber-400 animate-spin" />
                <span>Running fuzzy string & machine similarity scan against open issues...</span>
              </div>
            ) : duplicateResult?.is_possible_duplicate ? (
              <div className="p-3.5 bg-amber-500/10 border border-amber-500/40 rounded-xl space-y-2.5 animate-in fade-in">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-xs text-amber-300">
                    <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>Possible Duplicate Issue Detected!</span>
                  </div>
                  <span className="text-[11px] font-mono font-bold text-amber-400 bg-amber-500/20 px-2.5 py-0.5 rounded-full border border-amber-500/30">
                    Similarity Score: {duplicateResult.similarity_percentage}%
                  </span>
                </div>

                <div className="p-3 bg-slate-950/90 border border-slate-800 rounded-xl space-y-1.5 text-xs text-slate-300">
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="text-amber-400 font-bold">Existing Issue ID: #{duplicateResult.existing_issue_id} ({duplicateResult.existing_issue_code})</span>
                    <span className="text-slate-400">{duplicateResult.top_match?.machine_name}</span>
                  </div>
                  <p className="font-bold text-slate-100">{duplicateResult.top_match?.title}</p>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{duplicateResult.top_match?.description}</p>
                  <div className="pt-1 flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-800/60">
                    <span>Status: <strong className="text-amber-300">{duplicateResult.top_match?.status}</strong></span>
                    <span>Logged: {duplicateResult.top_match?.created_at ? new Date(duplicateResult.top_match.created_at).toLocaleDateString() : 'Recent'}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-2 pt-1">
                  <span className="text-[11px] text-slate-400 italic">
                    Note: System warns but does not reject. You can continue if this is distinct.
                  </span>
                  <button
                    type="button"
                    onClick={() => setBypassWarning(true)}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                      bypassWarning 
                        ? 'bg-emerald-500 text-slate-950 border border-emerald-400' 
                        : 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {bypassWarning ? '✓ Warning Acknowledged' : 'Acknowledge & Continue'}
                  </button>
                </div>
              </div>
            ) : title.trim().length >= 3 ? (
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>No duplicate issues detected above {Math.round(threshold * 100)}% similarity threshold.</span>
              </div>
            ) : null}
          </div>

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
