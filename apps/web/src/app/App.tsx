import { useEffect, useState, type ReactNode } from 'react'

type Job = { id: string; title: string; description: string; skills: string[]; budget_min: number; budget_max: number; connects_cost: number; client_rating: number }
type Evidence = { id: string; title: string; source: string; text: string }
type Run = { run_id: string; status: string; state: { job?: Job; risk?: { score: number; flags: string[] }; fit?: { score: number; evidence: Evidence[]; missing_skills: string[] }; decision?: { action: string; reason: string }; price?: { amount: number; rationale: string }; draft?: { text: string; claims: { text: string; evidence_ids: string[]; supported: boolean }[] }; events?: string[]; approval?: { approved: boolean; reason?: string }; marketplace_result?: { draft_id: string } } }

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) throw new Error((await response.json()).detail || `Request failed: ${response.status}`)
  return response.json()
}

function Pill({ children, tone = 'neutral' }: { children: ReactNode; tone?: string }) {
  return <span className={`pill pill-${tone}`}>{children}</span>
}

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selected, setSelected] = useState<Job | null>(null)
  const [run, setRun] = useState<Run | null>(null)
  const [edit, setEdit] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { api<Job[]>('/jobs').then(setJobs).catch(e => setError(e.message)) }, [])

  async function analyse(job: Job) {
    setSelected(job); setRun(null); setError(''); setBusy(true)
    try {
      const result = await api<Run>(`/jobs/${job.id}/runs`, { method: 'POST' })
      setRun(result); setEdit(result.state.draft?.text || '')
    } catch (e) { setError((e as Error).message) } finally { setBusy(false) }
  }

  async function respond(approved: boolean) {
    if (!run) return
    setBusy(true); setError('')
    try {
      const result = await api<Run>(`/runs/${run.run_id}/approval`, { method: 'POST', body: JSON.stringify({ approved, text: edit, reason: approved ? undefined : 'Rejected in studio' }) })
      setRun(result)
    } catch (e) { setError((e as Error).message) } finally { setBusy(false) }
  }

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">G</span><span>GigBid<small>FREELANCER COPILOT</small></span></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav aria-label="Main navigation">
        <a className="nav-active" href="#inbox">▦ <span>Job inbox</span><b>{jobs.length}</b></a>
        <a href="#run">◉ <span>Agent run</span></a>
        <a href="#studio">✎ <span>Proposal studio</span></a>
      </nav>
      <div className="side-bottom"><div className="avatar">FZ</div><div><strong>Development demo</strong><small>Synthetic local data</small></div></div>
    </aside>

    <main>
      <header><div className="eyebrow">WORKSPACE / JOB INBOX</div><Pill tone="amber">Pre-starter build</Pill></header>
      <div className="content">
        <section className="hero"><div><div className="eyebrow">YOUR OPPORTUNITIES</div><h1>Make every bid count.</h1><p>Review fit, risk, and portfolio evidence before you spend a Connect or send a proposal.</p></div><div className="hero-number"><strong>{jobs.length}</strong><span>demo jobs</span></div></section>
        {error && <div className="error" role="alert">{error}</div>}
        <div className="columns">
          <section id="inbox" className="inbox"><div className="section-head"><div><h2>Job inbox</h2><p>Local synthetic examples until GigSim arrives</p></div><span>{jobs.length} jobs</span></div>
            {jobs.length === 0 && !error && <p className="empty">Loading jobs…</p>}
            {jobs.map(job => <button className={`job-card ${selected?.id === job.id ? 'selected' : ''}`} key={job.id} onClick={() => analyse(job)} disabled={busy}>
              <div className="job-top"><strong>{job.title}</strong><span>↗</span></div><p>{job.description}</p><div className="tags">{job.skills.map(skill => <span key={skill}>{skill}</span>)}</div><div className="job-meta"><span>${job.budget_min}–${job.budget_max}</span><span>★ {job.client_rating}</span><span>{job.connects_cost} Connects</span></div>
            </button>)}
          </section>
          <section className="detail" aria-live="polite"><div className="section-head"><div><h2>Decision desk</h2><p>{selected ? selected.title : 'Choose a job to analyse'}</p></div></div>
            {!run && <div className="empty-state"><div className="empty-icon">◎</div><h3>{busy ? 'Analysing job…' : 'Select an opportunity'}</h3><p>{busy ? 'The agent is checking requirements, risk, and evidence.' : 'Open a job to see a traceable bid decision and review its proposal.'}</p></div>}
            {run && <div className="run-body">
              <div className="score-row"><div><span>Portfolio fit</span><strong>{Math.round((run.state.fit?.score || 0) * 100)}%</strong></div><div><span>Risk score</span><strong>{Math.round((run.state.risk?.score || 0) * 100)}%</strong></div><div><span>Action</span><strong>{run.state.decision?.action.toUpperCase()}</strong></div></div>
              <p className="decision-reason">{run.state.decision?.reason}</p>
              {run.state.risk?.flags.length ? <div className="warning">Risk signals: {run.state.risk.flags.join(', ')}</div> : null}
              <div className="subsection"><h3>Portfolio evidence</h3>{run.state.fit?.evidence.length ? run.state.fit.evidence.map(item => <div className="evidence" key={item.id}><strong>{item.title}</strong><p>{item.text}</p><small>{item.id} · {item.source}</small></div>) : <p>No supporting evidence found.</p>}</div>
              {run.state.draft && <div id="studio" className="subsection"><h3>Proposal studio</h3><label htmlFor="draft">Draft</label><textarea id="draft" value={edit} onChange={e => setEdit(e.target.value)} disabled={run.status !== 'awaiting_approval'} rows={7}/><small>Changes are held for claim and compliance review in this development build.</small>
                {run.status === 'awaiting_approval' && <div className="actions"><button className="secondary" onClick={() => respond(false)} disabled={busy}>Reject</button><button className="primary" onClick={() => respond(true)} disabled={busy}>Approve draft</button></div>}
                {run.state.approval && <div className={run.state.approval.approved ? 'success' : 'warning'}>{run.state.approval.approved ? `Approved draft created: ${run.state.marketplace_result?.draft_id || 'pending'}` : run.state.approval.reason}</div>}
              </div>}
              <div id="run" className="subsection"><h3>Run timeline</h3><ol className="timeline">{run.state.events?.map((event, index) => <li key={`${event}-${index}`}>{event}</li>)}</ol></div>
            </div>}
          </section>
        </div>
        <footer>GigBid development build · Synthetic data · No live marketplace actions</footer>
      </div>
    </main>
  </div>
}
