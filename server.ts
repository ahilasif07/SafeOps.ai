import express from "express";
import path from "path";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

// Lazy Gemini API Client setup
let aiClient: GoogleGenAI | null = null;
function getGeminiClient() {
  if (!aiClient && process.env.GEMINI_API_KEY) {
    aiClient = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
  }
  return aiClient;
}

// In-Memory Data Models & Seed Data
const workers = [
  {
    id: 1,
    worker_code: "WRK-1001",
    full_name: "John Doe",
    email: "john.doe@safeops.io",
    role: "TECHNICIAN",
    department: "ELECTRICAL",
    clearance_level: 3,
    is_active: true,
    created_at: new Date(Date.now() - 100 * 86400000).toISOString()
  },
  {
    id: 2,
    worker_code: "WRK-1002",
    full_name: "Sarah Connor",
    email: "sarah.c@safeops.io",
    role: "SUPERVISOR",
    department: "PLANT_OPS",
    clearance_level: 5,
    is_active: true,
    created_at: new Date(Date.now() - 200 * 86400000).toISOString()
  },
  {
    id: 3,
    worker_code: "WRK-1003",
    full_name: "Mike Vance",
    email: "mike.vance@safeops.io",
    role: "TECHNICIAN",
    department: "MECHANICAL",
    clearance_level: 1,
    is_active: true,
    created_at: new Date(Date.now() - 50 * 86400000).toISOString()
  },
  {
    id: 4,
    worker_code: "WRK-1004",
    full_name: "Alex Mercer",
    email: "alex.m@safeops.io",
    role: "SAFETY_OFFICER",
    department: "SAFETY_DEPT",
    clearance_level: 4,
    is_active: true,
    created_at: new Date(Date.now() - 150 * 86400000).toISOString()
  }
];

const certifications = [
  { id: 1, code: "CERT-ELEC-01", name: "High-Voltage Electrical Safety", validity_months: 24, issuing_body: "OSHA Safety Board" },
  { id: 2, code: "CERT-LOTO-01", name: "Lock-Out / Tag-Out Authorized Specialist", validity_months: 12, issuing_body: "National Safety Council" },
  { id: 3, code: "CERT-HAZMAT-01", name: "Hazmat & Chemical Handling", validity_months: 24, issuing_body: "EPA Industrial Safety" },
  { id: 4, code: "CERT-HYD-01", name: "High-Pressure Hydraulics", validity_months: 36, issuing_body: "Fluid Power Society" }
];

const trainingRecords: any[] = [
  { id: 1, worker_id: 1, certification_id: 1, issued_date: "2025-01-15", expiry_date: "2027-01-15", is_valid: true },
  { id: 2, worker_id: 1, certification_id: 2, issued_date: "2025-03-10", expiry_date: "2026-03-10", is_valid: true },
  { id: 3, worker_id: 2, certification_id: 1, issued_date: "2024-06-01", expiry_date: "2026-06-01", is_valid: true },
  { id: 4, worker_id: 2, certification_id: 2, issued_date: "2025-02-01", expiry_date: "2026-02-01", is_valid: true },
  { id: 5, worker_id: 2, certification_id: 3, issued_date: "2024-11-01", expiry_date: "2026-11-01", is_valid: true },
  { id: 6, worker_id: 2, certification_id: 4, issued_date: "2024-08-15", expiry_date: "2027-08-15", is_valid: true }
];

const departments: any[] = [
  { id: 1, name: "ELECTRICAL", code: "ELEC", description: "Electrical Power & Instrumentation" },
  { id: 2, name: "MECHANICAL", code: "MECH", description: "Mechanical Equipment & Hydraulics" },
  { id: 3, name: "PLANT_OPS", code: "OPS", description: "Plant Operations & Control" },
  { id: 4, name: "SAFETY_DEPT", code: "SAFE", description: "Environmental Health & Safety" },
  { id: 5, name: "CHEMICAL", code: "CHEM", description: "Chemical Processing & Refining" },
  { id: 6, name: "IT_SUPPORT", code: "IT", description: "Industrial Systems & IT Support" }
];

const roles: any[] = [
  { id: 1, name: "Mechanical Engineer", department: "MECHANICAL", clearance_level: 3 },
  { id: 2, name: "Electrical Engineer", department: "ELECTRICAL", clearance_level: 3 },
  { id: 3, name: "Plant Operator", department: "PLANT_OPS", clearance_level: 2 },
  { id: 4, name: "Safety Officer", department: "SAFETY_DEPT", clearance_level: 4 },
  { id: 5, name: "Chemical Engineer", department: "CHEMICAL", clearance_level: 3 },
  { id: 6, name: "IT Support", department: "IT_SUPPORT", clearance_level: 2 },
  { id: 7, name: "General Worker", department: "PLANT_OPS", clearance_level: 1 },
  { id: 8, name: "SUPERVISOR", department: "PLANT_OPS", clearance_level: 5 },
  { id: 9, name: "TECHNICIAN", department: "ELECTRICAL", clearance_level: 2 }
];

const workerCertifications: Record<number, string[]> = {
  1: ["CERT-ELEC-01", "CERT-LOTO-01"],
  2: ["CERT-ELEC-01", "CERT-LOTO-01", "CERT-HAZMAT-01", "CERT-HYD-01"],
  3: [], // Expired/Missing
  4: ["CERT-ELEC-01", "CERT-LOTO-01", "CERT-HAZMAT-01"]
};

const machines = [
  {
    id: 1,
    machine_code: "MCH-TURB-01",
    name: "Main Gas Turbine Alpha",
    model: "Siemens SGT-800",
    location: "Sector A - Powerhouse",
    status: "OPERATIONAL",
    safety_rating: 92.5,
    requires_loto: true,
    last_inspected_at: new Date(Date.now() - 2 * 86400000).toISOString()
  },
  {
    id: 2,
    machine_code: "MCH-PRESS-04",
    name: "Hydraulic Stamping Press 4",
    model: "Schuler 1000T",
    location: "Sector B - Fabrication",
    status: "MAINTENANCE",
    safety_rating: 84.0,
    requires_loto: true,
    last_inspected_at: new Date(Date.now() - 5 * 86400000).toISOString()
  },
  {
    id: 3,
    machine_code: "MCH-CHEM-02",
    name: "Chemical Reactor Vessel 2",
    model: "Pfaudler 5000L",
    location: "Sector C - Chemical Processing",
    status: "HAZARDOUS",
    safety_rating: 65.0,
    requires_loto: true,
    last_inspected_at: new Date(Date.now() - 1 * 86400000).toISOString()
  }
];

interface MachineProcedureJoin {
  id: number;
  machine_id: number;
  procedure_id: number;
  assigned_at: string;
}

const machineProcedures: MachineProcedureJoin[] = [
  { id: 1, machine_id: 1, procedure_id: 1, assigned_at: new Date().toISOString() },
  { id: 2, machine_id: 2, procedure_id: 2, assigned_at: new Date().toISOString() },
  { id: 3, machine_id: 3, procedure_id: 1, assigned_at: new Date().toISOString() }
];

