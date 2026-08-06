import React, { useState, useEffect } from 'react';
import { User, X, Plus, AlertTriangle, ShieldCheck, Building2, Briefcase } from 'lucide-react';
import { Department, Role } from '../types';

interface WorkerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess: () => void;
}

export function WorkerModal({ isOpen, onClose, onSaveSuccess }: WorkerModalProps) {
  const [workerCode, setWorkerCode] = useState(`WRK-${Math.floor(1000 + Math.random() * 9000)}`);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('ELECTRICAL');
  const [role, setRole] = useState('TECHNICIAN');
  const [clearanceLevel, setClearanceLevel] = useState<number>(1);
  const [password, setPassword] = useState('SafeOpsPass2026!');
  
  const [departmentsList, setDepartmentsList] = useState<Department[]>([]);
  const [rolesList, setRolesList] = useState<Role[]>([]);
  const [customDepartment, setCustomDepartment] = useState('');
  const [customRole, setCustomRole] = useState('');
  const [isCustomDept, setIsCustomDept] = useState(false);
  const [isCustomRole, setIsCustomRole] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchDepartmentsAndRoles();
    }
  }, [isOpen]);

  const fetchDepartmentsAndRoles = async () => {
    try {
      const [deptRes, roleRes] = await Promise.all([
        fetch('/api/v1/departments/').then(r => r.json()),
        fetch('/api/v1/roles/').then(r => r.json())
      ]);
      if (Array.isArray(deptRes) && deptRes.length > 0) setDepartmentsList(deptRes);
      if (Array.isArray(roleRes) && roleRes.length > 0) setRolesList(roleRes);
    } catch (err) {
      console.error('Error loading departments and roles:', err);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email) {
      setErrorMsg('Please enter worker full name and email.');
      return;
    }

    const finalDepartment = isCustomDept ? customDepartment.trim().toUpperCase().replace(/\s+/g, '_') : department;
    const finalRole = isCustomRole ? customRole.trim() : role;

    if (!finalDepartment || !finalRole) {
      setErrorMsg('Please specify department and role.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      // Create custom department on server if new
      if (isCustomDept && customDepartment.trim()) {
        await fetch('/api/v1/departments/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: finalDepartment, code: finalDepartment.slice(0, 4) })
        });
      }

      // Create custom role on server if new
      if (isCustomRole && customRole.trim()) {
        await fetch('/api/v1/roles/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: finalRole, department: finalDepartment, clearance_level: clearanceLevel })
        });
      }

      const res = await fetch('/api/v1/workers/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          worker_code: workerCode,
          full_name: fullName,
          email,
          department: finalDepartment,
          role: finalRole,
          clearance_level: Number(clearanceLevel),
          password,
          is_active: true
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create worker profile.');
      }

      onSaveSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred while creating worker.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const defaultDepts = ['ELECTRICAL', 'MECHANICAL', 'PLANT_OPS', 'SAFETY_DEPT', 'CHEMICAL', 'IT_SUPPORT'];
  const allDepts = Array.from(new Set([...defaultDepts, ...departmentsList.map(d => d.name)]));

  const defaultRoles = ['TECHNICIAN', 'SUPERVISOR', 'SAFETY_OFFICER', 'Mechanical Engineer', 'Electrical Engineer', 'Plant Operator', 'Chemical Engineer', 'IT Support', 'General Worker'];
  const allRoles = Array.from(new Set([...defaultRoles, ...rolesList.map(r => r.name)]));

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-slate-100">Add New Worker / Technician Profile</h2>
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
                Worker Code
              </label>
              <input 
                type="text" 
                value={workerCode}
                onChange={e => setWorkerCode(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-amber-300 focus:outline-none focus:border-amber-500"
                required
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Department
                </label>
                <button
                  type="button"
                  onClick={() => setIsCustomDept(!isCustomDept)}
                  className="text-[10px] text-amber-400 hover:underline"
                >
                  {isCustomDept ? 'Select Existing' : '+ Custom Dept'}
                </button>
              </div>
              {isCustomDept ? (
                <input
                  type="text"
                  placeholder="CUSTOM_DEPT_NAME"
                  value={customDepartment}
                  onChange={e => setCustomDepartment(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  required
                />
              ) : (
                <select 
                  value={department}
                  onChange={e => setDepartment(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  {allDepts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Full Name
            </label>
            <input 
              type="text" 
              placeholder="e.g. Marcus Vance"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <input 
              type="email" 
              placeholder="marcus.vance@safeops.io"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Role
                </label>
                <button
                  type="button"
                  onClick={() => setIsCustomRole(!isCustomRole)}
                  className="text-[10px] text-amber-400 hover:underline"
                >
                  {isCustomRole ? 'Select Existing' : '+ Custom Role'}
                </button>
              </div>
              {isCustomRole ? (
                <input
                  type="text"
                  placeholder="Custom Role Title"
                  value={customRole}
                  onChange={e => setCustomRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  required
                />
              ) : (
                <select 
                  value={role}
                  onChange={e => setRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  {allRoles.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              )}
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Clearance Level (1 - 5)
              </label>
              <input 
                type="number" 
                min={1}
                max={5}
                value={clearanceLevel}
                onChange={e => setClearanceLevel(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-bold text-amber-300 focus:outline-none focus:border-amber-500"
              />
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
              <span>{isSubmitting ? 'Saving...' : 'Create Worker'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
