/** TUN presentation contracts. These are not an authorization boundary. */
import type { ReviewBasis } from './review-contracts.js';
export type Consequence = 'C0' | 'C1' | 'C2' | 'C3' | 'C4';
export type AutonomyLevel = 0 | 1 | 2 | 3 | 4;
export type AgentState = 'idle' | 'listening' | 'thinking' | 'planning' | 'waiting' | 'acting' | 'verifying' | 'blocked' | 'completed' | 'failed' | 'escalated';
export type ApprovalStatus = 'awaiting' | 'approved' | 'rejected' | 'expired' | 'superseded';
export type ReceiptStatus = 'completed' | 'partially-completed' | 'failed' | 'reversed' | 'pending-verification';
export interface Actor { readonly id: string; readonly name: string; readonly type: 'human' | 'agent' | 'system' }
export interface Recovery {
  readonly kind: 'reversible' | 'compensatable' | 'irreversible' | 'unknown';
  readonly description: string;
}
export interface ActionProposal {
  readonly id: string;
  readonly version: string;
  readonly action: string;
  readonly target: string;
  readonly actor: Actor;
  readonly consequence: Consequence;
  readonly effect: string;
  readonly authority: string;
  readonly recovery: Recovery;
  /** Explicit timezone; seconds required; at most millisecond precision. */
  readonly expiresAt?: string;
  /** Optional immutable references. The host must validate their actual contents. */
  readonly reviewBasis?: ReviewBasis;
  /** Reviewable plain text; never rendered as HTML or treated as authority. */
  readonly contentPreview?: string;
}
export interface DecisionRequest {
  readonly proposalId: string;
  readonly proposalVersion: string;
  readonly decision: 'approve' | 'reject';
}
export interface AgentProfile {
  readonly id: string;
  readonly name: string;
  readonly purpose: string;
  readonly autonomy: AutonomyLevel;
  readonly authority: readonly string[];
  readonly capabilities?: readonly string[];
}
export interface ReceiptData {
  readonly id: string;
  readonly action: string;
  readonly actor: Actor;
  readonly target: string;
  readonly timestamp: string;
  readonly status: ReceiptStatus;
  readonly summary: string;
  readonly verification: { readonly state: 'verified' | 'pending' | 'unavailable'; readonly detail: string };
  readonly recovery: Recovery;
  readonly detailsUrl?: string;
}
export const agentLabels: Record<AgentState, string> = {
  idle: 'Idle', listening: 'Listening', thinking: 'Analyzing', planning: 'Planning',
  waiting: 'Waiting for approval', acting: 'Acting', verifying: 'Verifying',
  blocked: 'Blocked', completed: 'Completed', failed: 'Failed', escalated: 'Escalated',
};
export const autonomyLabels: Record<AutonomyLevel, string> = {
  0: 'Human only', 1: 'AI assists', 2: 'AI proposes', 3: 'AI acts', 4: 'AI operates',
};
export const consequenceLabels: Record<Consequence, string> = {
  C0: 'Informational', C1: 'Local reversible', C2: 'Shared reversible',
  C3: 'External consequential', C4: 'High consequence',
};
export const recoveryLabels: Record<Recovery['kind'], string> = {
  reversible: 'Reversible', compensatable: 'Compensation only',
  irreversible: 'Cannot be undone', unknown: 'Recovery not confirmed',
};
export const receiptLabels: Record<ReceiptStatus, string> = {
  completed: 'Completed', 'partially-completed': 'Partially completed', failed: 'Failed',
  reversed: 'Reversed', 'pending-verification': 'Pending verification',
};
/** A change to material presentation data invalidates the displayed decision. */
export function proposalFingerprint(p: ActionProposal): string {
  return JSON.stringify([p.id, p.version, p.action, p.target, p.actor.id, p.actor.name,
    p.actor.type, p.consequence, p.effect, p.authority, p.recovery.kind,
    p.recovery.description, p.expiresAt ?? null, p.contentPreview ?? null,
    p.reviewBasis ? [p.reviewBasis.context.id, p.reviewBasis.context.version,
      p.reviewBasis.plan.id, p.reviewBasis.plan.version] : null]);
}
/** Strict calendar validation prevents Date.parse from rolling February 30 into March. */
export function parseTimestamp(value: string): number | null {
  if (typeof value !== 'string') return null;
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?(Z|([+-])(\d{2}):(\d{2}))$/.exec(value);
  if (!match) return null;
  const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
  const hour = Number(match[4]), minute = Number(match[5]), second = Number(match[6]);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const monthDays = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (year < 1 || month < 1 || month > 12 || day < 1 || day > monthDays[month - 1]! ||
      hour > 23 || minute > 59 || second > 59) return null;
  // TUN's supported subset excludes the unknown-local-offset form -00:00.
  if (match[8] === '-00:00' || (match[8] !== 'Z' &&
      (Number(match[10]) > 23 || Number(match[11]) > 59))) return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}
export function proposalBlockReason(p: ActionProposal, now: number): string | null {
  if (!Number.isFinite(now)) return 'The approval clock is unavailable. Request a fresh proposal.';
  if (![p.id, p.version, p.action, p.target, p.actor.id, p.actor.name, p.effect,
    p.authority, p.recovery.description].every(s => typeof s === 'string' && s.trim())) {
    return 'Proposal details are incomplete. Request a fresh proposal.';
  }
  if (!Object.hasOwn(consequenceLabels, p.consequence) ||
      !Object.hasOwn(recoveryLabels, p.recovery.kind) ||
      !['human', 'agent', 'system'].includes(p.actor.type)) {
    return 'Proposal classification is invalid. Request a fresh proposal.';
  }
  if (p.contentPreview !== undefined && (typeof p.contentPreview !== 'string' || !p.contentPreview.trim())) {
    return 'The content preview is incomplete. Request a fresh proposal.';
  }
  if (p.reviewBasis && ![p.reviewBasis.context?.id, p.reviewBasis.context?.version,
      p.reviewBasis.plan?.id, p.reviewBasis.plan?.version].every(s => typeof s === 'string' && s.trim())) {
    return 'The review basis is incomplete. Request a fresh proposal.';
  }
  if (p.expiresAt !== undefined) {
    const expires = parseTimestamp(p.expiresAt);
    if (expires === null) return 'The approval expiry is invalid. Request a fresh proposal.';
    if (now >= expires) return 'This proposal has expired. Request a fresh proposal.';
  }
  return null;
}
/** Successful-looking receipts require explicit verification from the host. */
export function effectiveReceiptStatus(receipt: ReceiptData): ReceiptStatus {
  if ((receipt.status === 'completed' || receipt.status === 'reversed') &&
      (receipt.verification.state !== 'verified' || !receipt.verification.detail.trim())) {
    return 'pending-verification';
  }
  return receipt.status;
}
/** No javascript:, data:, protocol-relative, or backslash-based links. */
export function safeDetailsUrl(value: string | undefined): string | undefined {
  if (!value || value !== value.trim() || /[\x00-\x20\\]/.test(value)) return undefined;
  if (value.startsWith('/') && !value.startsWith('//')) return value;
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password
      ? url.href : undefined;
  } catch { return undefined; }
}
export function displayTimestamp(value: string): string {
  const time = parseTimestamp(value);
  return time === null ? 'Time unavailable' : new Date(time).toISOString().replace('T', ' ').replace('.000Z', ' UTC').replace('Z', ' UTC');
}
export * from './review-contracts.js';
