'use client';
import { useEffect, useId, useRef, useState } from 'react';
import { consequenceLabels, displayTimestamp, parseTimestamp, proposalBlockReason,
  proposalFingerprint, recoveryLabels, type ActionProposal, type ApprovalStatus,
  type DecisionRequest } from './contracts.js';

export interface ApprovalGateProps {
  proposal: ActionProposal;
  status: ApprovalStatus;
  /** Use a concrete action label, for example "Send email", never "Continue". */
  approveLabel: string;
  onDecision(request: DecisionRequest): void | Promise<void>;
  blockedReason?: string;
  className?: string;
}
/** A new proposal version starts a new review. A rerender cannot silently reset it. */
export function ApprovalGate(props: ApprovalGateProps) {
  return <ApprovalReview key={JSON.stringify([props.proposal.id, props.proposal.version])} {...props} />;
}
function ApprovalReview({ proposal, status, approveLabel, onDecision, blockedReason, className = '' }: ApprovalGateProps) {
  const id = useId();
  const [snapshot] = useState(() => proposalFingerprint(proposal));
  const [clock, setClock] = useState<number | null>(null);
  const [phase, setPhase] = useState<'idle' | 'pending' | 'submitted' | 'unknown'>('idle');
  const [localBlock, setLocalBlock] = useState('');
  const lock = useRef(false);
  const changed = snapshot !== proposalFingerprint(proposal);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const expires = proposal.expiresAt ? parseTimestamp(proposal.expiresAt) : null;
    const update = () => {
      const now = Date.now();
      setClock(now);
      if (expires !== null && expires > now) timer = setTimeout(update, Math.min(expires - now + 1, 2147483647));
    };
    update();
    return () => { if (timer !== undefined) clearTimeout(timer); };
  }, [proposal.expiresAt]);
  const reason = blockedReason || localBlock || (changed
    ? 'Proposal changed without a new version. Request a fresh proposal.'
    : proposalBlockReason(proposal, clock ?? 0)) ||
    (!approveLabel.trim() ? 'An explicit action label is required.' : '');
  const unavailable = status !== 'awaiting' || phase !== 'idle' || Boolean(reason) ||
    (proposal.expiresAt !== undefined && clock === null);
  async function decide(decision: DecisionRequest['decision']) {
    if (lock.current || unavailable) return;
    // Do not depend solely on the timer: background tabs can throttle it.
    const latestReason = proposalBlockReason(proposal, Date.now());
    if (latestReason) { setLocalBlock(latestReason); return; }
    lock.current = true;
    setPhase('pending');
    try {
      await onDecision({ proposalId: proposal.id, proposalVersion: proposal.version, decision });
      setPhase('submitted');
    } catch {
      // An error could be a lost acknowledgement after execution. Never auto-retry.
      setPhase('unknown');
    }
    // Deliberately keep the latch closed. Only a new proposal version resets it.
  }
  const statusText = reason || (phase === 'unknown'
    ? 'Decision outcome is unknown. Check the action history; do not submit it again.'
    : phase === 'pending' ? 'Submitting decision. Execution is not confirmed.'
    : status === 'approved' ? 'Approved. Execution is not confirmed by this gate.'
    : status === 'rejected' ? 'Rejected. This gate will not request execution.'
    : status === 'expired' ? 'Expired. Request a fresh proposal.'
    : status === 'superseded' ? 'Superseded by another proposal.'
    : phase === 'submitted' ? 'Decision submitted. Waiting for the application to confirm its state.'
    : 'Review the complete action before deciding.');
  return <section className={`tun-component tun-approval ${className}`} aria-labelledby={`${id}-title`}>
    <div className="tun-row tun-row-top">
      <div><p className="tun-eyebrow">Proposed action · not an action receipt</p><h2 className="tun-heading" id={`${id}-title`}>{proposal.action}</h2></div>
      <span className="tun-badge" style={{ color: `var(--tun-state-consequence-${proposal.consequence.toLowerCase()})` }}>
        {proposal.consequence} · {consequenceLabels[proposal.consequence]}
      </span>
    </div>
    <dl className="tun-facts">
      <div><dt>Actor</dt><dd>{proposal.actor.name} ({proposal.actor.type})</dd></div>
      <div><dt>Target</dt><dd>{proposal.target}</dd></div>
      <div><dt>Effect</dt><dd>{proposal.effect}</dd></div>
      <div><dt>Authority requested</dt><dd>{proposal.authority}</dd></div>
      <div><dt>Recovery</dt><dd><strong>{recoveryLabels[proposal.recovery.kind]}.</strong> {proposal.recovery.description}</dd></div>
      {proposal.expiresAt && <div><dt>Expires</dt><dd>{displayTimestamp(proposal.expiresAt)}</dd></div>}
      {proposal.reviewBasis && <>
        <div><dt>Context basis</dt><dd>{proposal.reviewBasis.context.id} · version {proposal.reviewBasis.context.version}</dd></div>
        <div><dt>Plan basis</dt><dd>{proposal.reviewBasis.plan.id} · version {proposal.reviewBasis.plan.version}</dd></div>
      </>}
    </dl>
    {proposal.contentPreview !== undefined && <div className="tun-preview"><h3 className="tun-subheading">Content preview</h3><p className="tun-preserve-text">{proposal.contentPreview}</p></div>}
    <div className="tun-notice" role="status" aria-live="polite" id={`${id}-status`}>{statusText}</div>
    <div className="tun-actions">
      <button type="button" className="tun-button" disabled={unavailable} onClick={() => void decide('reject')} aria-describedby={`${id}-status`}>Reject action</button>
      <button type="button" className={`tun-button ${proposal.consequence === 'C4' ? 'tun-button-danger' : 'tun-button-primary'}`}
        disabled={unavailable} onClick={() => void decide('approve')} aria-describedby={`${id}-status`}>{approveLabel}</button>
    </div>
    <p className="tun-caption">Proposal {proposal.id} · version {proposal.version}. Application services must validate and record authorization.</p>
  </section>;
}
