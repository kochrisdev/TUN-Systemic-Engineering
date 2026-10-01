import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ApprovalGate } from '../vendor/tun-design/ApprovalGate';
import { ActionReceipt } from '../vendor/tun-design/ActionReceipt';
import { effectiveReceiptStatus, proposalBlockReason, type ActionProposal, type ReceiptData } from '../vendor/tun-design/contracts';

const proposal: ActionProposal = {
  id: 'proposal-fixture', version: '1', action: 'Withdraw publication', target: 'project-board',
  actor: { id: 'alice-fixture', name: 'alice-fixture', type: 'human' }, consequence: 'C3',
  effect: 'Withdraw one local publication at resource revision 2.', authority: 'Current withdrawal permission required.',
  recovery: { kind: 'compensatable', description: 'History remains; this is not undo or deletion.' },
  contentPreview: '<script>not executable</script>',
};
const receipt: ReceiptData = {
  id: 'operation-fixture:4', action: 'Withdraw publication', actor: proposal.actor, target: proposal.target,
  timestamp: '2026-10-01T00:00:00.000Z', status: 'completed', summary: 'The withdrawal operation was observed.',
  verification: { state: 'verified', detail: 'Local provider outcome only; original publication history remains.' },
  recovery: proposal.recovery,
};

describe('pinned design integration', () => {
  it('accepts the material review projection', () => expect(proposalBlockReason(proposal, Date.now())).toBeNull());
  it('renders complete review details and escapes plain content', () => {
    const html = renderToStaticMarkup(<ApprovalGate proposal={proposal} status="awaiting" approveLabel="Approve withdrawal" onDecision={() => {}} />);
    expect(html).toContain('resource revision 2');
    expect(html).toContain('&lt;script&gt;not executable&lt;/script&gt;');
    expect(html).toContain('Reject action');
    expect(html).toContain('Approve withdrawal');
  });
  it('does not render approved as confirmed execution', () => {
    const html = renderToStaticMarkup(<ApprovalGate proposal={proposal} status="approved" approveLabel="Approve withdrawal" onDecision={() => {}} />);
    expect(html).toContain('Execution is not confirmed');
    expect(html).toContain('disabled=""');
  });
  it('refuses an unverified successful-looking receipt', () => {
    const pending = { ...receipt, verification: { state: 'pending' as const, detail: '' } };
    expect(effectiveReceiptStatus(pending)).toBe('pending-verification');
    expect(renderToStaticMarkup(<ActionReceipt receipt={pending} />)).toContain('Pending verification');
  });
  it('shows a separate completed withdrawal, never a reversed original', () => {
    const html = renderToStaticMarkup(<ActionReceipt receipt={receipt} />);
    expect(html).toContain('Completed');
    expect(html).toContain('original publication history remains');
    expect(html).not.toContain('>Reversed<');
  });
  it('rejects unsafe evidence links', () => {
    const html = renderToStaticMarkup(<ActionReceipt receipt={{ ...receipt, detailsUrl: 'javascript:alert(1)' }} />);
    expect(html).toContain('link is unavailable');
    expect(html).not.toContain('href="javascript:');
  });
});