const procedures = [
  {
    id: 1,
    procedure_code: "SOP-ELEC-401",
    title: "High-Voltage Transformer Maintenance & Inspection",
    description: "Standard procedure for isolating, testing, and replacing transformer coils.",
    category: "ELECTRICAL",
    required_clearance_level: 3,
    is_approved: true,
    version: "2.1",
    steps: [
      {
        id: 101,
        step_number: 1,
        title: "Verify Lock-Out / Tag-Out (LOTO)",
        instruction: "De-energize main 13.8kV circuit breaker and place master padlocks.",
        hazard_level: "CRITICAL",
        requires_supervisor_signoff: true,
        required_ppe: "Arc Flash Suit Level 4, Insulated Gloves 20kV"
      },
      {
        id: 102,
        step_number: 2,
        title: "Grounding Rod Discharge",
        instruction: "Attach grounding cable to discharge remaining capacitive charge.",
        hazard_level: "HIGH",
        requires_supervisor_signoff: false,
        required_ppe: "Safety Glasses, Insulated Gloves 20kV"
      },
      {
        id: 103,
        step_number: 3,
        title: "Insulation Oil Sampling",
        instruction: "Extract 500ml of oil from the bottom valve for breakdown voltage testing.",
        hazard_level: "MEDIUM",
        requires_supervisor_signoff: false,
        required_ppe: "Nitrile Gloves, Respirator"
      }
    ]
  },
  {
    id: 2,
    procedure_code: "SOP-HYD-202",
    title: "Hydraulic Cylinder Seal Replacement",
    description: "Procedure for depressurizing and replacing piston rod seals on stamping presses.",
    category: "HYDRAULIC",
    required_clearance_level: 2,
    is_approved: true,
    version: "1.0",
    steps: [
      {
        id: 201,
        step_number: 1,
        title: "Bleed Hydraulic Line Pressure",
        instruction: "Open bleed valve V-102 until accumulator pressure reads 0 PSI.",
        hazard_level: "HIGH",
        requires_supervisor_signoff: true,
        required_ppe: "Face Shield, Heavy Leather Gloves"
      },
      {
        id: 202,
        step_number: 2,
        title: "Remove Cylinder End Cap",
        instruction: "Unbolt 12 M24 retaining bolts in star pattern.",
        hazard_level: "MEDIUM",
        requires_supervisor_signoff: false,
        required_ppe: "Steel Toe Boots, Safety Glasses"
      }
    ]
  }
];

const sensorReadings: any[] = [
  { id: 1, machine_id: 1, sensor_type: "TEMPERATURE", value: 68.5, unit: "C", is_anomaly: false, timestamp: new Date().toISOString() },
  { id: 2, machine_id: 1, sensor_type: "VIBRATION", value: 2.1, unit: "mm/s", is_anomaly: false, timestamp: new Date().toISOString() },
  { id: 3, machine_id: 3, sensor_type: "TOXIC_GAS", value: 18.4, unit: "ppm", is_anomaly: true, timestamp: new Date().toISOString() },
  { id: 4, machine_id: 3, sensor_type: "TEMPERATURE", value: 102.3, unit: "C", is_anomaly: true, timestamp: new Date().toISOString() }
];

interface SensorRangeRecord {
  id: number;
  machine_id: number;
  sensor_type: string;
  min_value: number;
  max_value: number;
}

const defaultSensorRanges: Record<string, { min: number; max: number }> = {
  TEMPERATURE: { min: 45.0, max: 90.0 },
  PRESSURE: { min: 20.0, max: 100.0 },
  VIBRATION: { min: 0.5, max: 5.0 },
  TOXIC_GAS: { min: 0.0, max: 25.0 }
};

const sensorRanges: SensorRangeRecord[] = [
  { id: 1, machine_id: 1, sensor_type: "TEMPERATURE", min_value: 45.5, max_value: 90.25 },
  { id: 2, machine_id: 1, sensor_type: "PRESSURE", min_value: 20.0, max_value: 100.0 },
  { id: 3, machine_id: 1, sensor_type: "VIBRATION", min_value: 0.5, max_value: 5.0 },
  { id: 4, machine_id: 1, sensor_type: "TOXIC_GAS", min_value: 0.0, max_value: 25.0 },
  { id: 5, machine_id: 3, sensor_type: "TOXIC_GAS", min_value: 0.0, max_value: 10.0 },
  { id: 6, machine_id: 3, sensor_type: "TEMPERATURE", min_value: 40.0, max_value: 85.0 }
];

function getRangeForSensor(machineId: number, sensorType: string): { min: number; max: number } {
  const normType = String(sensorType || "").toUpperCase();
  const saved = sensorRanges.find(r => r.machine_id === Number(machineId) && r.sensor_type.toUpperCase() === normType);
  if (saved) {
    return { min: saved.min_value, max: saved.max_value };
  }
  const fallback = defaultSensorRanges[normType] || { min: 0.0, max: 100.0 };
  return fallback;
}

function checkIsAnomaly(machineId: number, sensorType: string, value: number): boolean {
  const numVal = Number(value);
  if (isNaN(numVal)) return false;
  const range = getRangeForSensor(machineId, sensorType);
  return numVal < range.min || numVal > range.max;
}

const incidents = [
  {
    id: 1,
    incident_code: "INC-2026-001",
    title: "Over-pressurization Alarm on Reactor 2",
    description: "Pressure spiked to 145 PSI during chemical batching process.",
    severity: "HIGH",
    machine_id: 3,
    reported_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    resolution_status: "UNDER_INVESTIGATION"
  }
];

const tasks: any[] = [
  {
    id: 1,
    task_code: "TSK-8801",
    title: "Annual Transformer Insulation Test",
    description: "Perform insulation voltage breakdown sampling and oil test.",
    status: "IN_PROGRESS",
    priority: "HIGH",
    composite_risk_score: 35.0,
    risk_level: "MEDIUM",
    is_blocked: false,
    blocking_reasons: [],
    worker_id: 1,
    machine_id: 1,
    procedure_id: 1,
    created_at: new Date(Date.now() - 1 * 86400000).toISOString()
  }
];

const approvals: any[] = [
  {
    id: 1,
    task_id: 1,
    supervisor_id: 2,
    status: "APPROVED",
    requested_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    decided_at: new Date(Date.now() - 1 * 86400000 + 3600000).toISOString(),
    comments: "LOTO verified and worker clearance level 3 confirmed."
  }
];

const issues: any[] = [
  {
    id: 1,
    issue_code: "ISS-2026-001",
    title: "Hydraulic Seal Leak on Stamping Press 4",
    description: "Persistent hydraulic fluid leak around piston rod gland packing. Requires immediate seal replacement.",
    machine_id: 2,
    department: "MECHANICAL",
    priority: "HIGH",
    status: "In Progress",
    reporter_id: 1,
    assigned_worker_id: 3,
    assigned_supervisor_id: 2,
    due_date: new Date(Date.now() + 2 * 86400000).toISOString(),
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    comments: [
      {
        id: 1,
        issue_id: 1,
        author_id: 1,
        author_name: "John Doe",
        comment_text: "Noticed oil residue accumulating during morning shift inspection.",
        created_at: new Date(Date.now() - 2 * 86400000).toISOString()
      },
      {
        id: 2,
        issue_id: 1,
        author_id: 3,
        author_name: "Mike Vance",
        comment_text: "Ordered replacement seal kit SK-1000T. Scheduled maintenance window.",
        created_at: new Date(Date.now() - 1 * 86400000).toISOString()
      }
    ],
    attachments: [
      {
        id: 1,
        issue_id: 1,
        file_name: "seal_leak_photo.jpg",
        file_url: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80",
        file_type: "image",
        uploaded_at: new Date(Date.now() - 2 * 86400000).toISOString()
      }
    ],
    status_history: [
      {
        id: 1,
        issue_id: 1,
        changed_by_id: 1,
        from_status: "CREATED",
        to_status: "Open",
        notes: "Issue logged",
        changed_at: new Date(Date.now() - 2 * 86400000).toISOString()
      },
      {
        id: 2,
        issue_id: 1,
        changed_by_id: 2,
        from_status: "Open",
        to_status: "In Progress",
        notes: "Assigned to Mike Vance for replacement.",
        changed_at: new Date(Date.now() - 1 * 86400000).toISOString()
      }
    ],
    ownership_history: [
      {
        id: 1,
        issue_id: 1,
        action_type: "INITIAL_CREATION",
        new_owner_id: 3,
        new_supervisor_id: 2,
        new_department: "MECHANICAL",
        changed_by_id: 1,
        reason_notes: "Logged by John Doe",
        changed_at: new Date(Date.now() - 2 * 86400000).toISOString()
      }
    ]
  },
  {
    id: 2,
    issue_code: "ISS-2026-002",
    title: "Gas Turbine Alpha Vibration Sensor Calibration",
    description: "Sensor VIB-01 showing minor baseline drift during warm-up cycle.",
    machine_id: 1,
    department: "ELECTRICAL",
    priority: "LOW",
    status: "Open",
    reporter_id: 2,
    assigned_worker_id: 1,
    assigned_supervisor_id: 2,
    due_date: new Date(Date.now() + 5 * 86400000).toISOString(),
    created_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    comments: [],
    attachments: [],
    status_history: [
      {
        id: 3,
        issue_id: 2,
        changed_by_id: 2,
        from_status: "CREATED",
        to_status: "Open",
        notes: "Calibration requested",
        changed_at: new Date(Date.now() - 1 * 86400000).toISOString()
      }
    ],
    ownership_history: [
      {
        id: 2,
        issue_id: 2,
        action_type: "INITIAL_CREATION",
        new_owner_id: 1,
        new_supervisor_id: 2,
        new_department: "ELECTRICAL",
        changed_by_id: 2,
        reason_notes: "Logged by Sarah Connor",
        changed_at: new Date(Date.now() - 1 * 86400000).toISOString()
      }
    ]
  }
];

