import React, { useState } from 'react';
import { 
  FileText, 
  X, 
  Edit3, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  HardHat, 
  Lock, 
  Play,
  ArrowRight,
  RotateCcw,
  Sparkles,
  UserCheck,
  Check
} from 'lucide-react';
import { Procedure } from '../types';

interface SopDetailModalProps {
  procedure: Procedure | null;
  onClose: () => void;
  onEdit: (proc: Procedure) => void;
}

export function SopDetailModal({ procedure, onClose, onEdit }: SopDetailModalProps) {
  if (!procedure) return null;

  const [interactiveMode, setInteractiveMode] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [ppeVerified, setPpeVerified] = useState<boolean>(false);
  const [supervisorSigned, setSupervisorSigned] = useState<boolean>(false);
  const [executionFinished, setExecutionFinished] = useState<boolean>(false);

  const steps = procedure.steps || [];
  const currentStep = steps[currentStepIndex];

  const handleNextStep = () => {
    if (!currentStep) return;

    if (!completedSteps.includes(currentStepIndex)) {
      setCompletedSteps(prev => [...prev, currentStepIndex]);
    }

    if (currentStepIndex + 1 < steps.length) {
      setCurrentStepIndex(prev => prev + 1);
      setPpeVerified(false);
      setSupervisorSigned(false);
    } else {
      setExecutionFinished(true);
    }
  };

  const handleResetExecution = () => {
    setCurrentStepIndex(0);
    setCompletedSteps([]);
    setPpeVerified(false);
    setSupervisorSigned(false);
    setExecutionFinished(false);
  };

  const isStepActionDisabled = () => {
    if (!currentStep) return true;
    if (currentStep.required_ppe && !ppeVerified) return true;
    if (currentStep.requires_supervisor_signoff && !supervisorSigned) return true;
    return false;
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 space-y-6 max-h-[92vh] overflow-y-auto shadow-2xl relative">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4 flex-wrap gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-amber-400 font-bold text-xs bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-md">
                {procedure.procedure_code}
              </span>
              <span className="text-xs text-slate-400 font-mono">v{procedure.version}</span>
              <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2.5 py-0.5 rounded-md font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Approved SOP
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">{procedure.title}</h2>
            <p className="text-xs text-slate-400">{procedure.description || 'Standard industrial operating procedure.'}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setInteractiveMode(!interactiveMode);
                handleResetExecution();
              }}
              className={`text-xs px-3.5 py-2 rounded-xl font-bold transition flex items-center gap-1.5 shadow-md ${
                interactiveMode 
                  ? 'bg-amber-500 text-slate-950 hover:bg-amber-400' 
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30'
              }`}
            >
              {interactiveMode ? (
                <>
                  <FileText className="w-3.5 h-3.5" />
                  <span>Standard Reader Mode</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Interactive Guided SOP Mode</span>
                </>
              )}
            </button>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-200 text-sm p-1.5 rounded-lg hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* INTERACTIVE GUIDED EXECUTION MODE */}
        {interactiveMode ? (
          <div className="space-y-6">
            {/* Progress Header */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>Worker Interactive SOP Execution Checklist</span>
                </span>
                <span className="text-slate-300">
                  {executionFinished ? '100% Completed' : `Step ${currentStepIndex + 1} of ${steps.length}`}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-amber-500 to-emerald-400 h-full transition-all duration-300"
                  style={{
                    width: `${executionFinished ? 100 : Math.round((completedSteps.length / Math.max(steps.length, 1)) * 100)}%`
                  }}
                />
              </div>
            </div>

            {/* Completion Screen */}
            {executionFinished ? (
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6 text-center space-y-4">
                <div className="w-12 h-12 bg-emerald-500/20 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-emerald-400">SOP Protocol Completed Successfully</h3>
                  <p className="text-xs text-slate-300 mt-1">All {steps.length} sequential steps and safety verifications have been logged.</p>
                </div>

                <div className="pt-2 flex justify-center gap-3">
                  <button
                    onClick={handleResetExecution}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold px-4 py-2 rounded-xl transition flex items-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Run SOP Again</span>
                  </button>
                  <button
                    onClick={onClose}
                    className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold px-5 py-2 rounded-xl transition"
                  >
                    Finish & Exit
                  </button>
                </div>
              </div>
            ) : currentStep ? (
              /* Active Step Card */
              <div className="bg-slate-950 border border-amber-500/40 rounded-2xl p-6 space-y-5 shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 bg-amber-500 text-slate-950 text-[10px] font-black uppercase px-3 py-1 rounded-bl-xl tracking-wider">
                  Active Instruction Step
                </div>

                <div className="flex items-start gap-3">
                  <span className="bg-amber-500 text-slate-950 font-black text-lg w-9 h-9 rounded-xl flex items-center justify-center shrink-0">
                    {currentStep.step_number}
                  </span>
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">{currentStep.title}</h3>
                    <p className="text-sm text-slate-300 mt-1 leading-relaxed">{currentStep.instruction}</p>
                  </div>
                </div>

                {/* Hazard Level & Badge */}
                <div className="flex items-center gap-2 pt-2 border-t border-slate-900 flex-wrap">
                  <span className={`px-2.5 py-1 rounded-md text-xs font-bold flex items-center gap-1.5 ${
                    currentStep.hazard_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                    currentStep.hazard_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                    'bg-slate-800 text-slate-300'
                  }`}>
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>{currentStep.hazard_level} Hazard Level</span>
                  </span>

                  {currentStep.requires_supervisor_signoff && (
                    <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2.5 py-1 rounded-md text-xs font-bold flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5" />
                      <span>Supervisor Hold Point</span>
                    </span>
                  )}
                </div>

                {/* Required Verifications for this step */}
                <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
                  <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px] block">
                    Mandatory Pre-Step Safety Verifications
                  </span>

                  {/* PPE Checklist */}
                  {currentStep.required_ppe ? (
                    <label className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer hover:border-slate-700 transition">
                      <input
                        type="checkbox"
                        checked={ppeVerified}
                        onChange={(e) => setPpeVerified(e.target.checked)}
                        className="w-4 h-4 rounded text-amber-500 focus:ring-amber-500 border-slate-700 bg-slate-900"
                      />
                      <div className="flex items-center gap-2 text-slate-200">
                        <HardHat className="w-4 h-4 text-amber-400 shrink-0" />
                        <span>I confirm wearing required PPE: <strong className="text-amber-300">{currentStep.required_ppe}</strong></span>
                      </div>
                    </label>
                  ) : (
                    <div className="text-slate-500 flex items-center gap-2">
                      <Check className="w-4 h-4 text-emerald-400" />
                      <span>No specialized PPE required for this step.</span>
                    </div>
                  )}

                  {/* Supervisor Signoff */}
                  {currentStep.requires_supervisor_signoff && (
                    <label className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer hover:border-slate-700 transition">
                      <input
                        type="checkbox"
                        checked={supervisorSigned}
                        onChange={(e) => setSupervisorSigned(e.target.checked)}
                        className="w-4 h-4 rounded text-blue-500 focus:ring-blue-500 border-slate-700 bg-slate-900"
                      />
                      <div className="flex items-center gap-2 text-slate-200">
                        <UserCheck className="w-4 h-4 text-blue-400 shrink-0" />
                        <span>Supervisor Sign-off Verified (Hold Point Passed)</span>
                      </div>
                    </label>
                  )}
                </div>

                {/* Action button */}
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={handleNextStep}
                    disabled={isStepActionDisabled()}
                    className={`px-6 py-3 rounded-xl font-bold text-xs flex items-center gap-2 transition shadow-lg ${
                      isStepActionDisabled()
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed shadow-none'
                        : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
                    }`}
                  >
                    <span>{currentStepIndex + 1 === steps.length ? 'Verify & Complete SOP' : 'Verify & Proceed to Next Step'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : null}

            {/* Step list navigation dots */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
              {steps.map((s, idx) => {
                const isCurrent = idx === currentStepIndex && !executionFinished;
                const isDone = completedSteps.includes(idx) || executionFinished;

                return (
                  <button
                    key={s.id || idx}
                    onClick={() => {
                      setCurrentStepIndex(idx);
                      setExecutionFinished(false);
                      setPpeVerified(false);
                      setSupervisorSigned(false);
                    }}
                    className={`p-2.5 rounded-xl border text-left text-xs space-y-1 transition ${
                      isCurrent
                        ? 'bg-amber-500/10 border-amber-500/50 text-amber-300 ring-1 ring-amber-500/40'
                        : isDone
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between font-bold text-[10px] uppercase">
                      <span>Step {s.step_number}</span>
                      {isDone && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                    <div className="font-semibold text-slate-200 truncate">{s.title}</div>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          /* STANDARD READER MODE */
          <>
            {/* Metadata grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs bg-slate-950 p-3.5 rounded-xl border border-slate-800">
              <div>
                <span className="text-slate-500 block">Category</span>
                <span className="font-bold text-slate-200">{procedure.category}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Required Clearance</span>
                <span className="font-bold text-amber-300">Level {procedure.required_clearance_level}+</span>
              </div>
              <div>
                <span className="text-slate-500 block">Total Safety Steps</span>
                <span className="font-bold text-slate-200">{procedure.steps?.length || 0} Steps</span>
              </div>
            </div>

            {/* Sequential Steps List */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                <span>Mandatory Step-by-Step Execution Protocol</span>
              </h3>

              <div className="space-y-2.5">
                {(!procedure.steps || procedure.steps.length === 0) ? (
                  <div className="p-4 text-xs text-slate-500 text-center bg-slate-950 rounded-xl">
                    No specific steps recorded for this SOP. Click "Edit SOP" to add steps.
                  </div>
                ) : (
                  procedure.steps.map((step) => (
                    <div key={step.id || step.step_number} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <span className="bg-amber-500 text-slate-950 font-black w-6 h-6 rounded-lg flex items-center justify-center shrink-0">
                            {step.step_number}
                          </span>
                          <span className="font-bold text-slate-200 text-sm">{step.title}</span>
                        </div>

                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            step.hazard_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                            step.hazard_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                            'bg-slate-800 text-slate-300'
                          }`}>
                            {step.hazard_level} HAZARD
                          </span>
                          {step.requires_supervisor_signoff && (
                            <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded text-[11px] font-bold">
                              Supervisor Signoff Required
                            </span>
                          )}
                        </div>
                      </div>

                      <p className="text-slate-300 leading-relaxed pl-8">{step.instruction}</p>

                      {step.required_ppe && (
                        <div className="pl-8 pt-1 flex items-center gap-2 text-amber-300 font-medium text-[11px]">
                          <HardHat className="w-3.5 h-3.5 shrink-0" />
                          <span>Required PPE: {step.required_ppe}</span>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Footer buttons */}
            <div className="flex justify-between items-center pt-4 border-t border-slate-800">
              <button
                onClick={onClose}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold px-4 py-2.5 rounded-xl transition"
              >
                Close Viewer
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setInteractiveMode(true)}
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-500/20 transition flex items-center gap-2"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>Start Guided SOP Checklist</span>
                </button>

                <button
                  onClick={() => {
                    onClose();
                    onEdit(procedure);
                  }}
                  className="bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-bold px-4 py-2.5 rounded-xl transition flex items-center gap-1.5"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Edit SOP</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

