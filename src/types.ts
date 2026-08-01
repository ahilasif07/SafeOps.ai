export interface Worker {
  id: number;
  worker_code: string;
  full_name: string;
  email: string;
  role: string;
  department: string;
  clearance_level: number;
  is_active: boolean;
  created_at?: string;
}

export interface Machine {
  id: number;
  machine_code: string;
  name: string;
  model: string;
  location: string;
  status: 'OPERATIONAL' | 'MAINTENANCE' | 'OFFLINE' | 'HAZARDOUS';
  safety_rating: number;
  requires_loto: boolean;
  last_inspected_at?: string;
}

export interface ProcedureStep {
  id: number;
  step_number: number;
  title: string;
  instruction: string;
  hazard_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  requires_supervisor_signoff: boolean;
  required_ppe?: string;
}

export interface Procedure {
  id: number;
  procedure_code: string;
  title: string;
  description: string;
  category: string;
  required_clearance_level: number;
  is_approved: boolean;
  version: string;
  steps: ProcedureStep[];
}

export interface Task {
  id: number;
  task_code: string;
  title: string;
  description: string;
  status: 'DRAFT' | 'SAFETY_EVALUATION' | 'PENDING_APPROVAL' | 'APPROVED' | 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED' | 'CANCELLED';
  priority: string;
  composite_risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  is_blocked: boolean;
  blocking_reasons?: string[];
  worker_id: number;
  machine_id: number;
  procedure_id: number;
  created_at: string;
  worker?: Worker;
  machine?: Machine;
  procedure?: Procedure;
}

export interface Certification {
  id: number;
  code: string;
  name: string;
  validity_months: number;
  issuing_body: string;
}

export interface TrainingRecord {
  id: number;
  worker_id: number;
  certification_id: number;
  issued_date: string;
  expiry_date: string;
  is_valid: boolean;
  certification?: Certification;
}

export interface Incident {
  id: number;
  incident_code: string;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  machine_id?: number;
  reported_at: string;
  resolution_status: string;
  machine?: Machine;
}

export interface SupervisorApproval {
  id: number;
  task_id: number;
  supervisor_id: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  requested_at: string;
  decided_at?: string;
  comments?: string;
  task?: Task;
  supervisor?: Worker;
}

export interface SensorReading {
  id: number;
  machine_id: number;
  sensor_type: string;
  value: number;
  unit: string;
  is_anomaly: boolean;
  timestamp: string;
}

export interface SafetyEvalResponse {
  is_permitted: boolean;
  composite_risk_score: number;
  risk_level: string;
  blocking_reasons: string[];
  required_mitigations: string[];
  ai_safety_briefing: string;
  evaluation_breakdown: {
    clearance_check: boolean;
    certification_check: boolean;
    machine_status_check: boolean;
    sensor_anomaly_check: boolean;
    loto_compliance: boolean;
  };
}
