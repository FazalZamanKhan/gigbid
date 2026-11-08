import { useEffect, useState, type ReactNode } from 'react'

type Job = { id: string; title: string; description: string; skills: string[]; budget_min: number; budget_max: number; connects_cost: number; client_rating: number }
type Evidence = { id: string; title: string; source: string; text: string }
type Run = { run_id: string; status: string; state: { job?: Job; risk?: { score: number; flags: string[] }; fit?: { score: number; evidence: Evidence[]; missing_skills: string[] }; decision?: { action: string; reason: string }; price?: { amount: number; rationale: string }; draft?: { text: string; claims: { text: string; evidence_ids: string[]; supported: boolean }[] }; events?: string[]; approval?: { approved: boolean; reason?: string }; marketplace_result?: { draft_id: string } } }
type ConversationRun = { run_id: string; status: string; state: { job?: Job; incoming?: string; intent?: string; risk_flags?: string[]; slots?: string[]; draft?: { text: string }; events?: string[]; approval?: { approved: boolean; reason?: string }; marketplace_result?: { message_id?: string } } }

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
  const [incoming, setIncoming] = useState('Could we schedule an interview for this project?')
  const [conversation, setConversation] = useState<ConversationRun | null>(null)
  const [replyEdit, setReplyEdit] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api<Job[]>('/jobs').then(setJobs).catch(e => setError(e.message))
    const previousRun = localStorage.getItem('gigbid:last-run')
    if (previousRun) {
      api<Run>(`/runs/${previousRun}`).then(result => {
        setRun(result)
        setSelected(result.state.job || null)
        setEdit(result.state.draft?.text || '')
      }).catch(() => localStorage.removeItem('gigbid:last-run'))
    }
    const previousConversation = localStorage.getItem('gigbid:last-conversation')
    if (previousConversation) {
      api<ConversationRun>(`/conversations/${previousConversation}`).then(result => {
        setConversation(result)
        setReplyEdit(result.state.draft?.text || '')
      }).catch(() => localStorage.removeItem('gigbid:last-conversation'))
    }
  }, [])

  async function analyse(job: Job) {
    setSelected(job); setRun(null); setError(''); setBusy(true)
    try {
      const result = await api<Run>(`/jobs/${job.id}/runs`, { method: 'POST' })
      setRun(result); setEdit(result.state.draft?.text || '')
      localStorage.setItem('gigbid:last-run', result.run_id)
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

  async function startConversation() {
    if (!selected || !incoming.trim()) return
    setBusy(true); setError(''); setConversation(null)
    try {
      const result = await api<ConversationRun>(`/jobs/${selected.id}/conversations`, { method: 'POST', body: JSON.stringify({ incoming }) })
      setConversation(result); setReplyEdit(result.state.draft?.text || '')
      localStorage.setItem('gigbid:last-conversation', result.run_id)
    } catch (e) { setError((e as Error).message) } finally { setBusy(false) }
  }

  async function respondConversation(approved: boolean) {
    if (!conversation) return
    setBusy(true); setError('')
    try {
      const result = await api<ConversationRun>(`/conversations/${conversation.run_id}/approval`, { method: 'POST', body: JSON.stringify({ approved, text: replyEdit, reason: approved ? undefined : 'Rejected in messages' }) })
      setConversation(result)
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
        <a href="#messages">✉ <span>Messages</span></a>
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
        <section id="messages" className="messages"><div className="section-head"><div><h2>Client messages</h2><p>Run a synthetic client reply through the Workspace MCP calendar and approval gate</p></div></div>
          <div className="message-grid"><div><label htmlFor="incoming">Incoming client message</label><textarea id="incoming" rows={4} value={incoming} onChange={e => setIncoming(e.target.value)} /><button className="primary" onClick={startConversation} disabled={busy || !selected || !incoming.trim()}>Prepare reply for selected job</button><small>{selected ? `Selected: ${selected.title}` : 'Select a job above first.'}</small></div>
            <div aria-live="polite">{!conversation ? <p className="empty">The reply and its approval status will appear here.</p> : <><div className="message-summary"><Pill tone="amber">{conversation.state.intent || 'pending'}</Pill>{conversation.state.slots?.length ? <span>Calendar slots: {conversation.state.slots.join(' · ')}</span> : null}</div>{conversation.state.risk_flags?.length ? <div className="warning">Reply blocked: {conversation.state.risk_flags.join(', ')}</div> : null}{conversation.state.draft && <><label htmlFor="reply">Reply draft</label><textarea id="reply" rows={5} value={replyEdit} onChange={e => setReplyEdit(e.target.value)} disabled={conversation.status !== 'awaiting_approval'} />{conversation.status === 'awaiting_approval' && <div className="actions"><button className="secondary" onClick={() => respondConversation(false)} disabled={busy}>Reject</button><button className="primary" onClick={() => respondConversation(true)} disabled={busy}>Approve message</button></div>}{conversation.state.approval && <div className={conversation.state.approval.approved ? 'success' : 'warning'}>{conversation.state.approval.approved ? `Approved synthetic message recorded: ${conversation.state.marketplace_result?.message_id || 'pending'}` : conversation.state.approval.reason}</div>}</>}<div className="subsection"><h3>Conversation timeline</h3><ol className="timeline">{conversation.state.events?.map((event, index) => <li key={`${event}-${index}`}>{event}</li>)}</ol></div></>}</div></div>
        </section>
        <footer>GigBid development build · Synthetic data · No live marketplace actions</footer>
      </div>
    </main>
  </div>
}
