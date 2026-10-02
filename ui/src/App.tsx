import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { ApprovalGate } from '../vendor/tun-design/ApprovalGate';
import { ActionReceipt } from '../vendor/tun-design/ActionReceipt';
import type { ActionProposal, ApprovalStatus, ReceiptData, DecisionRequest } from '../vendor/tun-design/contracts';
import '../vendor/tun-design/styles.css';
import './style.css';

export interface View {
  viewVersion: 'tse-design-view/0.2';
  csrfToken: string;
  proposals: { proposal: ActionProposal; status: ApprovalStatus; operationId: string | null }[];
  budget: { configured: boolean; limit: number | null; used: number; remaining: number };
  controls: { id: string; operationId: string; requestedVersion: string; outcome: 'effective' | 'too-late' | 'stale'; observedState: string }[];
  operations: { id: string; version: string; state: string; action: string; actionType: string;
    originalId: string | null; hostStatus: string; dispatchObservation: string; receipt: ReceiptData | null }[];
  resources: { rootId: string; target: string; revision: number; status: 'active' | 'withdrawn'; content: string }[];
}

async function responseView(response: Response): Promise<View> {
  const body = await response.json();
  if (!response.ok) throw new Error(typeof body.error === 'string' ? body.error : 'Request failed; refresh history.');
  if (body.viewVersion !== 'tse-design-view/0.2' || typeof body.csrfToken !== 'string' ||
      !Array.isArray(body.proposals) || !Array.isArray(body.operations) || !Array.isArray(body.resources) ||
      !Array.isArray(body.controls) || !body.budget || typeof body.budget.remaining !== 'number') {
    throw new Error('Unsupported server view. No action was inferred from this response.');
  }
  return body as View; // Same-origin fixture host projection; not an authorization boundary.
}

type Perform = (path: string, payload: object) => Promise<void>;

export function OperationPanel({ item, busy, remaining, loseResponse, perform }: {
  item: View['operations'][number]; busy: boolean; remaining: number; loseResponse: boolean; perform: Perform;
}) {
  const queued = item.state === 'reserved';
  return <article>
    {item.receipt ? <ActionReceipt receipt={item.receipt} /> : <div className="resource">
      <h3>{item.action}</h3>
      <p>{queued ? 'Queued — not dispatched' : item.state === 'cancelled' ? 'Cancelled before dispatch' : 'Dispatch blocked'}</p>
      <p>No effectful provider call was made for this operation.</p>
      {item.dispatchObservation === 'budget-exhausted' && <p>The host dispatch budget was missing or exhausted.</p>}
    </div>}
    <p className="lineage">Operation {item.id} · revision {item.version}</p>
    {item.originalId && <p className="lineage">Recovery for operation {item.originalId}. Original history is preserved.</p>}
    {queued ? <div className="buttons">
      <button disabled={busy || remaining <= 0} onClick={() => {
        void perform('/api/dispatch', { operationId: item.id, loseResponse }).catch(() => {});
      }}>Dispatch queued action</button>
      <button disabled={busy} onClick={() => {
        void perform('/api/cancel', { operationId: item.id, operationVersion: item.version }).catch(() => {});
      }}>Cancel queued action</button>
    </div> : item.receipt && <button disabled={busy} onClick={() => {
      void perform('/api/reconcile', { operationId: item.id }).catch(() => {});
    }}>Reconcile operation</button>}
    {queued && remaining <= 0 && <p>Dispatch budget exhausted. Cancellation and readback remain available.</p>}
  </article>;
}

function ResourceCard({ resource, allowed, busy, perform }: {
  resource: View['resources'][number]; allowed: boolean; busy: boolean; perform: Perform;
}) {
  const [correction, setCorrection] = useState(resource.content);
  async function prepare(event: FormEvent) {
    event.preventDefault();
    await perform('/api/recovery', { originalId: resource.rootId, action: 'correct', content: correction });
  }
  return <article className="resource">
    <div className="section-line"><h3>{resource.target}</h3><span>{resource.status} · revision {resource.revision}</span></div>
    <p className="lineage">Publication {resource.rootId}</p>
    {resource.status === 'active' ? <>
      <p className="content">{resource.content}</p>
      <form onSubmit={event => { void prepare(event).catch(() => {}); }}>
        <label htmlFor={'correction-' + resource.rootId}>Proposed correction</label>
        <textarea id={'correction-' + resource.rootId} value={correction} maxLength={4096}
          onChange={event => setCorrection(event.target.value)} disabled={busy} />
        <div className="buttons">
          <button disabled={busy || !allowed || !correction.trim()}>Prepare correction for review</button>
          <button type="button" disabled={busy || !allowed}
            onClick={() => { void perform('/api/recovery', { originalId: resource.rootId, action: 'withdraw', content: null }).catch(() => {}); }}>
            Prepare withdrawal for review
          </button>
        </div>
      </form>
      {!allowed && <p>Verify the original publication before preparing recovery.</p>}
    </> : <p>Withdrawn from the active board. Historical records remain; this is not deletion or undo.</p>}
  </article>;
}

