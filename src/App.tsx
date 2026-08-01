import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  FileText, 
  Wrench, 
  Users, 
  CheckSquare, 
  AlertTriangle, 
  Cpu, 
  Search, 
  Play, 
  Lock, 
  Unlock, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Sparkles, 
  Plus, 
  ChevronRight,
  ShieldCheck,
  Zap,
  HardHat,
  Thermometer,
  Gauge,
  Radio,
  UserCheck,
  Award,
  Edit3,
  Eye,
  Upload
} from 'lucide-react';
import { Worker, Machine, Procedure, Task, Incident, SupervisorApproval, SensorReading, SafetyEvalResponse } from './types';
import { CustomSelect } from './components/CustomSelect';
import { SopModal } from './components/SopModal';
import { SopDetailModal } from './components/SopDetailModal';

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'machines' | 'sops' | 'workers' | 'approvals' | 'incidents'>('overview');
  
  // App State from API
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [approvals, setApprovals] = useState<SupervisorApproval[]>([]);
  const [selectedWorkerId, setSelectedWorkerId] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  
  // SOP Modals State
  const [showSopModal, setShowSopModal] = useState(false);
  const [sopToEdit, setSopToEdit] = useState<Procedure | null>(null);
  const [sopToView, setSopToView] = useState<Procedure | null>(null);
  
  // AI SOP Search
  const [searchQuery, setSearchQuery] = useState('');
  const [sopSearchResults, setSopSearchResults] = useState<any[]>([]);
  const [searchingSop, setSearchingSop] = useState(false);

  // Safety Evaluation Modal State
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskMachineId, setNewTaskMachineId] = useState<number>(1);
  const [newTaskProcedureId, setNewTaskProcedureId] = useState<number>(1);
  const [evalResult, setEvalResult] = useState<SafetyEvalResponse | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  
  // Active Telemetry State
  const [activeMachineTelemetry, setActiveMachineTelemetry] = useState<Record<number, SensorReading[]>>({});
  const [simulating, setSimulating] = useState<number | null>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [wRes, mRes, pRes, tRes, iRes, aRes] = await Promise.all([
        fetch('/api/v1/workers/').then(r => r.json()),
        fetch('/api/v1/machines/').then(r => r.json()),
        fetch('/api/v1/procedures/').then(r => r.json()),
        fetch('/api/v1/tasks/').then(r => r.json()),
        fetch('/api/v1/incidents/').then(r => r.json()),
        fetch('/api/v1/approvals/').then(r => r.json())
      ]);

      setWorkers(Array.isArray(wRes) ? wRes : []);
      setMachines(Array.isArray(mRes) ? mRes : []);
      setProcedures(Array.isArray(pRes) ? pRes : []);
      setTasks(Array.isArray(tRes) ? tRes : []);
      setIncidents(Array.isArray(iRes) ? iRes : []);
      setApprovals(Array.isArray(aRes) ? aRes : []);
      
      if (Array.isArray(wRes) && wRes.length > 0) {
        setSelectedWorkerId(wRes[0].id);
      }
      if (Array.isArray(mRes) && mRes.length > 0) {
        setNewTaskMachineId(mRes[0].id);
      }
      if (Array.isArray(pRes) && pRes.length > 0) {
        setNewTaskProcedureId(pRes[0].id);
      }
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  const currentWorker = workers.find(w => w.id === selectedWorkerId) || workers[0];

  const handleEvaluateTask = async () => {
    setEvaluating(true);
    setEvalResult(null);
    try {
      const res = await fetch('/api/v1/safety/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          worker_id: selectedWorkerId,
          machine_id: newTaskMachineId,
          procedure_id: newTaskProcedureId
        })
      });
      const data = await res.json();
      setEvalResult(data);
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleCreateTask = async () => {
    if (!newTaskTitle) return;
    try {
      const res = await fetch('/api/v1/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTaskTitle,
          description: newTaskDesc,
          worker_id: selectedWorkerId,
          machine_id: newTaskMachineId,
          procedure_id: newTaskProcedureId,
          priority: 'HIGH'
        })
      });
      if (res.ok) {
        setShowTaskModal(false);
        setNewTaskTitle('');
        setNewTaskDesc('');
        setEvalResult(null);
        fetchInitialData();
      }
    } catch (err) {
      console.error("Task creation failed:", err);
    }
  };

  const handleSOPSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchingSop(true);
    try {
      const res = await fetch(`/api/v1/sop-ai/search?q=${encodeURIComponent(searchQuery)}&top_k=3`);
      const data = await res.json();
      setSopSearchResults(data);
    } catch (err) {
      console.error("SOP Search failed:", err);
    } finally {
      setSearchingSop(false);
    }
  };

  const handleSimulateSensor = async (machineId: number, forceAnomaly: boolean) => {
    setSimulating(machineId);
    try {
      const res = await fetch(`/api/v1/sensors/simulate/${machineId}?force_anomaly=${forceAnomaly}`, { method: 'POST' });
      const data = await res.json();
      setActiveMachineTelemetry(prev => ({ ...prev, [machineId]: data }));
      fetchInitialData();
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimulating(null);
    }
  };

  const handleSupervisorDecision = async (approvalId: number, statusDecision: 'APPROVED' | 'REJECTED') => {
    try {
      await fetch(`/api/v1/approvals/${approvalId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: statusDecision,
          comments: `Decision made by supervisor ${currentWorker?.full_name || 'System'}`
        })
      });
      fetchInitialData();
    } catch (err) {
      console.error("Approval update failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Top Industrial Header */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="bg-amber-500 text-slate-950 p-2.5 rounded-xl font-black tracking-wider flex items-center gap-2 shadow-lg shadow-amber-500/20">
            <ShieldAlert className="w-6 h-6 stroke-[2.5]" />
            <span className="text-xl tracking-tight">SAFEOPS<span className="text-amber-300 font-medium">.AI</span></span>
          </div>
          <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-800 text-xs">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-400 font-medium uppercase tracking-wider">Plant Alpha • Sector 4 Operations</span>
          </div>
        </div>

        {/* Worker Switcher & System Indicators */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium hidden sm:inline">Active Worker:</span>
            <CustomSelect
              value={selectedWorkerId}
              onChange={(val) => setSelectedWorkerId(Number(val))}
              options={workers.map(w => ({
                value: w.id,
                label: w.full_name,
                sublabel: `${w.role} (${w.department})`,
                badge: `Clearance L${w.clearance_level}`
              }))}
              className="w-56"
              icon={<UserCheck className="w-4 h-4 text-amber-400 shrink-0" />}
            />
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-3 py-1.5 rounded-lg">
            <Cpu className="w-4 h-4" />
            <span>Risk Engine: ACTIVE</span>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <div className="flex-1 flex flex-col md:flex-row max-w-7xl w-full mx-auto p-4 md:p-6 gap-6">
        {/* Navigation Sidebar */}
        <nav className="w-full md:w-64 flex flex-row md:flex-col gap-1.5 overflow-x-auto pb-2 md:pb-0 shrink-0">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'overview' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Safety Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('tasks')}
            className={`flex items-center justify-between px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'tasks' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <Wrench className="w-4 h-4" />
              <span>Work Orders</span>
            </div>
            <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-full">{tasks.length}</span>
          </button>

          <button
            onClick={() => setActiveTab('machines')}
            className={`flex items-center justify-between px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'machines' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <Radio className="w-4 h-4" />
              <span>Machinery & IoT</span>
            </div>
            <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-full">{machines.length}</span>
          </button>

          <button
            onClick={() => setActiveTab('sops')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'sops' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>SOP Library & AI</span>
          </button>

          <button
            onClick={() => setActiveTab('workers')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'workers' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Workers & Certs</span>
          </button>

          <button
            onClick={() => setActiveTab('approvals')}
            className={`flex items-center justify-between px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'approvals' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <CheckSquare className="w-4 h-4" />
              <span>Approvals</span>
            </div>
            {approvals.filter(a => a.status === 'PENDING').length > 0 && (
              <span className="bg-amber-500 text-slate-950 font-bold text-xs px-2 py-0.5 rounded-full animate-bounce">
                {approvals.filter(a => a.status === 'PENDING').length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('incidents')}
            className={`flex items-center justify-between px-4 py-3 rounded-xl font-medium text-sm transition-all ${
              activeTab === 'incidents' ? 'bg-amber-500 text-slate-950 font-semibold shadow-lg shadow-amber-500/10' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-4 h-4" />
              <span>Incidents Log</span>
            </div>
            <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-full">{incidents.length}</span>
          </button>
        </nav>

        {/* Content Area */}
        <main className="flex-1 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 overflow-hidden">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-slate-400">
              <RefreshCw className="w-8 h-8 animate-spin text-amber-500" />
              <span>Connecting to SafeOps Industrial Safety Backend...</span>
            </div>
          ) : (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-100">Industrial Safety Command Center</h1>
                    <p className="text-slate-400 text-sm mt-1">Real-time risk scoring, LOTO compliance monitoring, and AI safety briefings.</p>
                  </div>

                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                      <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
                        <span>Active Maintenance</span>
                        <Wrench className="w-4 h-4 text-amber-400" />
                      </div>
                      <div className="mt-3 flex items-baseline justify-between">
                        <span className="text-3xl font-black text-slate-100">{tasks.length}</span>
                        <span className="text-xs text-amber-400 font-medium">{tasks.filter(t => t.is_blocked).length} Blocked</span>
                      </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                      <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
                        <span>Overall Risk Level</span>
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="mt-3 flex items-baseline justify-between">
                        <span className="text-3xl font-black text-emerald-400">LOW</span>
                        <span className="text-xs text-slate-400">Composite: 18.5 / 100</span>
                      </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                      <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
                        <span>Registered Machines</span>
                        <Radio className="w-4 h-4 text-blue-400" />
                      </div>
                      <div className="mt-3 flex items-baseline justify-between">
                        <span className="text-3xl font-black text-slate-100">{machines.length}</span>
                        <span className="text-xs text-rose-400 font-medium">{machines.filter(m => m.status === 'HAZARDOUS').length} Hazardous</span>
                      </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                      <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
                        <span>Open Incidents</span>
                        <AlertTriangle className="w-4 h-4 text-rose-400" />
                      </div>
                      <div className="mt-3 flex items-baseline justify-between">
                        <span className="text-3xl font-black text-rose-400">{incidents.length}</span>
                        <span className="text-xs text-slate-400">Sector C Active</span>
                      </div>
                    </div>
                  </div>

                  {/* AI Copilot & Risk Engine Showcase Banner */}
                  <div className="bg-gradient-to-r from-amber-500/10 via-slate-900 to-slate-900 border border-amber-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="space-y-2">
                      <div className="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 text-xs font-bold px-3 py-1 rounded-full border border-amber-500/30">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>SafeOps AI Safety Advisor</span>
                      </div>
                      <h3 className="text-lg font-bold text-slate-100">Automated LOTO & Clearance Protection Active</h3>
                      <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
                        Every work order submitted is evaluated in real-time by our deterministic Risk Engine and Gemini AI safety agent. Unqualified technicians or compromised machine telemetry automatically block task dispatch.
                      </p>
                    </div>

                    <button 
                      onClick={() => setShowTaskModal(true)}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-5 py-3 rounded-xl shadow-lg shadow-amber-500/20 flex items-center gap-2 whitespace-nowrap transition-all"
                    >
                      <Plus className="w-5 h-5 stroke-[3]" />
                      <span>Evaluate & Create Task</span>
                    </button>
                  </div>

                  {/* Machine Telemetry Grid Overview */}
                  <div className="space-y-4">
                    <h3 className="text-md font-bold text-slate-200 flex items-center gap-2">
                      <Radio className="w-5 h-5 text-amber-400" />
                      <span>Live IoT Machine Status & Anomaly Monitors</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {machines.map(m => (
                        <div key={m.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-mono text-amber-400 font-bold">{m.machine_code}</span>
                            <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                              m.status === 'OPERATIONAL' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                              m.status === 'MAINTENANCE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                              'bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse'
                            }`}>
                              {m.status}
                            </span>
                          </div>

                          <div>
                            <h4 className="font-bold text-slate-200">{m.name}</h4>
                            <p className="text-xs text-slate-400">{m.location}</p>
                          </div>

                          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                            <span className="text-slate-400">LOTO Required:</span>
                            <span className="font-semibold text-slate-200">{m.requires_loto ? 'YES (Mandatory)' : 'NO'}</span>
                          </div>

                          <div className="flex items-center gap-2 pt-1">
                            <button
                              onClick={() => handleSimulateSensor(m.id, false)}
                              disabled={simulating === m.id}
                              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium py-2 rounded-lg transition"
                            >
                              Normal Ping
                            </button>
                            <button
                              onClick={() => handleSimulateSensor(m.id, true)}
                              disabled={simulating === m.id}
                              className="flex-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-xs font-bold py-2 rounded-lg transition"
                            >
                              Simulate Anomaly
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: TASKS & SAFETY EVALUATION */}
              {activeTab === 'tasks' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <h1 className="text-2xl font-bold tracking-tight text-slate-100">Maintenance Work Orders</h1>
                      <p className="text-slate-400 text-sm mt-1">Review safety status, composite risk scores, and clearance permits.</p>
                    </div>

                    <button
                      onClick={() => setShowTaskModal(true)}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all text-sm"
                    >
                      <Plus className="w-4 h-4 stroke-[3]" />
                      <span>New Work Order</span>
                    </button>
                  </div>

                  {/* Task List Table */}
                  <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900">
                    <table className="w-full text-left border-collapse text-sm">
                      <thead>
                        <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                          <th className="p-4">Task Code</th>
                          <th className="p-4">Title</th>
                          <th className="p-4">Risk Level</th>
                          <th className="p-4">Status</th>
                          <th className="p-4">Assigned Worker</th>
                          <th className="p-4">Target Machine</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {tasks.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="p-8 text-center text-slate-500">No maintenance tasks recorded yet. Click "New Work Order" to run a safety evaluation.</td>
                          </tr>
                        ) : (
                          tasks.map(t => (
                            <tr key={t.id} className="hover:bg-slate-800/40 transition">
                              <td className="p-4 font-mono text-amber-400 font-bold">{t.task_code}</td>
                              <td className="p-4">
                                <div className="font-semibold text-slate-200">{t.title}</div>
                                <div className="text-xs text-slate-400 truncate max-w-xs">{t.description}</div>
                              </td>
                              <td className="p-4">
                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                                  t.risk_level === 'CRITICAL' || t.is_blocked ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                  t.risk_level === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                                  'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                }`}>
                                  {t.is_blocked ? <XCircle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                                  {t.risk_level} ({t.composite_risk_score}/100)
                                </span>
                              </td>
                              <td className="p-4">
                                <span className={`text-xs px-2.5 py-1 rounded-lg font-bold ${
                                  t.status === 'BLOCKED' ? 'bg-rose-500 text-white' :
                                  t.status === 'APPROVED' ? 'bg-emerald-500 text-slate-950' :
                                  'bg-slate-800 text-slate-300'
                                }`}>
                                  {t.status}
                                </span>
                              </td>
                              <td className="p-4 text-slate-300">{t.worker?.full_name || `Worker #${t.worker_id}`}</td>
                              <td className="p-4 text-slate-300 font-mono text-xs">{t.machine?.name || `Machine #${t.machine_id}`}</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TAB 3: MACHINERY & IOT SENSORS */}
              {activeTab === 'machines' && (
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-100">Industrial Machinery & Telemetry</h1>
                    <p className="text-slate-400 text-sm mt-1">Monitor real-time machine safety ratings and trigger IoT sensor simulations.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {machines.map(m => (
                      <div key={m.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-mono text-amber-400 font-bold">{m.machine_code}</span>
                            <h3 className="text-lg font-bold text-slate-100">{m.name}</h3>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                            m.status === 'OPERATIONAL' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                          }`}>
                            {m.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950 p-3 rounded-xl border border-slate-800">
                          <div>
                            <span className="text-slate-500 block">Model</span>
                            <span className="text-slate-200 font-medium">{m.model}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Location</span>
                            <span className="text-slate-200 font-medium">{m.location}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Safety Score</span>
                            <span className="text-emerald-400 font-bold">{m.safety_rating} / 100</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">LOTO Enforcement</span>
                            <span className="text-amber-300 font-bold">{m.requires_loto ? 'REQUIRED' : 'NONE'}</span>
                          </div>
                        </div>

                        {/* Telemetry Output Box if available */}
                        {activeMachineTelemetry[m.id] && (
                          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                            <span className="text-xs text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                              <Radio className="w-3.5 h-3.5" />
                              <span>Latest Telemetry Ping</span>
                            </span>
                            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                              {activeMachineTelemetry[m.id].map(sensor => (
                                <div key={sensor.id} className={`p-2 rounded border ${sensor.is_anomaly ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' : 'bg-slate-900 border-slate-800 text-slate-300'}`}>
                                  <div>{sensor.sensor_type}: <span className="font-bold">{sensor.value} {sensor.unit}</span></div>
                                  {sensor.is_anomaly && <div className="text-[10px] text-rose-400 font-bold uppercase mt-0.5">ANOMALY DETECTED</div>}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSimulateSensor(m.id, false)}
                            disabled={simulating === m.id}
                            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold py-2.5 rounded-xl transition"
                          >
                            Ping Normal Telemetry
                          </button>
                          <button
                            onClick={() => handleSimulateSensor(m.id, true)}
                            disabled={simulating === m.id}
                            className="flex-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-bold py-2.5 rounded-xl transition flex items-center justify-center gap-1.5"
                          >
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>Inject Anomaly</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 4: SOP LIBRARY & AI SEARCH */}
              {activeTab === 'sops' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <h1 className="text-2xl font-bold tracking-tight text-slate-100">Standard Operating Procedures (SOPs) & AI Search</h1>
                      <p className="text-slate-400 text-sm mt-1">Vector-based semantic search & interactive SOP procedure management.</p>
                    </div>

                    <button
                      onClick={() => {
                        setSopToEdit(null);
                        setShowSopModal(true);
                      }}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all text-sm"
                    >
                      <Plus className="w-4 h-4 stroke-[3]" />
                      <span>Upload & Create New SOP</span>
                    </button>
                  </div>

                  {/* Search Bar */}
                  <div className="flex gap-3">
                    <div className="relative flex-1">
                      <Search className="w-5 h-5 text-slate-500 absolute left-4 top-3.5" />
                      <input 
                        type="text"
                        placeholder="Search SOPs by keyword (e.g., High-Voltage, Hydraulic, Grounding, Bleed valve)..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSOPSearch()}
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-12 pr-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <button
                      onClick={handleSOPSearch}
                      disabled={searchingSop}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-6 py-3 rounded-xl flex items-center gap-2 text-sm transition"
                    >
                      {searchingSop ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                      <span>Vector Search</span>
                    </button>
                  </div>

                  {/* AI Search Results */}
                  {sopSearchResults.length > 0 && (
                    <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 space-y-3">
                      <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        <span>AI Vector Search Results</span>
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {sopSearchResults.map((res: any, idx: number) => {
                          const matchedProc = procedures.find(p => p.procedure_code === res.code || p.id === res.procedure_id);
                          return (
                            <div key={idx} className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2">
                              <div className="flex items-center justify-between text-xs">
                                <span className="font-mono text-amber-400 font-bold">{res.code}</span>
                                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">Score: {(res.similarity_score * 100).toFixed(0)}%</span>
                              </div>
                              <h4 className="font-bold text-slate-200">{res.title}</h4>
                              <p className="text-xs text-slate-400">{res.description}</p>
                              {matchedProc && (
                                <div className="pt-2 flex gap-2">
                                  <button
                                    onClick={() => setSopToView(matchedProc)}
                                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1 rounded-lg font-medium transition flex items-center gap-1"
                                  >
                                    <Eye className="w-3.5 h-3.5 text-amber-400" />
                                    <span>Inspect SOP</span>
                                  </button>
                                  <button
                                    onClick={() => {
                                      setSopToEdit(matchedProc);
                                      setShowSopModal(true);
                                    }}
                                    className="text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 px-3 py-1 rounded-lg font-medium transition flex items-center gap-1"
                                  >
                                    <Edit3 className="w-3.5 h-3.5" />
                                    <span>Edit</span>
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Catalog Procedures */}
                  <div className="space-y-4">
                    {procedures.map(p => (
                      <div key={p.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                        <div className="flex items-start justify-between flex-wrap gap-2">
                          <div>
                            <span className="text-xs font-mono text-amber-400 font-bold">{p.procedure_code} • v{p.version}</span>
                            <h3 className="text-lg font-bold text-slate-100 mt-0.5">{p.title}</h3>
                            <p className="text-xs text-slate-400 mt-1">{p.description}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="bg-slate-800 text-slate-300 text-xs px-3 py-1 rounded-full font-medium">Clearance L{p.required_clearance_level}+</span>
                            <button
                              onClick={() => setSopToView(p)}
                              className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5"
                            >
                              <Eye className="w-3.5 h-3.5 text-amber-400" />
                              <span>View Full SOP</span>
                            </button>
                            <button
                              onClick={() => {
                                setSopToEdit(p);
                                setShowSopModal(true);
                              }}
                              className="bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                              <span>Edit SOP</span>
                            </button>
                          </div>
                        </div>

                        {/* Steps */}
                        <div className="space-y-2 pt-2 border-t border-slate-800">
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Required Sequential Steps ({p.steps?.length || 0})</h4>
                          <div className="space-y-2">
                            {p.steps?.map(step => (
                              <div key={step.id} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                                <div className="flex items-start gap-3">
                                  <span className="bg-amber-500 text-slate-950 font-black w-6 h-6 rounded-lg flex items-center justify-center shrink-0">
                                    {step.step_number}
                                  </span>
                                  <div>
                                    <div className="font-bold text-slate-200">{step.title}</div>
                                    <div className="text-slate-400 mt-0.5">{step.instruction}</div>
                                    {step.required_ppe && (
                                      <div className="text-amber-300 font-medium mt-1 flex items-center gap-1">
                                        <HardHat className="w-3.5 h-3.5" />
                                        <span>PPE: {step.required_ppe}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                <div className="flex items-center gap-2 self-end md:self-center">
                                  <span className={`px-2 py-0.5 rounded font-bold ${
                                    step.hazard_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' :
                                    step.hazard_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'
                                  }`}>
                                    {step.hazard_level}
                                  </span>
                                  {step.requires_supervisor_signoff && (
                                    <span className="bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded font-bold">
                                      Sign-off Required
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 5: WORKERS & CERTIFICATIONS */}
              {activeTab === 'workers' && (
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-100">Worker Registry & Safety Credentials</h1>
                    <p className="text-slate-400 text-sm mt-1">Verification of industrial clearance levels, LOTO qualification, and training record expirations.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {workers.map(w => (
                      <div key={w.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="bg-slate-800 w-10 h-10 rounded-xl flex items-center justify-center text-amber-400 font-bold">
                              {w.full_name.charAt(0)}
                            </div>
                            <div>
                              <h3 className="font-bold text-slate-100">{w.full_name}</h3>
                              <span className="text-xs font-mono text-amber-400">{w.worker_code} • {w.department}</span>
                            </div>
                          </div>
                          <span className="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs px-3 py-1 rounded-full font-bold">
                            Clearance L{w.clearance_level}
                          </span>
                        </div>

                        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                          <div className="text-xs text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                            <Award className="w-4 h-4 text-amber-400" />
                            <span>Safety Certifications & Training Records</span>
                          </div>
                          <div className="space-y-1.5 text-xs">
                            <div className="flex justify-between p-2 rounded bg-slate-900 text-slate-300">
                              <span>CERT-ELEC-01: High-Voltage Electrical</span>
                              <span className="text-emerald-400 font-bold">VALID (Exp 2028)</span>
                            </div>
                            <div className="flex justify-between p-2 rounded bg-slate-900 text-slate-300">
                              <span>CERT-LOTO-01: Lock-Out / Tag-Out Authorized</span>
                              <span className="text-emerald-400 font-bold">VALID (Exp 2027)</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 6: SUPERVISOR APPROVALS */}
              {activeTab === 'approvals' && (
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-100">Supervisor Sign-off Queue</h1>
                    <p className="text-slate-400 text-sm mt-1">High-risk procedures requiring explicit supervisor permit overrides.</p>
                  </div>

                  <div className="space-y-4">
                    {approvals.length === 0 ? (
                      <div className="p-12 text-center text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">
                        No pending supervisor approval requests.
                      </div>
                    ) : (
                      approvals.map(app => (
                        <div key={app.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono text-amber-400 font-bold">Approval #{app.id}</span>
                              <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                                app.status === 'PENDING' ? 'bg-amber-500/20 text-amber-400 animate-pulse' :
                                app.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                              }`}>
                                {app.status}
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-slate-100">High-Risk Task Order #{app.task_id}</h3>
                            <p className="text-xs text-slate-400">Requested on {new Date(app.requested_at).toLocaleString()}</p>
                          </div>

                          {app.status === 'PENDING' && (
                            <div className="flex gap-2 w-full md:w-auto">
                              <button
                                onClick={() => handleSupervisorDecision(app.id, 'APPROVED')}
                                className="flex-1 md:flex-initial bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-sm transition"
                              >
                                Approve Permit
                              </button>
                              <button
                                onClick={() => handleSupervisorDecision(app.id, 'REJECTED')}
                                className="flex-1 md:flex-initial bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 font-bold px-5 py-2.5 rounded-xl text-sm transition"
                              >
                                Reject Task
                              </button>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* TAB 7: INCIDENTS LOG */}
              {activeTab === 'incidents' && (
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-100">Safety Incident & Near-Miss Logs</h1>
                    <p className="text-slate-400 text-sm mt-1">Industrial incident reports and root cause analysis tracking.</p>
                  </div>

                  <div className="space-y-4">
                    {incidents.map(inc => (
                      <div key={inc.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono text-rose-400 font-bold">{inc.incident_code}</span>
                          <span className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs px-3 py-1 rounded-full font-bold uppercase">
                            {inc.severity} SEVERITY
                          </span>
                        </div>

                        <div>
                          <h3 className="text-lg font-bold text-slate-100">{inc.title}</h3>
                          <p className="text-xs text-slate-400 mt-1">{inc.description}</p>
                        </div>

                        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                          <span>Status: <strong className="text-amber-300">{inc.resolution_status}</strong></span>
                          <span>Reported: {new Date(inc.reported_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* Task Creation & Safety Evaluation Modal */}
      {showTaskModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2 text-amber-400">
                <ShieldAlert className="w-5 h-5" />
                <h2 className="text-lg font-bold text-slate-100">Submit Work Order & Evaluate Safety</h2>
              </div>
              <button 
                onClick={() => setShowTaskModal(false)}
                className="text-slate-400 hover:text-slate-200 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Task Title</label>
                <input 
                  type="text" 
                  placeholder="e.g., Replace Transformer Coils"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Description & Scope</label>
                <textarea 
                  placeholder="Describe maintenance actions..."
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-amber-500 h-20"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Target Machine</label>
                  <CustomSelect
                    value={newTaskMachineId}
                    onChange={(val) => setNewTaskMachineId(Number(val))}
                    options={machines.map(m => ({
                      value: m.id,
                      label: m.name,
                      sublabel: `${m.location} • Rating: ${m.safety_rating}`,
                      badge: m.machine_code
                    }))}
                    placeholder="Select machine..."
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Standard Operating Procedure</label>
                  <CustomSelect
                    value={newTaskProcedureId}
                    onChange={(val) => setNewTaskProcedureId(Number(val))}
                    options={procedures.map(p => ({
                      value: p.id,
                      label: p.title,
                      sublabel: `Req. Level ${p.required_clearance_level}+`,
                      badge: p.procedure_code
                    }))}
                    placeholder="Select procedure..."
                  />
                </div>
              </div>

              {/* Real-time Safety Risk Evaluator */}
              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleEvaluateTask}
                  disabled={evaluating}
                  className="w-full bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30 font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition"
                >
                  {evaluating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
                  <span>Run Automated Safety Evaluation</span>
                </button>
              </div>

              {/* Evaluation Outcome Box */}
              {evalResult && (
                <div className={`p-4 rounded-xl border space-y-3 ${
                  evalResult.is_permitted ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}>
                  <div className="flex items-center justify-between font-bold text-sm">
                    <div className="flex items-center gap-2">
                      {evalResult.is_permitted ? <ShieldCheck className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
                      <span>Safety Verdict: {evalResult.is_permitted ? 'PERMITTED TO DISPATCH' : 'TASK BLOCKED'}</span>
                    </div>
                    <span className="text-xs px-2.5 py-1 rounded bg-slate-950 font-mono">Risk: {evalResult.composite_risk_score}/100</span>
                  </div>

                  {evalResult.blocking_reasons?.length > 0 && (
                    <div className="text-xs space-y-1">
                      <span className="font-bold text-rose-400">Blocking Reasons:</span>
                      <ul className="list-disc list-inside text-rose-300 pl-1">
                        {evalResult.blocking_reasons.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>
                  )}

                  {evalResult.ai_safety_briefing && (
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
                      <span className="text-amber-400 font-bold flex items-center gap-1">
                        <Sparkles className="w-3.5 h-3.5" /> AI Safety Briefing
                      </span>
                      <p className="leading-relaxed">{evalResult.ai_safety_briefing}</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
              <button
                type="button"
                onClick={() => setShowTaskModal(false)}
                className="bg-slate-800 text-slate-300 px-4 py-2 rounded-xl text-sm font-medium hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCreateTask}
                disabled={!newTaskTitle}
                className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-6 py-2 rounded-xl text-sm shadow-lg shadow-amber-500/20"
              >
                Submit Work Order
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SOP Edit & Upload Modal */}
      <SopModal
        isOpen={showSopModal}
        onClose={() => {
          setShowSopModal(false);
          setSopToEdit(null);
        }}
        procedureToEdit={sopToEdit}
        onSaveSuccess={() => {
          fetchData();
          if (searchQuery) handleSOPSearch();
        }}
      />

      {/* SOP Detail Inspector Modal */}
      <SopDetailModal
        procedure={sopToView}
        onClose={() => setSopToView(null)}
        onEdit={(proc) => {
          setSopToView(null);
          setSopToEdit(proc);
          setShowSopModal(true);
        }}
      />
    </div>
  );
}
