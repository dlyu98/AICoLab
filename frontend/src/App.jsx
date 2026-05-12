import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, ClipboardList, FileText, HeartPulse, ShieldCheck } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const disclaimer = 'Clinical decision support only. Not a substitute for professional medical judgment.';

function Panel({ title, children }) { return <section className="panel"><h2>{title}</h2>{children}</section>; }
function Badge({ tier }) { return <span className={`badge ${tier || 'neutral'}`}>{tier || 'not scored'}</span>; }
function JsonPanel({ data }) { return <pre className="json">{data ? JSON.stringify(data, null, 2) : 'Run a workflow to see structured output.'}</pre>; }

function App() {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState('SYN-1001');
  const [note, setNote] = useState('Synthetic note: patient reports dyspnea and edema. Follow-up with cardiology recommended.');
  const [question, setQuestion] = useState('Suggest SQL for a readmission dashboard.');
  const [result, setResult] = useState(null);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetch(`${API}/patients`).then(r => r.json()).then(setPatients).catch(() => setPatients([])); loadAudit(); }, []);
  async function loadAudit() { fetch(`${API}/audit-logs`).then(r => r.json()).then(setAudit).catch(() => setAudit([])); }
  async function post(path, body) { setLoading(true); const res = await fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); const data = await res.json(); setResult(data); setLoading(false); loadAudit(); }

  const base = { patient_id: patientId, note, user_id: 'demo-clinician', role: 'clinician' };
  return <main>
    <div className="banner"><ShieldCheck size={18}/>{disclaimer}</div>
    <header className="hero"><div><p className="eyebrow">CareBridge AI Agent</p><h1>HIPAA-aware clinical AI decision-support workspace</h1><p>Reason over synthetic patient data, care gaps, readmission risk, notes, and healthcare operations with source evidence and human-in-the-loop safeguards.</p></div><HeartPulse className="heroIcon" size={72}/></header>
    <section className="grid top">
      <Panel title="Dashboard"><div className="cards"><div><Activity/>Patient Summary</div><div><ClipboardList/>Care Gaps</div><div><HeartPulse/>Readmission Risk</div><div><FileText/>Note Extraction</div></div></Panel>
      <Panel title="Patient selector"><label>Synthetic patient</label><select value={patientId} onChange={e=>setPatientId(e.target.value)}>{patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.display_name} ({p.patient_id})</option>)}</select><small>No real PHI is included or required.</small></Panel>
    </section>
    <section className="grid">
      <Panel title="Clinical note input"><textarea value={note} onChange={e=>setNote(e.target.value)} /><div className="buttons"><button onClick={()=>post('/agent/patient-summary', base)}>Run Patient Summary</button><button onClick={()=>post('/agent/care-gaps', base)}>Run Care Gaps</button><button onClick={()=>post('/agent/readmission-risk', base)}>Run Readmission Risk</button><button onClick={()=>post('/agent/note-extraction', base)}>Run Note Extraction</button><button onClick={()=>post('/redact-phi', { text: note })}>Redact PHI</button></div></Panel>
      <Panel title="Healthcare Operations Copilot"><textarea value={question} onChange={e=>setQuestion(e.target.value)} /><button onClick={()=>post('/agent/ask', { question, user_id: 'demo-analyst', role: 'analyst' })}>Ask Operations Copilot</button><p className="hint">Generates cohort logic, data-quality notes, and SQL suggestions for synthetic datasets.</p></Panel>
    </section>
    <section className="grid">
      <Panel title="Agent response"><div className="summary"><Badge tier={result?.risk_tier}/><strong>{loading ? 'Running...' : result?.agent_name || 'No workflow run yet'}</strong></div><p>{result?.summary || 'Outputs separate extracted facts from suggestions and require human review.'}</p><div className="list">{result?.findings?.map((f, i) => <article key={i}><b>{f.label}</b><span>{f.category} · {f.priority || 'n/a'} · confidence {f.confidence}</span><p>{f.reason}</p></article>)}</div></Panel>
      <Panel title="Structured output panels"><JsonPanel data={result}/></Panel>
    </section>
    <section className="grid">
      <Panel title="Admin / Audit Logs"><button onClick={loadAudit}>Refresh audit logs</button><JsonPanel data={audit}/></Panel>
      <Panel title="Settings"><ul><li>Model provider: local rule-based fallback by default.</li><li>API base URL: {API}</li><li>Human review required for clinical recommendations.</li><li>Prompt injection text in notes is treated as data, not instructions.</li></ul></Panel>
    </section>
  </main>;
}

createRoot(document.getElementById('root')).render(<App />);