export function App() {
  const [view, setView] = useState<View | null>(null);
  const [draft, setDraft] = useState('Synthetic project update: ready for review.');
  const [loseResponse, setLoseResponse] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const lock = useRef(false);

  useEffect(() => {
    const abort = new AbortController();
    void fetch('/api/state', { signal: abort.signal }).then(responseView).then(setView).catch(cause => {
      if (!abort.signal.aborted) setError(String(cause));
    });
    return () => abort.abort();
  }, []);

  async function perform(path: string, payload?: object) {
    if (lock.current) throw new Error('Wait for the pending request.');
    lock.current = true; setBusy(true); setError('');
    try {
      const response = await fetch(path, payload === undefined ? {} : {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TUN-CSRF': view?.csrfToken ?? '' },
        body: JSON.stringify(payload),
      });
      setView(await responseView(response));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Outcome may be unknown. Refresh history.');
      throw cause;
    } finally {
      lock.current = false; setBusy(false);
    }
  }

  async function decide(request: DecisionRequest) {
    await perform('/api/decision', request);
  }

  return <>
    <header><div className="brand">TUN <span>Systemic Engineering</span></div><span className="tag">Local fixture · v0.3</span></header>
    <main>
      <section className="intro"><p className="eyebrow">THE ACTION CONTRACT</p><h1>Review. Execute. Verify.</h1>
        <p>Approval records a decision. The host enforces permission. Evidence establishes what happened.</p>
        <p className="notice">Synthetic data and fixture identity only. Nothing is published to an external service.</p>
      </section>
      <div className="toolbar">
        <button disabled={busy} onClick={() => { void perform('/api/state').catch(() => {}); }}>Refresh history</button>
        <label className="check"><input type="checkbox" checked={loseResponse} disabled={busy}
          onChange={event => setLoseResponse(event.target.checked)} /> Simulate a lost provider response</label>
        <span role="status" aria-live="polite">{busy ? 'Waiting for the host…' : 'No automatic execution or replay'}</span>
      </div>
      {error && <p className="error" role="alert">{error} Refresh history before attempting further work.</p>}
      {!view ? <p role="status">Loading the local host…</p> : <>
        <section aria-labelledby="budget-title" className="draft-panel">
          <h2 id="budget-title">Dispatch budget</h2>
          <p role="status">{view.budget.used} of {view.budget.limit ?? 'unconfigured'} dispatch slots consumed · {view.budget.remaining} remaining</p>
          <p>Shared across this fixture actor's publications and recovery actions. No automatic reset or refund; this is not a money or token budget.</p>
          <p>Cancellation only prevents queued work from crossing the dispatch boundary. It cannot stop an accepted provider operation.</p>
        </section>
        <section aria-labelledby="draft-title" className="draft-panel">
          <h2 id="draft-title">1. Prepare a publication</h2>
          <form onSubmit={event => { event.preventDefault(); void perform('/api/proposals', { content: draft }).catch(() => {}); }}>
            <label htmlFor="publication-content">Publication content</label>
            <textarea id="publication-content" maxLength={4096} value={draft} disabled={busy}
              onChange={event => setDraft(event.target.value)} />
            <button className="primary" disabled={busy || !draft.trim()}>Prepare publication for review</button>
          </form>
        </section>
        <section aria-labelledby="review-title"><h2 id="review-title">2. Review and authorize</h2>
          {!view.proposals.length && <p className="empty">Prepared actions appear here. Preparing does not approve or execute them.</p>}
          <div className="cards">{view.proposals.map(item => <div key={item.proposal.id + ':' + item.proposal.version}>
            <ApprovalGate proposal={item.proposal} status={item.status} approveLabel={'Approve: ' + item.proposal.action.toLowerCase()}
              onDecision={decide} blockedReason={busy ? 'Another host request is pending.' : undefined} />
            {item.status === 'approved' && !item.operationId && <button className="execute" disabled={busy}
              onClick={() => { void perform('/api/reserve', { proposalId: item.proposal.id, proposalVersion: item.proposal.version }).catch(() => {}); }}>
              Queue approved action
            </button>}
          </div>)}</div>
        </section>
        <section aria-labelledby="history-title"><h2 id="history-title">3. Inspect evidence and history</h2>
          {!view.operations.length && <p className="empty">An approval is not an action receipt. Queue an approved proposal to begin an operation.</p>}
          <div className="cards">{view.operations.map(item => <OperationPanel key={item.id} item={item}
            busy={busy} remaining={view.budget.remaining} loseResponse={loseResponse} perform={perform} />)}</div>
        </section>
        <section aria-labelledby="controls-title"><h2 id="controls-title">Cancellation evidence</h2>
          {!view.controls.length && <p className="empty">Cancellation results appear here, separately from action receipts.</p>}
          {view.controls.map(control => <article key={control.id} className="resource">
            <h3>{control.outcome === 'effective' ? 'Cancellation effective before dispatch' :
              control.outcome === 'stale' ? 'Stale cancellation — no action taken' : 'Cancellation too late — no action taken'}</h3>
            <p className="lineage">Operation {control.operationId} · requested revision {control.requestedVersion}</p>
            <p>Observed operation state: {control.observedState}. No restoration of earlier effects is claimed.</p>
          </article>)}
        </section>
        <section aria-labelledby="board-title"><h2 id="board-title">Current provider board</h2>
          <p>The board shows current local state. Receipts above describe historical operation outcomes.</p>
          {!view.resources.length && <p className="empty">No publication exists yet.</p>}
          {view.resources.map(resource => <ResourceCard key={resource.rootId + ':' + resource.revision}
            resource={resource} busy={busy} perform={perform}
            allowed={view.operations.some(op => op.id === resource.rootId && op.hostStatus === 'completed')} />)}
        </section>
      </>}
      <footer>Experimental host and provider · Real TUN design components · No production-readiness or full accessibility claim</footer>
    </main>
  </>;
}

if (typeof document !== 'undefined') {
  const root = document.getElementById('root');
  if (root) createRoot(root).render(<App />);
}
