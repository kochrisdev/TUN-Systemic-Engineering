/** Presentation metadata for review. None of these records grants authority. */
import type { ActionProposal } from './contracts.js';

export interface RevisionRef { readonly id: string; readonly version: string }
export interface ReviewBasis { readonly context: RevisionRef; readonly plan: RevisionRef }
export type ContextAvailability = 'available' | 'stale' | 'missing' | 'restricted';
export type ContextUsage = 'used' | 'not-used' | 'unknown';
export type ContextPersistence = 'task' | 'session' | 'persistent' | 'operational';
interface ContextSourceBase {
  readonly id: string;
  /** Supply only metadata the viewer is authorized to see. */
  readonly label: string;
  readonly kind: 'file' | 'note' | 'memory' | 'tool' | 'other';
  readonly scope: string;
  readonly persistence: ContextPersistence;
  readonly provenance: 'provided' | 'retrieved' | 'inferred';
}
export type ContextSource = ContextSourceBase & (
  | { readonly availability: 'available' | 'stale'; readonly usage: ContextUsage;
      readonly summary?: string; readonly detailsUrl?: string; readonly observedAt?: string }
  | { readonly availability: 'missing' | 'restricted'; readonly usage: 'not-used' }
);
export interface ContextSnapshot extends RevisionRef {
  readonly scope: string;
  readonly sources: readonly ContextSource[];
  readonly changeSummary?: string;
}
export type PlanStatus = 'proposed' | 'approved' | 'in-progress' | 'changed' | 'blocked' | 'completed';
export type PlanStepStatus = 'pending' | 'in-progress' | 'waiting-approval' | 'blocked' | 'completed' | 'skipped';
export interface PlanStep {
  readonly id: string;
  readonly title: string;
  readonly detail: string;
  readonly status: PlanStepStatus;
  readonly dependsOn?: readonly string[];
  readonly approvalRequired?: boolean;
  readonly owner?: string;
  /** Application evidence, not proof independently established by the UI. */
  readonly completionEvidence?: string;
}
export interface TaskPlan extends RevisionRef {
  readonly context: RevisionRef;
  readonly objective: string;
  readonly status: PlanStatus;
  readonly steps: readonly PlanStep[];
  readonly expectedOutputs: readonly string[];
  readonly changeSummary?: string;
  readonly blockers?: readonly string[];
  readonly completionEvidence?: string;
}
export type ProposalStatus = 'draft' | 'ready' | 'modified' | 'approved' | 'rejected' | 'expired' | 'superseded';
/** Requests navigation to review, never permission to execute. */
export interface ReviewRequest { readonly proposalId: string; readonly proposalVersion: string }
export const contextAvailabilityLabels: Record<ContextAvailability, string> = {
  available: 'Available', stale: 'Stale', missing: 'Missing', restricted: 'Restricted',
};
export const contextUsageLabels: Record<ContextUsage, string> = {
  used: 'Used for this task', 'not-used': 'Not used', unknown: 'Usage not confirmed',
};
export const contextPersistenceLabels: Record<ContextPersistence, string> = {
  task: 'Task-only context', session: 'Session context', persistent: 'Persistent context', operational: 'Operational context',
};
export const planStatusLabels: Record<PlanStatus, string> = {
  proposed: 'Proposed approach', approved: 'Approach reviewed — not action authorization',
  'in-progress': 'In progress', changed: 'Plan changed — review again', blocked: 'Blocked', completed: 'Completed',
};
export const planStepLabels: Record<PlanStepStatus, string> = {
  pending: 'Pending', 'in-progress': 'In progress', 'waiting-approval': 'Waiting for action approval',
  blocked: 'Blocked', completed: 'Completed', skipped: 'Skipped',
};
export const proposalStatusLabels: Record<ProposalStatus, string> = {
  draft: 'Draft', ready: 'Ready for review', modified: 'Modified — review again',
  approved: 'Approved — execution not confirmed here', rejected: 'Rejected',
  expired: 'Expired', superseded: 'Superseded',
};
export function contextState(context: ContextSnapshot): string {
  const sources = context.sources;
  if (!sources.length) return 'No context';
  if (sources.every(s => s.availability === 'restricted')) return 'Restricted context';
  if (sources.every(s => s.availability === 'missing')) return 'Missing context';
  if (sources.some(s => s.availability !== 'available')) return 'Partial context';
  return 'Active context';
}
/** Fingerprint material plan content, not ordinary progress/evidence updates. */
export function planFingerprint(plan: TaskPlan): string {
  return JSON.stringify([plan.id, plan.version, plan.context.id, plan.context.version, plan.objective,
    plan.expectedOutputs, plan.steps.map(s => [s.id, s.title, s.detail, s.dependsOn ?? [], s.approvalRequired ?? false, s.owner ?? null])]);
}
/** Bounded metadata checks for typed plans; not a general untrusted-JSON validator. */
export function planIssues(plan: TaskPlan): string[] {
  const issues: string[] = [];
  const hasText = (s: string) => typeof s === 'string' && Boolean(s.trim());
  if (![plan.id, plan.version, plan.context.id, plan.context.version, plan.objective].every(hasText)) issues.push('Plan identity, context revision, and objective are required.');
  if (!plan.expectedOutputs.length || !plan.expectedOutputs.every(hasText)) issues.push('Expected outputs must be described.');
  if (!plan.steps.length) issues.push('No plan steps supplied.');
  if (!Object.hasOwn(planStatusLabels, plan.status)) issues.push('Plan status is invalid.');
  if (plan.status === 'changed' && !plan.changeSummary?.trim()) issues.push('A changed plan needs a change summary.');
  const ids = new Set(plan.steps.map(s => s.id));
  if (ids.size !== plan.steps.length) issues.push('Plan step identifiers must be unique.');
  for (const step of plan.steps) {
    if (![step.id, step.title, step.detail].every(hasText)) issues.push('Every step needs an identifier, title, and description.');
    if (!Object.hasOwn(planStepLabels, step.status)) issues.push('Step status is invalid.');
    if (step.dependsOn?.some(id => !ids.has(id))) issues.push('A dependency refers to an unknown step.');
  }
  // Topological elimination also detects self-dependencies, without recursive traversal.
  const remaining = new Map(plan.steps.map(s => [s.id, new Set(s.dependsOn ?? [])]));
  let advanced = true;
  while (advanced && remaining.size) {
    advanced = false;
    for (const [id, dependencies] of remaining) {
      if (!dependencies.size) {
        remaining.delete(id);
        for (const pending of remaining.values()) pending.delete(id);
        advanced = true;
      }
    }
  }
  if (remaining.size && !issues.includes('A dependency refers to an unknown step.')) issues.push('Plan dependencies contain a cycle.');
  return [...new Set(issues)];
}
export function effectivePlanStepStatus(step: PlanStep): PlanStepStatus | 'unverified' {
  return step.status === 'completed' && !step.completionEvidence?.trim() ? 'unverified' : step.status;
}
export function effectivePlanStatus(plan: TaskPlan): PlanStatus | 'unverified' {
  if (planIssues(plan).length) return 'blocked';
  return plan.status === 'completed' && (!plan.completionEvidence?.trim() ||
    plan.steps.some(s => !['completed', 'skipped'].includes(effectivePlanStepStatus(s)))) ? 'unverified' : plan.status;
}
/** Host convenience check. Authenticity, immutable revisions, and policy are server responsibilities. */
export function reviewBasisMatches(proposal: ActionProposal, context: ContextSnapshot, plan: TaskPlan): boolean {
  const basis = proposal.reviewBasis;
  return Boolean(basis && basis.context.id === context.id && basis.context.version === context.version &&
    basis.plan.id === plan.id && basis.plan.version === plan.version &&
    plan.context.id === context.id && plan.context.version === context.version);
}