// Helper for Fuzzy String Comparison
function stringSimilarity(s1: string, s2: string): number {
  if (!s1 || !s2) return 0;
  const norm1 = s1.toLowerCase().replace(/[^\w\s]/g, '').trim();
  const norm2 = s2.toLowerCase().replace(/[^\w\s]/g, '').trim();
  if (norm1 === norm2) return 1.0;
  if (!norm1.length || !norm2.length) return 0;

  const len1 = norm1.length;
  const len2 = norm2.length;
  const matrix: number[][] = [];
  for (let i = 0; i <= len1; i++) matrix[i] = [i];
  for (let j = 0; j <= len2; j++) matrix[0][j] = j;
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = norm1[i - 1] === norm2[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }
  const maxLen = Math.max(len1, len2);
  return (maxLen - matrix[len1][len2]) / maxLen;
}

// Helper to expand relationships for objects
function expandWorker(workerId?: number) {
  return workers.find(w => w.id === workerId);
}

function expandMachine(machineId?: number) {
  return machines.find(m => m.id === machineId);
}

function expandProcedure(procedureId?: number) {
  return procedures.find(p => p.id === procedureId);
}

function expandIssue(issue: any) {
  return {
    ...issue,
    machine: expandMachine(issue.machine_id),
    reporter: expandWorker(issue.reporter_id),
    assigned_worker: expandWorker(issue.assigned_worker_id),
    assigned_supervisor: expandWorker(issue.assigned_supervisor_id),
    comments: (issue.comments || []).map((c: any) => ({
      ...c,
      author: expandWorker(c.author_id)
    })),
    status_history: (issue.status_history || []).map((s: any) => ({
      ...s,
      changed_by: expandWorker(s.changed_by_id)
    })),
    ownership_history: (issue.ownership_history || []).map((o: any) => ({
      ...o,
      previous_owner: expandWorker(o.previous_owner_id),
      new_owner: expandWorker(o.new_owner_id),
      previous_supervisor: expandWorker(o.previous_supervisor_id),
      new_supervisor: expandWorker(o.new_supervisor_id),
      changed_by: expandWorker(o.changed_by_id)
    }))
  };
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // --- API ROUTES ---

  // Health
  app.get("/api/v1/health", (req, res) => {
    res.json({ status: "ok", service: "SafeOps AI Enterprise Engine" });
  });

  // Workers
  app.get(["/api/v1/workers/", "/api/v1/workers"], (req, res) => {
    res.json(workers);
  });

  app.post(["/api/v1/workers/", "/api/v1/workers"], (req, res) => {
    const { worker_code, full_name, email, role, department, clearance_level } = req.body;
    const newWorker = {
      id: workers.length + 1,
      worker_code: worker_code || `WRK-${Math.floor(1000 + Math.random() * 9000)}`,
      full_name,
      email,
      role: role || "TECHNICIAN",
      department: department || "ELECTRICAL",
      clearance_level: Number(clearance_level) || 1,
      is_active: true,
      created_at: new Date().toISOString()
    };
    workers.push(newWorker);
    workerCertifications[newWorker.id] = ["CERT-ELEC-01", "CERT-LOTO-01"];
    res.status(201).json(newWorker);
  });

  // Certifications & Training Records
  app.get(["/api/v1/certifications/", "/api/v1/certifications"], (req, res) => {
    res.json(certifications);
  });

  app.post(["/api/v1/certifications/", "/api/v1/certifications"], (req, res) => {
    const { code, name, validity_months, issuing_body } = req.body;
    const newCert = {
      id: certifications.length + 1,
      code: code || `CERT-${Math.floor(100 + Math.random() * 900)}`,
      name: name || "New Certification",
      validity_months: Number(validity_months) || 12,
      issuing_body: issuing_body || "Industrial Safety Board"
    };
    certifications.push(newCert);
    res.status(201).json(newCert);
  });

  app.post(["/api/v1/certifications/worker/", "/api/v1/certifications/worker"], (req, res) => {
    const { worker_id, certification_id, issued_date, expiry_date, is_valid } = req.body;
    const record = {
      id: trainingRecords.length + 1,
      worker_id: Number(worker_id),
      certification_id: Number(certification_id),
      issued_date: issued_date || new Date().toISOString().split('T')[0],
      expiry_date: expiry_date || new Date(Date.now() + 365 * 86400000).toISOString().split('T')[0],
      is_valid: is_valid !== undefined ? Boolean(is_valid) : true
    };
    trainingRecords.push(record);

    // Sync workerCertifications codes list
    const cert = certifications.find(c => c.id === Number(certification_id));
    if (cert) {
      if (!workerCertifications[record.worker_id]) {
        workerCertifications[record.worker_id] = [];
      }
      if (!workerCertifications[record.worker_id].includes(cert.code)) {
        workerCertifications[record.worker_id].push(cert.code);
      }
    }

    res.status(201).json(record);
  });

  app.get(["/api/v1/certifications/worker/:worker_id/", "/api/v1/certifications/worker/:worker_id"], (req, res) => {
    const workerId = Number(req.params.worker_id);
    const records = trainingRecords.filter(r => r.worker_id === workerId).map(r => ({
      ...r,
      certification: certifications.find(c => c.id === r.certification_id)
    }));
    res.json(records);
  });

  // Departments
  app.get(["/api/v1/departments/", "/api/v1/departments"], (req, res) => {
    res.json(departments);
  });

  app.post(["/api/v1/departments/", "/api/v1/departments"], (req, res) => {
    const { name, code, description } = req.body;
    const newDept = {
      id: departments.length + 1,
      name: String(name || "NEW_DEPT").toUpperCase().replace(/\s+/g, '_'),
      code: code || (name ? name.slice(0, 4).toUpperCase() : "DEPT"),
      description: description || ""
    };
    departments.push(newDept);
    res.status(201).json(newDept);
  });

  // Roles
  app.get(["/api/v1/roles/", "/api/v1/roles"], (req, res) => {
    res.json(roles);
  });

  app.post(["/api/v1/roles/", "/api/v1/roles"], (req, res) => {
    const { name, department, clearance_level } = req.body;
    const newRole = {
      id: roles.length + 1,
      name: String(name || "New Role"),
      department: department || "PLANT_OPS",
      clearance_level: clearance_level ? Number(clearance_level) : 1
    };
    roles.push(newRole);
    res.status(201).json(newRole);
  });

  // Machines
  app.get("/api/v1/machines/", (req, res) => {
    res.json(machines);
  });

  app.get("/api/v1/machines", (req, res) => {
    res.json(machines);
  });

  app.post("/api/v1/machines/", (req, res) => {
    const { machine_code, name, model, location, status, safety_rating, requires_loto } = req.body;
    const newMachine = {
      id: machines.length + 1,
      machine_code: machine_code || `MCH-${Math.floor(1000 + Math.random() * 9000)}`,
      name,
      model,
      location: location || "Sector A",
      status: status || "OPERATIONAL",
      safety_rating: Number(safety_rating) || 90.0,
      requires_loto: Boolean(requires_loto),
      last_inspected_at: new Date().toISOString()
    };
    machines.push(newMachine);
    res.status(201).json(newMachine);
  });

  // Machine-SOP Assignments (join table machine_procedures)
  // GET /api/v1/machines/{machine_id}/sops — return list of SOPs assigned to that machine
  app.get(["/api/v1/machines/:machine_id/sops/", "/api/v1/machines/:machine_id/sops"], (req, res) => {
    const machineId = Number(req.params.machine_id);
    const machine = machines.find(m => m.id === machineId);
    if (!machine) {
      return res.status(404).json({ detail: "Machine not found" });
    }

    const assignedProcIds = machineProcedures
      .filter(mp => mp.machine_id === machineId)
      .map(mp => mp.procedure_id);

    const assignedSops = procedures.filter(p => assignedProcIds.includes(p.id));
    res.json(assignedSops);
  });

  // POST /api/v1/machines/{machine_id}/sops — assign an SOP to a machine, body: { "procedure_id": 1 }
  app.post(["/api/v1/machines/:machine_id/sops/", "/api/v1/machines/:machine_id/sops"], (req, res) => {
    const machineId = Number(req.params.machine_id);
    const machine = machines.find(m => m.id === machineId);
    if (!machine) {
      return res.status(404).json({ detail: "Machine not found" });
    }

    const procedureId = Number(req.body?.procedure_id || req.body?.procedureId);
    if (!procedureId || isNaN(procedureId)) {
      return res.status(400).json({ detail: "Valid procedure_id is required" });
    }

    const procedure = procedures.find(p => p.id === procedureId);
    if (!procedure) {
      return res.status(404).json({ detail: "Procedure not found" });
    }

    let existing = machineProcedures.find(mp => mp.machine_id === machineId && mp.procedure_id === procedureId);
    if (!existing) {
      existing = {
        id: machineProcedures.length + 1,
        machine_id: machineId,
        procedure_id: procedureId,
        assigned_at: new Date().toISOString()
      };
      machineProcedures.push(existing);
    }

    res.status(201).json({
      machine_id: machineId,
      procedure_id: procedureId,
      assigned_at: existing.assigned_at,
      procedure: procedure
    });
  });

  // DELETE /api/v1/machines/{machine_id}/sops/{procedure_id} — unassign an SOP from a machine
  app.delete([
    "/api/v1/machines/:machine_id/sops/:procedure_id/",
    "/api/v1/machines/:machine_id/sops/:procedure_id",
    "/api/v1/machines/:id/sops/:procedure_id/",
    "/api/v1/machines/:id/sops/:procedure_id"
  ], (req, res) => {
    const machineId = Number(req.params.machine_id || req.params.id);
    const procedureId = Number(req.params.procedure_id);

    const index = machineProcedures.findIndex(mp => mp.machine_id === machineId && mp.procedure_id === procedureId);
    if (index === -1) {
      return res.status(404).json({ detail: "SOP assignment not found for this machine" });
    }

    machineProcedures.splice(index, 1);
    res.json({ message: "SOP unassigned successfully", machine_id: machineId, procedure_id: procedureId });
  });

  // Procedures / SOPs
  app.get("/api/v1/procedures/", (req, res) => {
    res.json(procedures);
  });

  app.get("/api/v1/procedures", (req, res) => {
    res.json(procedures);
  });

  app.post(["/api/v1/procedures/", "/api/v1/procedures"], (req, res) => {
    const { procedure_code, title, description, category, required_clearance_level, version, steps } = req.body;
    const newProc = {
      id: procedures.length + 1,
      procedure_code: procedure_code || `SOP-${Math.floor(100 + Math.random() * 900)}`,
      title,
      description: description || "",
      category: category || "ELECTRICAL",
      required_clearance_level: Number(required_clearance_level) || 1,
      is_approved: true,
      version: version || "1.0",
      steps: Array.isArray(steps) ? steps.map((s: any, idx: number) => ({
        id: (procedures.length + 1) * 100 + idx + 1,
        step_number: idx + 1,
        title: s.title || `Step ${idx + 1}`,
        instruction: s.instruction || s.title || "",
        hazard_level: s.hazard_level || "LOW",
        requires_supervisor_signoff: Boolean(s.requires_supervisor_signoff),
        required_ppe: s.required_ppe || "Safety Glasses"
      })) : []
    };
    procedures.push(newProc);
    res.status(201).json(newProc);
  });

  app.put("/api/v1/procedures/:id", (req, res) => {
    const procId = Number(req.params.id);
    const procIndex = procedures.findIndex(p => p.id === procId);
    if (procIndex === -1) {
      return res.status(404).json({ detail: "Procedure not found" });
    }
    const { procedure_code, title, description, category, required_clearance_level, version, steps } = req.body;
    procedures[procIndex] = {
      ...procedures[procIndex],
      procedure_code: procedure_code || procedures[procIndex].procedure_code,
      title: title || procedures[procIndex].title,
      description: description !== undefined ? description : procedures[procIndex].description,
      category: category || procedures[procIndex].category,
      required_clearance_level: required_clearance_level !== undefined ? Number(required_clearance_level) : procedures[procIndex].required_clearance_level,
      version: version || procedures[procIndex].version,
      steps: Array.isArray(steps) ? steps.map((s: any, idx: number) => ({
        id: s.id || (procId * 100 + idx + 1),
        step_number: idx + 1,
        title: s.title || `Step ${idx + 1}`,
        instruction: s.instruction || s.title || "",
        hazard_level: s.hazard_level || "LOW",
        requires_supervisor_signoff: Boolean(s.requires_supervisor_signoff),
        required_ppe: s.required_ppe || "Safety Glasses"
      })) : procedures[procIndex].steps
    };
    res.json(procedures[procIndex]);
  });

  // DELETE /api/v1/procedures/{id} — delete SOP procedure by ID
  app.delete(["/api/v1/procedures/:id/", "/api/v1/procedures/:id"], (req, res) => {
    const procId = Number(req.params.id);
    const procIndex = procedures.findIndex(p => p.id === procId);
    if (procIndex === -1) {
      return res.status(404).json({ detail: "Procedure not found" });
    }

    const deletedProc = procedures.splice(procIndex, 1)[0];

    // Clean up machine-SOP assignments
    let j = machineProcedures.length;
    while (j--) {
      if (machineProcedures[j].procedure_id === procId) {
        machineProcedures.splice(j, 1);
      }
    }

    res.json({ message: "Procedure deleted successfully", id: procId, deleted_procedure: deletedProc });
  });

  // SOP AI & Vector Indexing
  app.post("/api/v1/sop-ai/index/:id", (req, res) => {
    res.json({ status: "indexed", procedure_id: Number(req.params.id) });
  });

  app.get("/api/v1/sop-ai/search", async (req, res) => {
    const q = String(req.query.q || "").toLowerCase();
    const results = procedures.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q) ||
      p.steps.some((s: any) => s.title.toLowerCase().includes(q) || s.instruction.toLowerCase().includes(q))
    ).map(p => ({
      procedure_id: p.id,
      // Use 'code' to match what the frontend reads as res.code
      code: p.procedure_code,
      // Keep procedure_code for backwards compat
      procedure_code: p.procedure_code,
      title: p.title,
      description: p.description,
      category: p.category,
      // Use 'similarity_score' to match what the frontend renders
      similarity_score: 0.92,
      relevance_score: 0.92,
      matching_steps: p.steps
    }));

    if (results.length > 0) {
      return res.json(results);
    }

    // Fallback response if query didn't match directly
    return res.json(procedures.slice(0, 2).map(p => ({
      procedure_id: p.id,
      code: p.procedure_code,
      procedure_code: p.procedure_code,
      title: p.title,
      description: p.description,
      category: p.category,
      similarity_score: 0.75,
      relevance_score: 0.75,
      matching_steps: p.steps
    })));
  });

  // Tasks
  app.get("/api/v1/tasks/", (req, res) => {
    const expandedTasks = tasks.map(t => ({
      ...t,
      worker: expandWorker(t.worker_id),
      machine: expandMachine(t.machine_id),
      procedure: expandProcedure(t.procedure_id)
    }));
    res.json(expandedTasks);
  });

  app.get("/api/v1/tasks", (req, res) => {
    const expandedTasks = tasks.map(t => ({
      ...t,
      worker: expandWorker(t.worker_id),
      machine: expandMachine(t.machine_id),
      procedure: expandProcedure(t.procedure_id)
    }));
    res.json(expandedTasks);
  });

  app.post(["/api/v1/tasks/", "/api/v1/tasks"], (req, res) => {
    const {
      title, description, worker_id, machine_id, procedure_id, priority,
      // Accept safety evaluation data passed from the frontend
      composite_risk_score, risk_level, is_blocked, blocking_reasons,
      send_for_approval
    } = req.body;

    const resolvedRiskScore = composite_risk_score !== undefined ? Number(composite_risk_score) : 25.0;
    const resolvedRiskLevel = risk_level || "LOW";
    const resolvedIsBlocked = is_blocked !== undefined ? Boolean(is_blocked) : false;
    const resolvedBlockingReasons = Array.isArray(blocking_reasons) ? blocking_reasons : [];

    // Status: if blocked and sent for approval, set PENDING_APPROVAL; else IN_PROGRESS or BLOCKED
    let status = "IN_PROGRESS";
    if (resolvedIsBlocked && send_for_approval) {
      status = "PENDING_APPROVAL";
    } else if (resolvedIsBlocked) {
      status = "BLOCKED";
    }

    const newTask = {
      id: tasks.length + 1,
      task_code: `TSK-${Math.floor(8000 + Math.random() * 1000)}`,
      title,
      description: description || "",
      status,
      priority: priority || "HIGH",
      composite_risk_score: resolvedRiskScore,
      risk_level: resolvedRiskLevel,
      is_blocked: resolvedIsBlocked,
      blocking_reasons: resolvedBlockingReasons,
      worker_id: Number(worker_id),
      machine_id: Number(machine_id),
      procedure_id: Number(procedure_id),
      created_at: new Date().toISOString()
    };
    tasks.push(newTask);

    // If blocked and needs approval, automatically create an approval record
    if (resolvedIsBlocked && send_for_approval) {
      const supervisors = workers.filter(w => w.role === "SUPERVISOR" || w.clearance_level >= 4);
      const supervisorId = supervisors.length > 0 ? supervisors[0].id : 2;
      approvals.push({
        id: approvals.length + 1,
        task_id: newTask.id,
        supervisor_id: supervisorId,
        status: "PENDING",
        requested_at: new Date().toISOString(),
        decided_at: undefined,
        comments: `Auto-generated approval request. Blocking reasons: ${resolvedBlockingReasons.join("; ")}`
      });
    }

    res.status(201).json({
      ...newTask,
      worker: expandWorker(newTask.worker_id),
      machine: expandMachine(newTask.machine_id),
      procedure: expandProcedure(newTask.procedure_id)
    });
  });

  // Incidents
  app.get("/api/v1/incidents/", (req, res) => {
    const expandedIncidents = incidents.map(inc => ({
      ...inc,
      machine: expandMachine(inc.machine_id)
    }));
    res.json(expandedIncidents);
  });

  app.get("/api/v1/incidents", (req, res) => {
    const expandedIncidents = incidents.map(inc => ({
      ...inc,
      machine: expandMachine(inc.machine_id)
    }));
    res.json(expandedIncidents);
  });

  // Approvals
  app.get("/api/v1/approvals/", (req, res) => {
    const expandedApprovals = approvals.map(a => {
      const task = tasks.find(t => t.id === a.task_id);
      return {
        ...a,
        task: task ? {
          ...task,
          worker: expandWorker(task.worker_id),
          machine: expandMachine(task.machine_id),
          procedure: expandProcedure(task.procedure_id)
        } : undefined,
        supervisor: expandWorker(a.supervisor_id)
      };
    });
    res.json(expandedApprovals);
  });

  app.put("/api/v1/approvals/:id", (req, res) => {
    const approvalId = Number(req.params.id);
    const approval = approvals.find(a => a.id === approvalId);
    if (!approval) {
      return res.status(404).json({ detail: "Approval record not found" });
    }
    const { status, comments } = req.body;
    approval.status = status;
    approval.comments = comments || approval.comments;
    approval.decided_at = new Date().toISOString();
    res.json(approval);
  });

  // Safety Evaluation Engine & AI Advisor
  app.post("/api/v1/safety/evaluate", async (req, res) => {
    const { worker_id, machine_id, procedure_id } = req.body;

    const worker = expandWorker(Number(worker_id));
    const machine = expandMachine(Number(machine_id));
    const procedure = expandProcedure(Number(procedure_id));

    if (!worker || !machine || !procedure) {
      return res.status(404).json({ detail: "Worker, Machine, or Procedure not found" });
    }

    const blocking_reasons: string[] = [];
    const required_mitigations: string[] = [];
    let riskScore = 15.0;

    // Clearance Check
    const clearance_check = worker.clearance_level >= procedure.required_clearance_level;
    if (!clearance_check) {
      blocking_reasons.push(`Worker Clearance Level ${worker.clearance_level} insufficient for Procedure Required Level ${procedure.required_clearance_level}`);
      required_mitigations.push("Obtain Supervisor Override & Temporary Level 3 Authorization Badge.");
      riskScore += 35.0;
    }

    // Certifications Check
    const activeCerts = workerCertifications[worker.id] || [];
    const requiredCerts = procedure.category === "ELECTRICAL" ? ["CERT-ELEC-01", "CERT-LOTO-01"] : ["CERT-HYD-01", "CERT-LOTO-01"];
    const missingCerts = requiredCerts.filter(c => !activeCerts.includes(c));
    const certification_check = missingCerts.length === 0;

    if (!certification_check) {
      blocking_reasons.push(`Missing mandatory safety certifications: ${missingCerts.join(", ")}`);
      required_mitigations.push(`Complete refresher training module for ${missingCerts[0]}.`);
      riskScore += 25.0;
    }

    // Machine Status Check
    const machine_status_check = machine.status === "OPERATIONAL";
    if (machine.status === "MAINTENANCE") {
      riskScore += 15.0;
      required_mitigations.push("Perform double lock tag out check before restoring hydraulic power.");
    } else if (machine.status === "HAZARDOUS" || machine.status === "OFFLINE") {
      blocking_reasons.push(`Target machine status is currently ${machine.status}`);
      riskScore += 40.0;
    }

    // Sensor Anomaly Check — only examine the LATEST reading per sensor type
    const machineSensors = sensorReadings.filter(s => s.machine_id === machine.id);
    // Group by sensor_type and take the most recent entry for each
    const latestBySensorType: Record<string, any> = {};
    for (const reading of machineSensors) {
      const st = String(reading.sensor_type).toUpperCase();
      if (!latestBySensorType[st] || new Date(reading.timestamp) >= new Date(latestBySensorType[st].timestamp)) {
        latestBySensorType[st] = reading;
      }
    }
    const latestReadings = Object.values(latestBySensorType);
    const anomalousReadings = latestReadings.filter(s => s.is_anomaly);
    const hasAnomaly = anomalousReadings.length > 0;
    const sensor_anomaly_check = !hasAnomaly;
    if (hasAnomaly) {
      const anomalousTypes = anomalousReadings.map(s => `${s.sensor_type} (${s.value} ${s.unit})`).join(", ");
      blocking_reasons.push(`Active telemetry anomaly detected on machine sensors: ${anomalousTypes}`);
      required_mitigations.push("Purge sensor lines and calibrate the affected sensor(s) back to baseline.");
      riskScore += 20.0;
    }

    const loto_compliance = !machine.requires_loto || activeCerts.includes("CERT-LOTO-01");

    const finalScore = Math.min(100, Math.round(riskScore));
    let risk_level = "LOW";
    if (finalScore >= 80) risk_level = "CRITICAL";
    else if (finalScore >= 60) risk_level = "HIGH";
    else if (finalScore >= 35) risk_level = "MEDIUM";

    const is_permitted = blocking_reasons.length === 0;

    // Generate AI Safety Briefing (Dynamic intelligent fallback with optional Gemini enrichment)
    const hazardsText = blocking_reasons.length > 0 ? `Hazards/Blocks: ${blocking_reasons.join("; ")}.` : "All safety baseline criteria passed.";
    const mitigationsText = required_mitigations.length > 0 ? ` Required Action: ${required_mitigations.join("; ")}.` : " Maintain standard vigilance.";
    let ai_safety_briefing = `[Safety Advisory] ${worker.full_name} operating ${machine.name} for SOP "${procedure.title}" (Risk Level: ${risk_level}, Score: ${finalScore}/100). ${hazardsText}${mitigationsText}`;

    const gemini = getGeminiClient();
    if (gemini) {
      try {
        const response = await gemini.models.generateContent({
          model: "gemini-2.0-flash",
          contents: `Generate a concise 2-sentence industrial safety briefing for technician ${worker.full_name} performing "${procedure.title}" on machine "${machine.name}". Risk Score: ${finalScore}/100 (${risk_level}). Hazards/Issues: ${blocking_reasons.concat(required_mitigations).join("; ")}`
        });
        if (response.text) {
          ai_safety_briefing = response.text.trim();
        }
      } catch (err: any) {
        // Silently use dynamic safety briefing fallback without triggering console error dumps
        console.log("Using dynamic safety briefing fallback (Gemini API unavailable or rate limited)");
      }
    }

    res.json({
      is_permitted,
      composite_risk_score: finalScore,
      risk_level,
      blocking_reasons,
      required_mitigations,
      ai_safety_briefing,
      evaluation_breakdown: {
        clearance_check,
        certification_check,
        machine_status_check,
        sensor_anomaly_check,
        loto_compliance
      }
    });
  });

  // --- SENSOR TELEMETRY & RANGES MODULE ---

  // GET Sensor Readings
  app.get(["/api/v1/sensors/", "/api/v1/sensors", "/api/v1/sensors/log/", "/api/v1/sensors/log"], (req, res) => {
    const { machine_id } = req.query;
    if (machine_id) {
      const filtered = sensorReadings.filter(s => s.machine_id === Number(machine_id));
      return res.json(filtered);
    }
    res.json(sensorReadings);
  });

  // 1. Sensor Readings Bulk Save
  app.post(["/api/v1/sensors/log/bulk/", "/api/v1/sensors/log/bulk"], (req, res) => {
    const items = Array.isArray(req.body) ? req.body : (req.body ? [req.body] : []);

    if (!items || items.length === 0) {
      return res.status(400).json({ detail: "Array of sensor readings required" });
    }

    const createdReadings: any[] = [];

    for (const item of items) {
      const machine_id = Number(item.machine_id || item.machineId);
      const sensor_type = String(item.sensor_type || item.sensorType || "TEMPERATURE").toUpperCase();
      const value = Number(item.value);
      const unit = String(item.unit || (sensor_type === "TEMPERATURE" ? "C" : sensor_type === "PRESSURE" ? "PSI" : sensor_type === "VIBRATION" ? "mm/s" : "ppm"));

      const is_anomaly = item.is_anomaly !== undefined ? Boolean(item.is_anomaly) : checkIsAnomaly(machine_id, sensor_type, value);

      const record = {
        id: sensorReadings.length + 1,
        machine_id,
        sensor_type,
        value: isNaN(value) ? 0 : value,
        unit,
        is_anomaly,
        timestamp: item.timestamp || new Date().toISOString()
      };

      sensorReadings.push(record);
      createdReadings.push(record);
    }

    res.status(201).json(createdReadings);
  });

  // 2. GET Machine Sensor Ranges
  app.get([
    "/api/v1/sensors/machine/:machine_id/ranges/",
    "/api/v1/sensors/machine/:machine_id/ranges",
    "/api/v1/sensors/machine/:id/ranges/",
    "/api/v1/sensors/machine/:id/ranges"
  ], (req, res) => {
    const machineId = Number(req.params.machine_id || req.params.id);
    if (isNaN(machineId)) {
      return res.status(400).json({ detail: "Invalid machine_id" });
    }

    const result: Record<string, { min: number; max: number; min_value: number; max_value: number }> = {};

    // Standard types
    const standardTypes = ["TEMPERATURE", "PRESSURE", "VIBRATION", "TOXIC_GAS"];
    for (const sType of standardTypes) {
      const range = getRangeForSensor(machineId, sType);
      result[sType] = {
        min: range.min,
        max: range.max,
        min_value: range.min,
        max_value: range.max
      };
    }

    // Custom saved types for this machine
    const savedForMachine = sensorRanges.filter(r => r.machine_id === machineId);
    for (const r of savedForMachine) {
      const sType = r.sensor_type.toUpperCase();
      result[sType] = {
        min: r.min_value,
        max: r.max_value,
        min_value: r.min_value,
        max_value: r.max_value
      };
    }

    res.json(result);
  });

  // POST Machine Sensor Ranges
  app.post([
    "/api/v1/sensors/machine/:machine_id/ranges/",
    "/api/v1/sensors/machine/:machine_id/ranges",
    "/api/v1/sensors/machine/:id/ranges/",
    "/api/v1/sensors/machine/:id/ranges"
  ], (req, res) => {
    const machineId = Number(req.params.machine_id || req.params.id);
    if (isNaN(machineId)) {
      return res.status(400).json({ detail: "Invalid machine_id" });
    }

    const payload = req.body;
    if (!payload || typeof payload !== "object") {
      return res.status(400).json({ detail: "Payload must be an object or array containing sensor ranges" });
    }

    const rangeEntries: { sensor_type: string; min: any; max: any }[] = [];

    if (Array.isArray(payload)) {
      for (const item of payload) {
        if (item && item.sensor_type) {
          const minVal = item.min !== undefined ? item.min : item.min_value;
          const maxVal = item.max !== undefined ? item.max : item.max_value;
          rangeEntries.push({ sensor_type: String(item.sensor_type), min: minVal, max: maxVal });
        }
      }
    } else {
      for (const [sensorType, vals] of Object.entries(payload)) {
        if (vals && typeof vals === "object") {
          const v = vals as any;
          const minVal = v.min !== undefined ? v.min : v.min_value;
          const maxVal = v.max !== undefined ? v.max : v.max_value;
          rangeEntries.push({ sensor_type: sensorType, min: minVal, max: maxVal });
        }
      }
    }

    if (rangeEntries.length === 0) {
      return res.status(400).json({ detail: "No valid sensor ranges provided in payload" });
    }

    // Step 1: Validate all entries
    for (const entry of rangeEntries) {
      const { sensor_type, min, max } = entry;

      if (min === null || min === undefined || max === null || max === undefined || min === "" || max === "") {
        return res.status(400).json({ detail: `min_value and max_value are required for ${sensor_type}` });
      }

      const minNum = Number(min);
      const maxNum = Number(max);

      if (typeof min === "boolean" || typeof max === "boolean" || isNaN(minNum) || isNaN(maxNum)) {
        return res.status(400).json({ detail: `min_value and max_value must be valid numeric values for ${sensor_type}` });
      }

      if (minNum >= maxNum) {
        return res.status(400).json({ detail: `min_value (${minNum}) must be strictly less than max_value (${maxNum}) for ${sensor_type}` });
      }
    }

    // Step 2: Save/Upsert validated ranges
    for (const entry of rangeEntries) {
      const sType = entry.sensor_type.toUpperCase();
      const minNum = Number(entry.min);
      const maxNum = Number(entry.max);

      const existingIdx = sensorRanges.findIndex(r => r.machine_id === machineId && r.sensor_type.toUpperCase() === sType);
      if (existingIdx !== -1) {
        sensorRanges[existingIdx].min_value = minNum;
        sensorRanges[existingIdx].max_value = maxNum;
      } else {
        sensorRanges.push({
          id: sensorRanges.length + 1,
          machine_id: machineId,
          sensor_type: sType,
          min_value: minNum,
          max_value: maxNum
        });
      }
    }

    // Return current saved dictionary for machine
    const responseDict: Record<string, { min: number; max: number; min_value: number; max_value: number }> = {};
    const updatedForMachine = sensorRanges.filter(r => r.machine_id === machineId);
    for (const r of updatedForMachine) {
      responseDict[r.sensor_type] = {
        min: r.min_value,
        max: r.max_value,
        min_value: r.min_value,
        max_value: r.max_value
      };
    }

    res.json(responseDict);
  });

  // Sensor Simulator Telemetry
  app.post("/api/v1/sensors/simulate/:machineId", (req, res) => {
    const machineId = Number(req.params.machineId);
    const forceAnomaly = req.query.force_anomaly === "true";

    const machine = expandMachine(machineId);
    if (!machine) {
      return res.status(404).json({ detail: "Machine not found" });
    }

    const tempRange = getRangeForSensor(machineId, "TEMPERATURE");
    const vibRange = getRangeForSensor(machineId, "VIBRATION");

    const tempVal = forceAnomaly ? (tempRange.max + 25.4) : Math.round((tempRange.min + Math.random() * Math.max(1, tempRange.max - tempRange.min)) * 10) / 10;
    const vibVal = forceAnomaly ? (vibRange.max + 9.8) : Math.round((vibRange.min + Math.random() * Math.max(0.5, vibRange.max - vibRange.min)) * 10) / 10;

    const newReadings = [
      {
        id: sensorReadings.length + 1,
        machine_id: machineId,
        sensor_type: "TEMPERATURE",
        value: tempVal,
        unit: "C",
        is_anomaly: checkIsAnomaly(machineId, "TEMPERATURE", tempVal),
        timestamp: new Date().toISOString()
      },
      {
        id: sensorReadings.length + 2,
        machine_id: machineId,
        sensor_type: "VIBRATION",
        value: vibVal,
        unit: "mm/s",
        is_anomaly: checkIsAnomaly(machineId, "VIBRATION", vibVal),
        timestamp: new Date().toISOString()
      }
    ];

    sensorReadings.push(...newReadings);
    res.json(newReadings);
  });

  // Reset / Clear Sensor Readings for a Machine (removes all historical readings)
  app.delete(["/api/v1/sensors/reset/:machineId", "/api/v1/sensors/reset/:machineId/"], (req, res) => {
    const machineId = Number(req.params.machineId);
    const machine = expandMachine(machineId);
    if (!machine) {
      return res.status(404).json({ detail: "Machine not found" });
    }
    const before = sensorReadings.length;
    // Remove all readings for this machine in-place
    const toRemove = new Set(
      sensorReadings
        .filter(s => s.machine_id === machineId)
        .map(s => s.id)
    );
    let i = sensorReadings.length;
    while (i--) {
      if (toRemove.has(sensorReadings[i].id)) {
        sensorReadings.splice(i, 1);
      }
    }
    res.json({ message: `Cleared ${before - sensorReadings.length} sensor readings for machine ${machineId}`, machine_id: machineId });
  });

  // --- ISSUES MODULE & DUPLICATE DETECTOR ---

  app.get("/api/v1/issues/", (req, res) => {
    const { machine_id, department, priority, worker_id, status } = req.query;

    let filtered = issues;
    if (machine_id && machine_id !== "ALL") {
      filtered = filtered.filter(i => i.machine_id === Number(machine_id));
    }
    if (department && department !== "ALL") {
      filtered = filtered.filter(i => i.department === String(department));
    }
    if (priority && priority !== "ALL") {
      filtered = filtered.filter(i => i.priority === String(priority));
    }
    if (worker_id && worker_id !== "ALL") {
      filtered = filtered.filter(i => i.assigned_worker_id === Number(worker_id));
    }
    if (status && status !== "ALL") {
      filtered = filtered.filter(i => i.status === String(status));
    }

    res.json(filtered.map(expandIssue));
  });

  app.post(["/api/v1/issues/", "/api/v1/issues"], (req, res) => {
    const {
      issue_code,
      title,
      description,
      machine_id,
      department,
      priority,
      status,
      reporter_id,
      assigned_worker_id,
      assigned_supervisor_id,
      due_date
    } = req.body;

    const newIssue = {
      id: issues.length + 1,
      issue_code: issue_code || `ISS-${Math.floor(1000 + Math.random() * 9000)}`,
      title,
      description,
      machine_id: machine_id ? Number(machine_id) : undefined,
      department: department || "PLANT_OPS",
      priority: priority || "MEDIUM",
      status: status || "Open",
      reporter_id: reporter_id ? Number(reporter_id) : undefined,
      assigned_worker_id: assigned_worker_id ? Number(assigned_worker_id) : undefined,
      assigned_supervisor_id: assigned_supervisor_id ? Number(assigned_supervisor_id) : undefined,
      due_date: due_date || new Date(Date.now() + 3 * 86400000).toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      comments: [],
      attachments: [],
      status_history: [
        {
          id: Date.now(),
          issue_id: issues.length + 1,
          changed_by_id: reporter_id ? Number(reporter_id) : undefined,
          from_status: "CREATED",
          to_status: status || "Open",
          notes: "Issue logged via SafeOps portal",
          changed_at: new Date().toISOString()
        }
      ],
      ownership_history: [
        {
          id: Date.now(),
          issue_id: issues.length + 1,
          action_type: "INITIAL_CREATION",
          new_owner_id: assigned_worker_id ? Number(assigned_worker_id) : undefined,
          new_supervisor_id: assigned_supervisor_id ? Number(assigned_supervisor_id) : undefined,
          new_department: department || "PLANT_OPS",
          changed_by_id: reporter_id ? Number(reporter_id) : undefined,
          reason_notes: "Initial creation",
          changed_at: new Date().toISOString()
        }
      ]
    };

    issues.push(newIssue);
    res.status(201).json(expandIssue(newIssue));
  });

  // Duplicate Check Engine Endpoint
  app.post("/api/v1/issues/check-duplicates", (req, res) => {
    const { title, description, machine_id, threshold = 0.55 } = req.body;

    const matches: any[] = [];
    const openIssues = issues.filter(i => ["Open", "In Progress", "Waiting"].includes(i.status));

    for (const issue of openIssues) {
      const titleRatio = stringSimilarity(title, issue.title);
      const descRatio = description && issue.description ? stringSimilarity(description, issue.description) : 0;
      const machineMatch = machine_id && issue.machine_id && Number(machine_id) === issue.machine_id ? 1.0 : (machine_id ? 0.0 : 0.5);

      const compositeScore = Math.round(((titleRatio * 0.55) + (descRatio * 0.30) + (machineMatch * 0.15)) * 1000) / 1000;

      if (compositeScore >= Number(threshold)) {
        const machineObj = expandMachine(issue.machine_id);
        matches.push({
          issue_id: issue.id,
          issue_code: issue.issue_code,
          title: issue.title,
          description: issue.description,
          machine_id: issue.machine_id,
          machine_name: machineObj ? machineObj.name : "Facility General",
          status: issue.status,
          priority: issue.priority,
          created_at: issue.created_at,
          similarity_score: compositeScore,
          similarity_percentage: Math.round(compositeScore * 100)
        });
      }
    }

    matches.sort((a, b) => b.similarity_score - a.similarity_score);
    const topMatch = matches[0] || null;

    res.json({
      is_possible_duplicate: matches.length > 0,
      threshold_used: Number(threshold),
      existing_issue_id: topMatch ? topMatch.issue_id : null,
      existing_issue_code: topMatch ? topMatch.issue_code : null,
      similarity_score: topMatch ? topMatch.similarity_score : 0,
      similarity_percentage: topMatch ? topMatch.similarity_percentage : 0,
      top_match: topMatch,
      all_matches: matches
    });
  });

  // Issue Status Update
  app.put("/api/v1/issues/:id/status", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) {
      return res.status(404).json({ detail: "Issue not found" });
    }

    const { status, notes, changed_by_id, resolution } = req.body;
    const fromStatus = issue.status;
    issue.status = status;
    issue.updated_at = new Date().toISOString();
    if (resolution) {
      issue.resolution = resolution;
      issue.resolution_time = new Date().toISOString();
    }

    issue.status_history.push({
      id: Date.now(),
      issue_id: issueId,
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      from_status: fromStatus,
      to_status: status,
      notes: notes || `Status updated from ${fromStatus} to ${status}`,
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  // Issue Comments
  app.post("/api/v1/issues/:id/comments", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) {
      return res.status(404).json({ detail: "Issue not found" });
    }

    const { comment_text, author_name, author_id } = req.body;
    const newComment = {
      id: Date.now(),
      issue_id: issueId,
      author_id: author_id ? Number(author_id) : undefined,
      author_name: author_name || "System User",
      comment_text,
      created_at: new Date().toISOString()
    };

    issue.comments.push(newComment);
    res.status(201).json(newComment);
  });

  // Issue Attachments
  app.post("/api/v1/issues/:id/attachments", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) {
      return res.status(404).json({ detail: "Issue not found" });
    }

    const { file_name, file_url, file_type } = req.body;
    const newAttachment = {
      id: Date.now(),
      issue_id: issueId,
      file_name,
      file_url,
      file_type: file_type || "document",
      uploaded_at: new Date().toISOString()
    };

    issue.attachments.push(newAttachment);
    res.status(201).json(newAttachment);
  });

  // Ownership Module Actions
  app.post("/api/v1/issues/:id/assign-owner", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return res.status(404).json({ detail: "Issue not found" });

    const { assigned_worker_id, changed_by_id, notes } = req.body;
    const prevOwner = issue.assigned_worker_id;
    issue.assigned_worker_id = Number(assigned_worker_id);
    issue.updated_at = new Date().toISOString();

    issue.ownership_history.push({
      id: Date.now(),
      issue_id: issueId,
      action_type: "ASSIGN_OWNER",
      previous_owner_id: prevOwner,
      new_owner_id: Number(assigned_worker_id),
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      reason_notes: notes || "Assigned owner",
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  app.post("/api/v1/issues/:id/transfer-ownership", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return res.status(404).json({ detail: "Issue not found" });

    const { new_owner_id, changed_by_id, reason } = req.body;
    const prevOwner = issue.assigned_worker_id;
    issue.assigned_worker_id = Number(new_owner_id);
    issue.updated_at = new Date().toISOString();

    issue.ownership_history.push({
      id: Date.now(),
      issue_id: issueId,
      action_type: "TRANSFER_OWNERSHIP",
      previous_owner_id: prevOwner,
      new_owner_id: Number(new_owner_id),
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      reason_notes: reason,
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  app.post("/api/v1/issues/:id/reassign-department", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return res.status(404).json({ detail: "Issue not found" });

    const { new_department, new_owner_id, new_supervisor_id, changed_by_id, reason } = req.body;
    const prevDept = issue.department;
    issue.department = new_department;
    if (new_owner_id) issue.assigned_worker_id = Number(new_owner_id);
    if (new_supervisor_id) issue.assigned_supervisor_id = Number(new_supervisor_id);
    issue.updated_at = new Date().toISOString();

    issue.ownership_history.push({
      id: Date.now(),
      issue_id: issueId,
      action_type: "REASSIGN_DEPARTMENT",
      previous_department: prevDept,
      new_department,
      new_owner_id: new_owner_id ? Number(new_owner_id) : undefined,
      new_supervisor_id: new_supervisor_id ? Number(new_supervisor_id) : undefined,
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      reason_notes: reason,
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  app.post("/api/v1/issues/:id/escalate", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return res.status(404).json({ detail: "Issue not found" });

    const { new_supervisor_id, new_owner_id, changed_by_id, reason, boost_priority } = req.body;
    const prevSupervisor = issue.assigned_supervisor_id;
    if (new_supervisor_id) issue.assigned_supervisor_id = Number(new_supervisor_id);
    if (new_owner_id) issue.assigned_worker_id = Number(new_owner_id);
    if (boost_priority) issue.priority = "CRITICAL";
    issue.updated_at = new Date().toISOString();

    issue.ownership_history.push({
      id: Date.now(),
      issue_id: issueId,
      action_type: "ESCALATE",
      previous_supervisor_id: prevSupervisor,
      new_supervisor_id: new_supervisor_id ? Number(new_supervisor_id) : undefined,
      new_owner_id: new_owner_id ? Number(new_owner_id) : undefined,
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      reason_notes: reason,
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  app.post("/api/v1/issues/:id/close", (req, res) => {
    const issueId = Number(req.params.id);
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return res.status(404).json({ detail: "Issue not found" });

    const { resolution, changed_by_id, notes } = req.body;
    const prevStatus = issue.status;
    issue.status = "Closed";
    issue.resolution = resolution;
    issue.resolution_time = new Date().toISOString();
    issue.updated_at = new Date().toISOString();

    issue.status_history.push({
      id: Date.now(),
      issue_id: issueId,
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      from_status: prevStatus,
      to_status: "Closed",
      notes: notes || `Resolved and closed: ${resolution}`,
      changed_at: new Date().toISOString()
    });

    issue.ownership_history.push({
      id: Date.now(),
      issue_id: issueId,
      action_type: "CLOSE_ISSUE",
      changed_by_id: changed_by_id ? Number(changed_by_id) : undefined,
      reason_notes: resolution,
      changed_at: new Date().toISOString()
    });

    res.json(expandIssue(issue));
  });

  // --- VITE MIDDLEWARE ---
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`SafeOps AI Platform server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
